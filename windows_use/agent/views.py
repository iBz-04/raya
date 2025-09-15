from pydantic import BaseModel
from typing import Optional
    
class AgentResult(BaseModel):
    content:str|None=None
    error:str|None=None

class Action(BaseModel):
    name:str
    params: dict

class AgentData(BaseModel):
    evaluate: Optional[str]=None
    memory: Optional[str]=None
    plan:Optional[str]=None
    thought: Optional[str]=None
    action: Optional[Action]=None
