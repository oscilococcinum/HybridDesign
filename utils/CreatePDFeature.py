# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
import FreeCADGui as Gui #type: ignore
import FreeCAD as App #type: ignore
from utils.FreeCADInterfaces import FeatureProxyLike, FeatureLike, BodyLike, VPLike


def createPDFeature(featureClass: type[FeatureProxyLike], vpClass: type[VPLike], selectionReq: bool = True):
    if not (doc := App.ActiveDocument): raise RuntimeError("No Active document")
    if not (guiDoc := Gui.ActiveDocument): raise RuntimeError("No Active document")
    if not (activeView := guiDoc.ActiveView): raise RuntimeError(f"No Active View, {type(activeView)}")
    if selectionReq and not (sel := Gui.Selection.getSelection()): raise RuntimeError(f"No input feature selected")
    body: BodyLike
    if not (body := activeView.getActiveObject("pdbody")): raise RuntimeError(f"No active body, activate some PD Body and try again")
    doc.openTransaction(f"Create {featureClass.getFeatureName()}")
    feature: FeatureLike = doc.addObject("PartDesign::FeaturePython", featureClass.getFeatureName())
    featureClass(feature)
    vpClass(feature.ViewObject)
    body.addObject(feature)
    body.Tip = feature
    doc.recompute()
    doc.commitTransaction()
    return feature