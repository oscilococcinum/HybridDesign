# SPDX-License-Identifier: LGPL-2.1-or-later
# pyright: standard, reportUnusedImport=error, reportMissingImports=information

import FreeCADGui as Gui

FEATURE_NAME = "ReloadWB"


def proxyCommand() -> None:
    import importlib
    import sys

    mods = [
        m
        for m in sys.modules
        if m.startswith("freecad.HybridDesign.") and not m.endswith("init_gui")
    ]

    Gui.removeWorkbench("HybridDesign")

    for m in sorted(mods, reverse=True):
        importlib.reload(sys.modules[m])

    import freecad.HybridDesign.init_gui as hd

    importlib.reload(hd)
    Gui.removeWorkbench("HybridDesign")
    Gui.addWorkbench(hd.HybridDesign())
    Gui.activateWorkbench("HybridDesign")
