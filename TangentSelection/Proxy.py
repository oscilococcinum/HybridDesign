# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
import FreeCADGui as Gui
from utils.FreeCADInterfaces import ShapeLike
from utils.Walker import FaceWalker, EdgeWalker
from utils.utils import getReferencedShapes, getSelectionEx

FEATURE_NAME = "TangentSelection"


def proxyCommand() -> None:
    sel = getSelectionEx()
    match sel[0][1][0][:4]:
        case "Face":
            currentShape: ShapeLike = sel[0][0].Shape
            facesToJoin: list[ShapeLike] = getReferencedShapes(sel)
            tgTrack = FaceWalker(currentShape)
            tgHashFaces: list[int] = tgTrack.walkTangent(facesToJoin[-1].hashCode(), 1e-2)
            Gui.Selection.addSelection(sel[0][0], [tgTrack.HashToFace[f].name for f in tgHashFaces])
        case "Edge":
            currentShape: ShapeLike = sel[0][0].Shape
            edgesToJoin: list[ShapeLike] = getReferencedShapes(sel)
            tgTrack = EdgeWalker(currentShape)
            tgHashEdges: list[int] = tgTrack.walkTangent(edgesToJoin[-1].hashCode(), 1e-2)
            Gui.Selection.addSelection(sel[0][0], [tgTrack.HashToEdge[f].name for f in tgHashEdges])
        case _:
            raise RuntimeError("Select face or edge!")
