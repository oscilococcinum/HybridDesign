# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard
from typing import Callable
from collections.abc import ItemsView
from utils.FreeCADInterfaces import ShapeLike
from utils.FaceDef import FaceDef
from utils.EdgeDef import EdgeDef


class LazyFaceDict:
    def __init__(self, faces: list[ShapeLike]):
        self._faces = faces
        self._cache: dict[int, FaceDef] = {}

    def __getitem__(self, hash_code: int) -> FaceDef:
        if hash_code in self._cache:
            return self._cache[hash_code]
        else:
            for i in range(len(self._cache), len(self._faces)):
                f = self._faces[i]
                hsh = f.hashCode()
                self._cache[hsh] = FaceDef(hsh, f, f"Face{i+1}")
                if hsh == hash_code:
                    return self._cache[hash_code]

            raise KeyError

class LazyEdgeDict:
    def __init__(self, edges: list[ShapeLike]):
        self._edges = edges
        self._cache: dict[int, EdgeDef] = {}

    def __getitem__(self, hash_code: int) -> EdgeDef:
        if hash_code in self._cache:
            return self._cache[hash_code]
        else:
            for i in range(len(self._cache), len(self._edges)):
                f = self._edges[i]
                hsh = f.hashCode()
                self._cache[hsh] = EdgeDef(hsh, f, f"Edge{i+1}")
                if hsh == hash_code:
                    return self._cache[hash_code]

            raise KeyError
