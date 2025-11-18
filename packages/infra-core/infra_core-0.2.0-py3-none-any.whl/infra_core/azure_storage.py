"""Removed legacy module `infra_core.azure_storage`.

The public Azure storage helpers now live at :mod:`infra_core.azure.storage`. Importers
must update to the new location instead of relying on this shim.
"""

from __future__ import annotations

raise ImportError(
    "infra_core.azure_storage has been removed; import from infra_core.azure.storage instead.",
)
