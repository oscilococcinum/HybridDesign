# SPDX-License-Identifier: LGPL-2.1-or-later
# pyright: standard, reportUnusedImport=error, reportMissingImports=information
import FreeCADGui as Gui

import FreeCAD as App

from .FreeCADInterfaces import FeatureLike, FeatureProxyLike, VPLike


def createSurfaceFeature(
    featureClass: type[FeatureProxyLike],
    vpClass: type[VPLike],
    selectionReq: bool = True,
):
    if not (doc := App.ActiveDocument):
        raise RuntimeError("No Active document")
    if not (guiDoc := Gui.ActiveDocument):
        raise RuntimeError("No Active document")
    if not (activeView := guiDoc.ActiveView):
        raise RuntimeError(f"No Active View, {type(activeView)}")
    if selectionReq and not (sel := Gui.Selection.getSelection()):
        raise RuntimeError(f"No input feature selected")
    doc.openTransaction(f"Create {featureClass.getFeatureName()}")
    feature: FeatureLike = doc.addObject(
        "Part::FeaturePython", featureClass.getFeatureName()
    )
    featureClass(feature)
    vpClass(feature.ViewObject)
    doc.recompute()
    doc.commitTransaction()
    return feature
