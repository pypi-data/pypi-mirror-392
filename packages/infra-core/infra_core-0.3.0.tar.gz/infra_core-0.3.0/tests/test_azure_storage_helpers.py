from __future__ import annotations

import asyncio
import errno
from collections.abc import Iterable
from pathlib import Path
from types import SimpleNamespace

import pytest

from infra_core.azure.storage import (
    _DEFAULT_SETTINGS_KEY,
    AzureStorageClient,
    AzureStorageSettings,
    ResourceNotFoundError,
    _atomic_replace,
    _AzureStorageConfig,
    _blob_name_for_path,
    _dispose_client,
    _iter_downloader_chunks,
    _resolve_settings,
    _schedule_async_disposal,
    _settings_cache_key,
    _stream_blob_to_path,
    _upload_file_sync,
    _upload_text_sync,
)


def test_blob_name_trims_slashes() -> None:
    assert _blob_name_for_path(Path("/foo/bar")) == "foo/bar"
    assert _blob_name_for_path(Path("/")) == ""
    assert _blob_name_for_path(Path("data"), prefix="prefix/") == "prefix/data"


def test_upload_helpers_record_calls(tmp_path: Path) -> None:
    class DummyContainer:
        def __init__(self) -> None:
            self.uploads: list[tuple[str, bytes]] = []

        def upload_blob(self, *, name: str, data: bytes, overwrite: bool = False) -> None:
            content = data.read() if hasattr(data, "read") else data
            self.uploads.append((name, content))

    container = DummyContainer()
    _upload_text_sync(container, "foo", b"bar")

    tmp_file = tmp_path / "tmp.bin"
    tmp_file.write_bytes(b"stream")
    _upload_file_sync(container, "blob-name", tmp_file)

    assert container.uploads == [("foo", b"bar"), ("blob-name", b"stream")]


def test_iter_downloader_chunks_supports_iterables() -> None:
    class ChunkDownloader:
        def chunks(self) -> Iterable[bytes]:
            return [b"a", b"", b"bc"]

    chunks = list(_iter_downloader_chunks(ChunkDownloader()))
    assert chunks == [b"a", b"", b"bc"]


def test_iter_downloader_chunks_supports_readall() -> None:
    class ReadAllDownloader:
        def readall(self) -> bytes:
            return b"value"

    assert list(_iter_downloader_chunks(ReadAllDownloader())) == [b"value"]


def test_iter_downloader_chunks_unsupported() -> None:
    class EmptyDownloader:
        pass

    with pytest.raises(RuntimeError):
        list(_iter_downloader_chunks(EmptyDownloader()))


def test_stream_blob_to_path_writes_chunks(tmp_path: Path) -> None:
    class ChunkDownloader:
        def chunks(self) -> Iterable[bytes]:
            return [b"hello", b"", b"world"]

    destination = tmp_path / "blob.txt"
    _stream_blob_to_path(ChunkDownloader(), destination)
    assert destination.read_bytes() == b"helloworld"


