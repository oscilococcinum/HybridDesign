# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard
import FreeCADGui as Gui #type: ignore

FEATURE_NAME = "IsolateShape"


def proxyCommand() -> None:
    Gui.runCommand("Part_SimpleCopy", 0)
