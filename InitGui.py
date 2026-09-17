# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard, reportUnusedImport=error, reportMissingImports=information
import FreeCADGui as Gui
import os


class PDExtended(Gui.Workbench):
    MenuText = "HybridDesign"
    ToolTip = "HybridDesign Workbench"
    Icon = os.path.join(
            ".",
            "Assets",
            "HybridDesignWorkbench.svg"
        )

    def Initialize(self):

        import PartDesignGui #type: ignore
        from AutoFillet.Command import Command as AutoFilletCommand
        from Extrusion.Command import Command as ExtrudeCommand
        from Defeature.Command import Command as DefeatureCommand
        from Extract.Command import Command as ExtractCommand
        from OffsetSurface.Command import Command as OffsetSurfaceCommand
        from Boundary.Command import Command as BoundaryCommand
        from CutSolid.Command import Command as CutSolidCommand
        from ThickenSurface.Command import Command as ThickenSurfaceCommand
        from TangentSelection.Command import Command as TangencySelectionCommand
        from EnclosedSelection.Command import Command as EnclosedSelectionCommand
        from IsolateShape.Command import Command as IsolateShapeCommand
        from CurvedHelix.Command import Command as CurvedHelixCommand
        #from PararellCurve.Command import Command as PararellCurveCommand
        from ShapeFillet.Command import Command as ShapeFilletCommand
        from SplitSurface.Command import Command as SplitSurfaceCommand
        from Extrapolate.Command import Command as ExtrapolateCommand
        from Join.Command import Command as JoinCommand

        features: dict[str, list[str]] = {
            "Solid": ["PartDesign_Body",
                      "PartDesign_NewSketch",
                      "PartDesign_SubShapeBinder",
                      "PartDesign_Pad",
                      "PartDesign_Revolution",
                      "PartDesign_AdditiveLoft",
                      "PartDesign_AdditivePipe",
                      "PartDesign_AdditiveHelix",
                      "PartDesign_Pocket",
                      "PartDesign_Hole",
                      "PartDesign_Groove",
                      "PartDesign_SubtractiveLoft",
                      "PartDesign_SubtractivePipe",
                      "PartDesign_SubtractiveHelix",
                      "PartDesign_Fillet",
                      AutoFilletCommand.getCommandName(),
                      "PartDesign_Chamfer",
                      "PartDesign_Draft",
                      "PartDesign_Thickness",
                      "PartDesign_Mirrored",
                      "PartDesign_LinearPattern",
                      "PartDesign_PolarPattern",
                      "PartDesign_MultiTransform",
                      DefeatureCommand.getCommandName(),
                      CutSolidCommand.getCommandName(),
                      ThickenSurfaceCommand.getCommandName()],
            "Surface": [ExtrudeCommand.getCommandName(),
                        ExtractCommand.getCommandName(),
                        OffsetSurfaceCommand.getCommandName(),
                        BoundaryCommand.getCommandName(),
                        ShapeFilletCommand.getCommandName(),
                        SplitSurfaceCommand.getCommandName(),
                        ExtrapolateCommand.getCommandName(),
                        JoinCommand.getCommandName(),],
            "Wireframe": [CurvedHelixCommand.getCommandName(),],
                          #PararellCurveCommand.getCommandName()],
            "Selection": [TangencySelectionCommand.getCommandName(),
                          EnclosedSelectionCommand.getCommandName()],
            "Other": [IsolateShapeCommand.getCommandName()]}

        for k, v in features.items():
                self.appendToolbar(k, v)
                self.appendMenu(k, v)

Gui.addWorkbench(PDExtended())
