from dataclasses import dataclass, field

@dataclass
class TreeState:
    interactive_nodes: list['TreeElementNode'] = field(default_factory=list)
    informative_nodes: list['TextElementNode'] = field(default_factory=list)
    scrollable_nodes: list['ScrollElementNode'] = field(default_factory=list)

    def interactive_elements_to_string(self) -> str:
        if not self.interactive_nodes:
            return ""
        lines = []
        for idx, node in enumerate(self.interactive_nodes):
            lines.append(
                f"Label: {idx} App Name: {node.app_name} ControlType: {node.control_type} "
                f"Control Name: {node.name} Shortcut: {node.shortcut} Cordinates: {node.center.to_string()}"
            )
        return "\n".join(lines)

    def informative_elements_to_string(self) -> str:
        if not self.informative_nodes:
            return ""
        lines = []
        for node in self.informative_nodes:
            lines.append(f"App Name: {node.app_name} Name: {node.name}")
        return "\n".join(lines)

    def scrollable_elements_to_string(self) -> str:
        if not self.scrollable_nodes:
            return ""
        lines = []
        base_index = len(self.interactive_nodes)
        for idx, node in enumerate(self.scrollable_nodes):
            lines.append(
                f"Label: {base_index+idx} App Name: {node.app_name} ControlType: {node.control_type} "
                f"Control Name: {node.name} Cordinates: {node.center.to_string()} "
                f"Horizontal Scrollable: {node.horizontal_scrollable} Vertical Scrollable: {node.vertical_scrollable}"
            )
        return "\n".join(lines)
    
@dataclass
class BoundingBox:
    left: int
    top: int
    right: int
    bottom: int
    width: int = field(init=False)
    height: int = field(init=False)

    def __post_init__(self):
        # Compute width and height based on coordinates
        self.width = self.right - self.left
        self.height = self.bottom - self.top

    def xywh_to_string(self):
        return f'({self.left},{self.top},{self.width},{self.height})'
    
    def xyxy_to_string(self):
        x1,y1,x2,y2=self.convert_xywh_to_xyxy()
        return f'({x1},{y1},{x2},{y2})'
    
    def convert_xywh_to_xyxy(self)->tuple[int,int,int,int]:
        x1,y1=self.left,self.top
        x2,y2=self.left+self.width,self.top+self.height
        return x1,y1,x2,y2

@dataclass
class Center:
    x:int
    y:int

    def to_string(self)->str:
        return f'({self.x},{self.y})'

@dataclass
class TreeElementNode:
    name: str
    control_type: str
    shortcut: str
    bounding_box: BoundingBox
    center: Center
    app_name: str

    def to_row(self, index: int):
        return [index, self.app_name, self.control_type, self.name, self.shortcut, self.center.to_string()]


@dataclass
class TextElementNode:
    name: str
    app_name: str

    def to_row(self):
        return [self.app_name, self.name]


@dataclass
class ScrollElementNode:
    name: str
    control_type: str
    app_name: str
    bounding_box: BoundingBox
    center: Center
    horizontal_scrollable: bool
    vertical_scrollable: bool

    def to_row(self, index: int, base_index: int):
        return [
            base_index + index,
            self.app_name,
            self.control_type,
            self.name,
            self.center.to_string(),
            self.horizontal_scrollable,
            self.vertical_scrollable,
        ]
