# SPDX-License-Identifier: LGPL-2.1-or-later
# pyright: standard, reportUnusedImport=error, reportMissingImports=information
from dataclasses import dataclass

from Part import Face


@dataclass
class VertexDef:
    id: int
    topoFace: Face
    name: str | None = None
