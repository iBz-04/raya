from raya.tree.views import TreeState
from typing import Literal,Optional
from dataclasses import dataclass
from tabulate import tabulate

@dataclass
class App:
    name:str
    depth:int
    status:Literal['Maximized','Minimized','Normal']
    size:'Size'
    handle: int
    
    def to_row(self):
        return [self.name, self.depth, self.status, self.size.width, self.size.height, self.handle]
    
    def to_string(self) -> str:
        """Return a compact string representation of the App."""
        return f"Name: {self.name}|Depth: {self.depth}|Status: {self.status}|Size: {self.size.to_string()} Handle: {self.handle}"

@dataclass
class Size:
    width:int
    height:int

    def to_string(self):
        return f'({self.width},{self.height})'

@dataclass
class DesktopState:
    apps:list[App]
    active_app:Optional[App]
    screenshot:bytes|None
    tree_state:TreeState

    def active_app_to_string(self) -> str:
        """Return a string for the active app or a default message if none."""
        if self.active_app is None:
            return "No active app"
        return self.active_app.to_string()

    def apps_to_string(self) -> str:
        """Return a string listing all apps or a default message if none."""
        if not self.apps:
            return "No apps opened"
        return "\n".join(app.to_string() for app in self.apps)