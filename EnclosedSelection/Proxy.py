# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard
import FreeCADGui as Gui #type: ignore
from utils.FreeCADInterfaces import ShapeLike
from utils.FaceWalker import FaceWalker
from utils.utils import getReferencedShapes, getSelectionEx

FEATURE_NAME = "EnclosedSelection"


def proxyCommand() -> None:
    sel = getSelectionEx()
    currentShape: ShapeLike = sel[0][0].Shape
    facesToJoin: list[ShapeLike] = getReferencedShapes(sel)
    tgTrack = FaceWalker(currentShape)
    enclosure = [f.hashCode() for f in facesToJoin[1:]]
    tgHashFaces: list[int] = tgTrack.walkEnclose(facesToJoin[0].hashCode(), enclosure)
    Gui.Selection.clearSelection()
    Gui.Selection.addSelection(sel[0][0], [tgTrack.HashToFace[f].name for f in tgHashFaces])
    [Gui.Selection.removeSelection(sel[0][0], x) for x in [tgTrack.HashToFace[f].name for f in enclosure]]
