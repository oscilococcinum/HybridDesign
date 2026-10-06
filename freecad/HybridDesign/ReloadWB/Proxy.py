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
        if m == "freecad.HybridDesign" or m.startswith("freecad.HybridDesign.")
    ]

    Gui.removeWorkbench("HybridDesign")
    for m in sorted(mods, reverse=True):
        # print("Reloading", m)
        importlib.reload(sys.modules[m])
