# SPDX-License-Identifier: LGPL-2.1-or-later
# pyright: standard, reportUnusedImport=error, reportMissingImports=information
import os

import FreeCADGui as Gui


class HybridDesign(Gui.Workbench):
    MenuText = "HybridDesign"
    ToolTip = "HybridDesign Workbench"
    Icon = os.path.join(".", "Resources", "Icons", "HybridDesignWorkbench.svg")

    def Initialize(self):

        import PartDesignGui  # type: ignore

        from .AutoFillet.Command import Command as AutoFilletCommand
        from .Boundary.Command import Command as BoundaryCommand
        from .CurvedHelix.Command import Command as CurvedHelixCommand
        from .CutSolid.Command import Command as CutSolidCommand
        from .Defeature.Command import Command as DefeatureCommand
        from .EnclosedSelection.Command import Command as EnclosedSelectionCommand
        from .Extract.Command import Command as ExtractCommand
        from .Extrapolate.Command import Command as ExtrapolateCommand
        from .Extrusion.Command import Command as ExtrudeCommand
        from .Intersection.Command import Command as IntersectionCommand
        from .IsolateShape.Command import Command as IsolateShapeCommand
        from .Join.Command import Command as JoinCommand
        from .Line.Command import Command as LineCommand
        from .OffsetSurface.Command import Command as OffsetSurfaceCommand
        from .Point.Command import Command as PointCommand
        from .ReloadWB.Command import Command as ReloadWBCommand
        from .ShapeFillet.Command import Command as ShapeFilletCommand
        from .SplitSurface.Command import Command as SplitSurfaceCommand
        from .TangentSelection.Command import Command as TangencySelectionCommand
        from .ThickenSurface.Command import Command as ThickenSurfaceCommand

        features: dict[str, list[str]] = {
            "Solid": [
                "PartDesign_Body",
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
                ThickenSurfaceCommand.getCommandName(),
            ],
            "Surface": [
                ExtrudeCommand.getCommandName(),
                ExtractCommand.getCommandName(),
                OffsetSurfaceCommand.getCommandName(),
                ShapeFilletCommand.getCommandName(),
                SplitSurfaceCommand.getCommandName(),
                ExtrapolateCommand.getCommandName(),
                JoinCommand.getCommandName(),
            ],
            "Wireframe": [
                PointCommand.getCommandName(),
                LineCommand.getCommandName(),
                IntersectionCommand.getCommandName(),
                CurvedHelixCommand.getCommandName(),
                BoundaryCommand.getCommandName(),
            ],
            "Selection": [
                TangencySelectionCommand.getCommandName(),
                EnclosedSelectionCommand.getCommandName(),
            ],
            "Other": [
                IsolateShapeCommand.getCommandName(),
                ReloadWBCommand.getCommandName(),
            ],
        }

        for k, v in features.items():
            self.appendToolbar(k, v)
            self.appendMenu(k, v)


Gui.addWorkbench(HybridDesign())
