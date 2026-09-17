# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
from dataclasses import dataclass
from functools import cached_property
from .FreeCADInterfaces import GeomSurface
from .FreeCADInterfaces import ShapeLike


@dataclass
class FaceDef:
    id: int 
    topoFace: ShapeLike
    name: str | None = None

    @cached_property
    def Surface(self) -> GeomSurface:
        return self.topoFace.Surface


