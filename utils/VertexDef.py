# SPDX-License-Identifier: LGPL-2.1-or-later
from Part import Face #type: ignore
from dataclasses import dataclass


@dataclass
class VertexDef:
    id: int
    topoFace: Face
    name: str | None = None
