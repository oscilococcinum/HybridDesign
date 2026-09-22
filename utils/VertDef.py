# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
from dataclasses import dataclass, field
from .FreeCADInterfaces import ShapeLike


@dataclass
class VertDef:
    id: int 
    Vert: ShapeLike
    name: str | None = None
    parentEdges: list[int] = field(default_factory=list)