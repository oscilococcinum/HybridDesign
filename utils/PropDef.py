# SPDX-License-Identifier: LGPL-2.1-or-later
#pyright: standard
from typing import Literal, Any
from dataclasses import dataclass
from typing import Self
from utils.FreeCADInterfaces import FeatureLike

PropType = Literal["App::PropertyStringList", "App::PropertyEnumeration",
                    "App::PropertyInteger","App::PropertyBool",
                    "App::PropertyFloat", "App::PropertyLength",
                    "App::PropertyLink", "App::PropertyLinkList",
                    "App::PropertyLinkSub", "App::PropertyLinkSubList",
                    "App::PropertyAngle"]
class PropDef:
    def __init__(self, type: PropType, name: str, section: str, description: str, defVal: Any | None = None) -> None:
        self.type: PropType = type
        self.name: str = name
        self.section: str = section
        self.description: str = description
        self.defVal: Any | None = defVal

class PropertyStringList(PropDef):
    def __init__(self, section: str, description: str, defVal: Any | None = None) -> None:
        super().__init__(type = "App::PropertyStringList", name='', section=section, description=description, defVal=defVal)

class PropertyEnumeration(PropDef):
    def __init__(self, section: str, description: str, defVal: Any | None = None) -> None:
        super().__init__(type = "App::PropertyEnumeration", name='', section=section, description=description, defVal=defVal)

class PropertyInteger(PropDef):
    def __init__(self, section: str, description: str, defVal: Any | None = None) -> None:
        super().__init__(type = "App::PropertyInteger", name='', section=section, description=description, defVal=defVal)

class PropertyBool(PropDef):
    def __init__(self, section: str, description: str, defVal: Any | None = None) -> None:
        super().__init__(type = "App::PropertyBool", name='', section=section, description=description, defVal=defVal)

class PropertyFloat(PropDef):
    def __init__(self, section: str, description: str, defVal: Any | None = None) -> None:
        super().__init__(type = "App::PropertyFloat", name='', section=section, description=description, defVal=defVal)

class PropertyLength(PropDef):
    def __init__(self, section: str, description: str, defVal: Any | None = None) -> None:
        super().__init__(type = "App::PropertyLength", name='', section=section, description=description, defVal=defVal)

class PropertyLink(PropDef):
    def __init__(self, section: str, description: str, defVal: Any | None = None) -> None:
        super().__init__(type = "App::PropertyLink", name='', section=section, description=description, defVal=defVal)

class PropertyLinkList(PropDef):
    def __init__(self, section: str, description: str, defVal: Any | None = None) -> None:
        super().__init__(type = "App::PropertyLinkList", name='', section=section, description=description, defVal=defVal)

class PropertyLinkSub(PropDef):
    def __init__(self, section: str, description: str, defVal: Any | None = None) -> None:
        super().__init__(type = "App::PropertyLinkSub", name='', section=section, description=description, defVal=defVal)

class PropertyLinkSubList(PropDef):
    def __init__(self, section: str, description: str, defVal: Any | None = None) -> None:
        super().__init__(type = "App::PropertyLinkSubList", name='', section=section, description=description, defVal=defVal)

class PropertyAngle(PropDef):
    def __init__(self, section: str, description: str, defVal: Any | None = None) -> None:
        super().__init__(type = "App::PropertyAngle", name='', section=section, description=description, defVal=defVal)