def test_atomic_replace_uses_move_on_exdev(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = tmp_path / "source.txt"
    destination = tmp_path / "dest.txt"
    source.write_text("data")
    destination.write_text("old")

    def fake_replace(self: Path, target: Path) -> None:  # pragma: no cover - raises special case
        raise OSError(errno.EXDEV, "cross-device")

    def fake_move(src: str, dest: str) -> None:
        Path(dest).write_text(Path(src).read_text())

    monkeypatch.setattr(Path, "replace", fake_replace)
    monkeypatch.setattr("shutil.move", fake_move)
    _atomic_replace(source, destination)

    assert destination.read_text() == "data"


def test_settings_resolve_and_cache_key(monkeypatch: pytest.MonkeyPatch) -> None:
    settings = AzureStorageSettings(container="c", prefix="p")
    assert _settings_cache_key(settings) == (
        "c",
        None,
        None,
        None,
        "p",
    )

    resolved = []

    def fake_from_env() -> AzureStorageSettings:
        resolved.append(True)
        return settings

    monkeypatch.setattr("infra_core.azure.storage.AzureStorageSettings.from_env", fake_from_env)
    key, returned = _resolve_settings(None)
    assert key is _DEFAULT_SETTINGS_KEY
    assert returned is settings

    key2, returned2 = _resolve_settings(settings)
    assert key2 == _settings_cache_key(settings)
    assert returned2 is settings


def test_dispose_triggers_schedule(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[SimpleNamespace] = []

    class Stub:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

        async def aclose(self) -> None:
            calls.append(SimpleNamespace(name="async"))

    stub = Stub()
    scheduled: list[SimpleNamespace] = []
    monkeypatch.setattr(
        "infra_core.azure.storage._schedule_async_disposal",
        lambda client: scheduled.append(client),
    )
    _dispose_client(stub)
    assert stub.closed
    assert scheduled == [stub]


def test_schedule_async_disposal_without_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    called: list[str] = []

    class Stub:
        async def aclose(self) -> None:
            called.append("aclose")

    def fake_get_loop() -> None:
        raise RuntimeError("no loop")

    def fake_run(coro: object) -> None:
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(coro)  # type: ignore[arg-type]
        finally:
            loop.close()

    monkeypatch.setattr(asyncio, "get_running_loop", fake_get_loop)
    monkeypatch.setattr(asyncio, "run", fake_run)

    _schedule_async_disposal(Stub())
    assert called == ["aclose"]


def test_async_service_client_connection_string(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = _AzureStorageConfig(container="cont", connection_string="conn")
    created: list[str] = []

    class FakeCli:
        pass

    def fake_from_connection_string(connection: str) -> FakeCli:
        created.append(connection)
        return FakeCli()

    monkeypatch.setattr(
        "infra_core.azure.storage.AsyncBlobServiceClient.from_connection_string",
        fake_from_connection_string,
    )
    client, credential = config.create_async_service_client()
    assert isinstance(client, FakeCli)
    assert credential is None
    assert created == ["conn"]


def test_async_service_client_account_url(monkeypatch: pytest.MonkeyPatch) -> None:
    config = _AzureStorageConfig(
        container="cont",
        connection_string=None,
        account_name="account",
        blob_endpoint=None,
    )
    credentials: list[str] = []

    class FakeCred:
        pass

    class FakeCli:
        def __init__(self, account_url: str, credential: FakeCred) -> None:
            credentials.append(account_url)

    monkeypatch.setattr("infra_core.azure.storage.AsyncDefaultAzureCredential", lambda: FakeCred())
    monkeypatch.setattr(
        "infra_core.azure.storage.AsyncBlobServiceClient",
        FakeCli,
    )
    client, credential = config.create_async_service_client()
    assert isinstance(client, FakeCli)
    assert isinstance(credential, FakeCred)
    assert credentials == ["https://account.blob.core.windows.net"]


def test_async_service_client_missing_account_raises() -> None:
    config = _AzureStorageConfig(container="cont")
    with pytest.raises(RuntimeError):
        config.create_async_service_client()


def test_current_prefix_prefers_config() -> None:
    config = SimpleNamespace(container="cont", prefix="cfg")
    settings = AzureStorageSettings(container="cont", prefix="prefs")
    client = AzureStorageClient(config=config, settings=settings, enabled=True, swallow_errors=True)
    name = client.blob_name_for_path(Path("thing"))
    assert name == "cfg/thing"


def test_log_unconfigured_debug(monkeypatch: pytest.MonkeyPatch) -> None:
    client = AzureStorageClient(config=None, settings=AzureStorageSettings(container=None), enabled=True)
    records: list[tuple[str, str]] = []

    class FakeLogger:
        def debug(self, message: str, *, extra: dict[str, str]) -> None:
            records.append((message, extra["action"]))

    client._logger = FakeLogger()
    client._log_unconfigured("test")
    assert records == [
        ("Azure storage not configured; skipping action", "test"),
    ]


def test_download_to_path_false_without_container(tmp_path: Path) -> None:
    client = AzureStorageClient(config=None, enabled=True)
    assert client.download_to_path(tmp_path / "missing") is False


def test_download_tree_and_list_populate_files(tmp_path: Path) -> None:
    class DummyDownloader:
        def chunks(self) -> Iterable[bytes]:
            return [b"data"]

    class DummyContainer:
        def download_blob(self, name: str) -> DummyDownloader:
            return DummyDownloader()

        def list_blobs(self, *, name_starts_with: str):
            return [
                SimpleNamespace(name=f"{name_starts_with}file.txt", size=5),
                SimpleNamespace(name=f"{name_starts_with}folder/", size=0),
            ]

        def upload_blob(self, **kwargs: object) -> None:
            pass

        def create_container(self) -> None:
            pass

    class DummyConfig:
        container = "container"
        prefix = None

        def create_container_client(self):
            return DummyContainer(), SimpleNamespace(), None

        def create_async_service_client(self):
            return SimpleNamespace(get_container_client=lambda container: DummyContainer()), None

    settings = AzureStorageSettings(container="container")
    client = AzureStorageClient(config=DummyConfig(), settings=settings, enabled=True)
    target = tmp_path / "tree"
    assert client.download_to_path(target)
    assert (tmp_path / "tree").exists()
    root = tmp_path / "tree-root"
    client.download_to_path = lambda *_: False
    assert client.download_tree(root)
    tree = client.list_tree(root)
    assert tree == [("file.txt", 5)]


def test_download_to_path_handles_not_found(tmp_path: Path) -> None:
    class BrokenContainer:
        def download_blob(self, name: str) -> None:
            raise ResourceNotFoundError("missing")

        def create_container(self) -> None:
            pass

        def upload_blob(self, **kwargs: object) -> None:
            pass

    class BrokenConfig:
        container = "container"
        prefix = None

        def create_container_client(self):
            return BrokenContainer(), SimpleNamespace(), None

        def create_async_service_client(self):
            return SimpleNamespace(get_container_client=lambda container: BrokenContainer()), None

    client = AzureStorageClient(config=BrokenConfig(), enabled=True)
    assert client.download_to_path(tmp_path / "notfound") is False
