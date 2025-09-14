from windows_use.agent.tools.service import click_tool, type_tool, launch_tool, shell_tool, clipboard_tool, done_tool, shortcut_tool, scroll_tool, drag_tool, move_tool, key_tool, wait_tool, scrape_tool, switch_tool, resize_tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from windows_use.agent.utils import extract_agent_data, image_message
from langchain_core.language_models.chat_models import BaseChatModel
from windows_use.agent.registry.views import ToolResult
from windows_use.agent.registry.service import Registry
from windows_use.agent.prompt.service import Prompt
from live_inspect.watch_cursor import WatchCursor
from langgraph.graph import START,END,StateGraph
from windows_use.agent.views import AgentResult
from windows_use.desktop.service import Desktop
from windows_use.agent.state import AgentState
from langchain_core.tools import BaseTool
from contextlib import nullcontext
from rich.markdown import Markdown
from rich.console import Console
from termcolor import colored
from textwrap import shorten
from typing import Literal
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Agent:
    '''
    Windows Use

    An agent that can interact with GUI elements on Windows

    Args:
        instructions (list[str], optional): Instructions for the agent. Defaults to [].
        browser (Literal['edge', 'chrome', 'firefox'], optional): Browser the agent should use (Make sure this browser is installed). Defaults to 'edge'.
        additional_tools (list[BaseTool], optional): Additional tools for the agent. Defaults to [].
        llm (BaseChatModel): Language model for the agent. Defaults to None.
        consecutive_failures (int, optional): Maximum number of consecutive failures for the agent. Defaults to 3.
        max_steps (int, optional): Maximum number of steps for the agent. Defaults to 100.
        use_vision (bool, optional): Whether to use vision for the agent. Defaults to False.
        auto_minimize (bool, optional): Whether to automatically minimize the IDE while agent is working. Defaults to False.

    Returns:
        Agent
    '''
    def __init__(self,instructions:list[str]=[],additional_tools:list[BaseTool]=[],browser:Literal['edge','chrome','firefox']='edge', llm: BaseChatModel=None,consecutive_failures:int=3,max_steps:int=20,use_vision:bool=False,auto_minimize:bool=False):
        self.name='Windows Use'
        self.description='An agent that can interact with GUI elements on Windows' 
        self.registry = Registry([
            click_tool,type_tool, launch_tool, shell_tool, clipboard_tool,
            done_tool, shortcut_tool, scroll_tool, drag_tool, move_tool,
            key_tool, wait_tool, scrape_tool, switch_tool, resize_tool
        ] + additional_tools)
        self.instructions=instructions
        self.browser=browser
        self.max_steps=max_steps
        self.consecutive_failures=consecutive_failures
        self.auto_minimize=auto_minimize
        self.use_vision=use_vision
        self.llm = llm
        self.watch_cursor = WatchCursor()
        self.desktop = Desktop()
        self.console=Console()
        self.graph=self.create_graph()

    def reason(self,state:AgentState):
        steps=state.get('steps')
        max_steps=state.get('max_steps')
        messages=state.get('messages')
        message=self.llm.invoke(messages)
        logger.info(f"Iteration: {steps}")
        agent_data = extract_agent_data(message=message)
        logger.info(colored(f"📝: Evaluate: {agent_data.evaluate}",color='yellow',attrs=['bold']))
        logger.info(colored(f"📒: Memory: {agent_data.memory}",color='light_green',attrs=['bold']))
        logger.info(colored(f"📚: Plan: {agent_data.plan}",color='light_blue',attrs=['bold']))
        logger.info(colored(f"💭: Thought: {agent_data.thought}",color='light_magenta',attrs=['bold']))

        last_message = state.get('messages').pop()
        if isinstance(last_message, HumanMessage):
            message=HumanMessage(content=Prompt.previous_observation_prompt(steps=steps,max_steps=max_steps,observation=state.get('previous_observation')))
            return {**state,'agent_data':agent_data,'messages':[message],'steps':steps+1}

    def action(self,state:AgentState):
        steps=state.get('steps')
        max_steps=state.get('max_steps')
        agent_data=state.get('agent_data')
        name = agent_data.action.name
        params = agent_data.action.params
        ai_message = AIMessage(content=Prompt.action_prompt(agent_data=agent_data))
        logger.info(colored(f"🔧: Action: {name}({', '.join(f'{k}={v}' for k, v in params.items())})",color='blue',attrs=['bold']))
        
        tool_result = self.registry.execute(tool_name=name, desktop=self.desktop, **params)
        observation=tool_result.content if tool_result.is_success else tool_result.error
        logger.info(colored(f"🔭: Observation: {shorten(observation,500,placeholder='...')}",color='green',attrs=['bold']))
        desktop_state = self.desktop.get_state(use_vision=self.use_vision)
        prompt=Prompt.observation_prompt(query=state.get('input'),steps=steps,max_steps=max_steps, tool_result=tool_result, desktop_state=desktop_state)
        human_message=image_message(prompt=prompt,image=desktop_state.screenshot) if self.use_vision and desktop_state.screenshot else HumanMessage(content=prompt)
        return {**state,'agent_data':None,'messages':[ai_message, human_message],'previous_observation':observation}

    def answer(self,state:AgentState):
        agent_data=state.get('agent_data')
        name = agent_data.action.name
        params = agent_data.action.params
        tool_result = self.registry.execute(tool_name=name, desktop=None, **params)
        ai_message = AIMessage(content=Prompt.answer_prompt(agent_data=agent_data, tool_result=tool_result))
        logger.info(colored(f"📜: Final Answer: {tool_result.content}",color='cyan',attrs=['bold']))
        return {**state,'agent_data':None,'messages':[ai_message],'previous_observation':None,'output':tool_result.content}

    def main_controller(self,state:AgentState):
        if state.get('steps')<state.get('max_steps'):
            agent_data=state.get('agent_data')
            action_name=agent_data.action.name
            if action_name!='Done Tool':
                return 'action'
        return 'answer'    

    def create_graph(self):
        graph=StateGraph(AgentState)
        graph.add_node('reason',self.reason)
        graph.add_node('action',self.action)
        graph.add_node('answer',self.answer)

        graph.add_edge(START,'reason')
        graph.add_conditional_edges('reason',self.main_controller)
        graph.add_edge('action','reason')
        graph.add_edge('answer',END)

        return graph.compile(debug=False)

    def invoke(self,query: str)->AgentResult:
        steps=1
        with (self.desktop.auto_minimize() if self.auto_minimize else nullcontext()):
            desktop_state = self.desktop.get_state(use_vision=self.use_vision)
            language=self.desktop.get_default_language()
            tools_prompt = self.registry.get_tools_prompt()
            system_prompt=Prompt.system_prompt(browser=self.browser,language=language,instructions=self.instructions,tools_prompt=tools_prompt,max_steps=self.max_steps)
            system_message=SystemMessage(content=system_prompt)
            human_prompt=Prompt.observation_prompt(query=query,steps=steps,max_steps=self.max_steps,tool_result=ToolResult(is_success=True, content="The desktop is ready to operate."), desktop_state=desktop_state)
            human_message=image_message(prompt=human_prompt,image=desktop_state.screenshot) if self.use_vision and desktop_state.screenshot else HumanMessage(content=human_prompt)
            messages=[system_message,human_message]
            state={
                'input':query,
                'steps':steps,
                'max_steps':self.max_steps,
                'output':'',
                'error':'',
                'consecutive_failures':0,
                'agent_data':None,
                'messages':messages,
                'previous_observation':None
            }
            try:
                with self.watch_cursor:
                    response=self.graph.invoke(state,config={'recursion_limit':self.max_steps*10})         
            except Exception as error:
                response={
                    'output':None,
                    'error':f"Error: {error}"
                }
        return AgentResult(content=response['output'], error=response['error'])

    def print_response(self,query: str):
        response=self.invoke(query)
        self.console.print(Markdown(response.content or response.error))   