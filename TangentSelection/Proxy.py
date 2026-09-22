# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
import FreeCADGui as Gui #type: ignore
from utils.FreeCADInterfaces import ShapeLike
from utils.Walker import FaceWalker
from utils.utils import getReferencedShapes, getSelectionEx

FEATURE_NAME = "TangentSelection"


def proxyCommand() -> None:
    sel = getSelectionEx()
    currentShape: ShapeLike = sel[0][0].Shape
    facesToJoin: list[ShapeLike] = getReferencedShapes(sel)
    tgTrack = FaceWalker(currentShape)
    tgHashFaces: list[int] = tgTrack.walkTangent(facesToJoin[0].hashCode())
    Gui.Selection.addSelection(sel[0][0], [tgTrack.HashToFace[f].name for f in tgHashFaces])
