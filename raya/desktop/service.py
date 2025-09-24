from uiautomation import Control, GetRootControl, IsIconic, IsZoomed, IsWindowVisible, ControlType, ControlFromCursor, SetWindowTopmost, IsTopLevelWindow, ShowWindow, ControlFromHandle
from raya.desktop.config import EXCLUDED_APPS, BROWSER_NAMES
from raya.desktop.views import DesktopState,App,Size
from raya.tree.service import Tree
from PIL.Image import Image as PILImage
from contextlib import contextmanager
from fuzzywuzzy import process
from psutil import Process
from time import sleep
from io import BytesIO
from PIL import Image
import subprocess
import pyautogui
import ctypes
import base64
import csv
import io

class Desktop:
    def __init__(self):
        self.desktop_state=None
        
    def get_state(self,use_vision:bool=False)->DesktopState:
        tree=Tree(self)
        active_app,apps=self.get_apps()
        tree_state=tree.get_state()
        if use_vision:
            annotated_screenshot=tree.annotated_screenshot(tree_state.interactive_nodes,scale=0.5)
            screenshot=self.screenshot_in_bytes(annotated_screenshot)
        else:
            screenshot=None
        self.desktop_state=DesktopState(apps= apps,active_app=active_app,screenshot=screenshot,tree_state=tree_state)
        return self.desktop_state
    
    def get_window_element_from_element(self,element:Control)->Control|None:
        while element is not None:
            if IsTopLevelWindow(element.NativeWindowHandle):
                return element
            element = element.GetParentControl()
        return None
    
    def get_active_app(self,apps:list[App])->App|None:
        if len(apps)>0 and apps[0].status != "Minimized":
            return apps[0]
        return None
    
    def get_app_status(self,control:Control)->str:
        if IsIconic(control.NativeWindowHandle):
            return 'Minimized'
        elif IsZoomed(control.NativeWindowHandle):
            return 'Maximized'
        elif IsWindowVisible(control.NativeWindowHandle):
            return 'Normal'
        else:
            return 'Hidden'
    
    def get_cursor_location(self)->tuple[int,int]:
        position=pyautogui.position()
        return (position.x,position.y)
    
    def get_element_under_cursor(self)->Control:
        return ControlFromCursor()
    
    def get_apps_from_start_menu(self)->dict[str,str]:
        command='Get-StartApps | ConvertTo-Csv -NoTypeInformation'
        apps_info,_=self.execute_command(command)
        reader=csv.DictReader(io.StringIO(apps_info))
        return {row.get('Name').lower():row.get('AppID') for row in reader}
    
    def is_app_running(self,name:str)->bool:
        apps=self.get_apps()
        return process.extractOne(name,apps,score_cutoff=60) is not None
    
    def _find_powershell(self) -> str | None:
        """Return the path to the PowerShell executable available on the system.
        Tries `powershell`, `powershell.exe`, and `pwsh` in that order."""
        from shutil import which

        for exe in ("powershell", "powershell.exe", "pwsh"):
            path = which(exe)
            if path:
                return path
        return None

    def execute_command(self, command: str) -> tuple[str, int]:
        """Execute a PowerShell command and return (stdout, returncode).

        The method finds the first available PowerShell executable. If none is
        found, a descriptive error message is returned instead of raising an
        unhandled exception. The entire *command* string is passed to the
        `-Command` argument to preserve pipes and other PowerShell syntax.
        """
        powershell_path = self._find_powershell()
        if powershell_path is None:
            error_msg = (
                "PowerShell executable was not found in PATH. Make sure either\n"
                "`powershell.exe` (Windows PowerShell) or `pwsh` (PowerShell 7+)\n"
                "is installed and its directory is added to the system PATH."
            )
            return (error_msg, 1)

        try:
            result = subprocess.run(
                [powershell_path, "-Command", command],
                capture_output=True,
                text=True,
                check=True,
            )
            return (result.stdout, result.returncode)
        except subprocess.CalledProcessError as e:
            # Return stderr as part of the output to help with debugging
            output = (e.stdout or "") + ("\n" + e.stderr if e.stderr else "")
            return (output, e.returncode)
        
    def is_app_browser(self,node:Control):
        proc = Process(node.ProcessId)
        return proc.name() in BROWSER_NAMES
    
    def get_default_language(self) -> str:
        """Return the OS default language display name.

        Falls back to `"Unknown"` if the information cannot be parsed (e.g.
        PowerShell not available or unexpected output). This prevents `TypeError`
        when `None` values appear in the CSV rows.
        """
        command = (
            "Get-Culture | Select-Object Name,DisplayName | ConvertTo-Csv -NoTypeInformation"
        )
        response, _ = self.execute_command(command)

        display_names: list[str] = []
        try:
            reader = csv.DictReader(io.StringIO(response))
            display_names = [row.get("DisplayName") for row in reader if row.get("DisplayName")]
        except Exception:
            # If parsing fails, we'll fall back to Unknown below
            pass

        return " ".join(display_names) if display_names else "Unknown"
    
    def resize_app(self,name:str,size:tuple[int,int]=None,loc:tuple[int,int]=None)->tuple[str,int]:
        apps=self.get_apps()
        matched_app:tuple[App,int]|None=process.extractOne(name,apps)
        if matched_app is None:
            return (f'Application {name.title()} not found.',1)
        app,_=matched_app
        app_control=ControlFromHandle(app.handle)
        if loc is None:
            x=app_control.BoundingRectangle.left
            y=app_control.BoundingRectangle.top
            loc=(x,y)
        if size is None:
            width=app_control.BoundingRectangle.width()
            height=app_control.BoundingRectangle.height()
            size=(width,height)
        x,y=loc
        width,height=size
        app_control.MoveWindow(x,y,width,height)
        return (f'Application {name.title()} resized to {width}x{height} at {x},{y}.',0)
        
    def launch_app(self,name:str):
        if not name or not isinstance(name, str):
            return ('Invalid application name provided.', None, 1)
        
        apps_map=self.get_apps_from_start_menu()
        if not apps_map:
            return ('Could not retrieve start menu applications.', None, 1)
            
        matched_app=process.extractOne(name, apps_map.keys(), score_cutoff=60)
        if matched_app is None:
            # Try common application alternatives
            common_apps = {
                'word': ['microsoft word', 'winword', 'word'],
                'excel': ['microsoft excel', 'excel'],
                'powerpoint': ['microsoft powerpoint', 'powerpoint'],
                'chrome': ['google chrome', 'chrome'],
                'firefox': ['mozilla firefox', 'firefox'],
                'edge': ['microsoft edge', 'edge'],
                'notepad': ['notepad'],
                'calculator': ['calculator', 'calc'],
                'paint': ['paint'],
                'cmd': ['command prompt', 'cmd'],
                'powershell': ['windows powershell', 'powershell']
            }
            
            name_lower = name.lower()
            for key, alternatives in common_apps.items():
                if name_lower in alternatives or key in name_lower:
                    for alt in alternatives:
                        matched_app = process.extractOne(alt, apps_map.keys(), score_cutoff=60)
                        if matched_app:
                            break
                    if matched_app:
                        break
            
            if matched_app is None:
                return (f'Application "{name}" not found in start menu. Available apps: {", ".join(list(apps_map.keys())[:10])}...', None, 1)
        
        app_name, _ = matched_app
        appid = apps_map.get(app_name)
        if appid is None:
            return (f'Application ID not found for "{app_name}".', None, 1)
        
        try:
            if name.endswith('.exe'):
                response, status = self.execute_command(f'Start-Process "{appid}"')
            else:
                response, status = self.execute_command(f'Start-Process "shell:AppsFolder\\{appid}"')
            return app_name, response, status
        except Exception as e:
            return (f'Error launching {app_name}: {str(e)}', None, 1)
    
    def switch_app(self,name:str):
        apps={app.name:app for app in self.desktop_state.apps}
        matched_app:tuple[str,float]=process.extractOne(name,list(apps.keys()))
        if matched_app is None:
            return (f'Application {name.title()} not found.',1)
        app_name,_=matched_app
        app=apps.get(app_name)
        if IsIconic(app.handle):
            ShowWindow(app.handle, cmdShow=9)
            return (f'{app_name.title()} restored from minimized state.',0)
        elif SetWindowTopmost(app.handle,isTopmost=True):
            return (f'{app_name.title()} switched to foreground.',0)
        else:
            return (f'Failed to switch to {app_name.title()}.',1)
    
    def get_app_size(self,control:Control):
        window=control.BoundingRectangle
        if window.isempty():
            return Size(width=0,height=0)
        return Size(width=window.width(),height=window.height())
    
    def is_app_visible(self,app)->bool:
        is_minimized=self.get_app_status(app)!='Minimized'
        size=self.get_app_size(app)
        area=size.width*size.height
        is_overlay=self.is_overlay_app(app)
        return not is_overlay and is_minimized and area>10
    
    def is_overlay_app(self,element:Control) -> bool:
        no_children = len(element.GetChildren()) == 0
        is_name = "Overlay" in element.Name.strip()
        return no_children or is_name
        
    def get_apps(self) -> tuple[App|None,list[App]]:
        try:
            sleep(0.5)
            desktop = GetRootControl()  # Get the desktop control
            elements = desktop.GetChildren()
            apps = []
            for depth, element in enumerate(elements):
                if element.ClassName in EXCLUDED_APPS or self.is_overlay_app(element):
                    continue
                if element.ControlType in [ControlType.WindowControl, ControlType.PaneControl]:
                    status = self.get_app_status(element)
                    size=self.get_app_size(element)
                    apps.append(App(name=element.Name, depth=depth, status=status,size=size,handle=element.NativeWindowHandle))
        except Exception as ex:
            print(f"Error: {ex}")
            apps = []

        active_app=self.get_active_app(apps)
        apps=apps[1:] if len(apps)>1 else []
        return (active_app,apps)
    
    def get_dpi_scaling(self):
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        dpi = user32.GetDpiForSystem()
        return dpi / 96.0
    
    def screenshot_in_bytes(self,screenshot:PILImage)->bytes:
        buffer=BytesIO()
        screenshot.save(buffer,format='PNG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        data_uri = f"data:image/png;base64,{img_base64}"
        return data_uri

    def get_screenshot(self,scale:float=0.7)->Image.Image:
        screenshot=pyautogui.screenshot()
        size=(screenshot.width*scale, screenshot.height*scale)
        screenshot.thumbnail(size=size, resample=Image.Resampling.LANCZOS)
        return screenshot
    
    @contextmanager
    def auto_minimize(self):
        SW_MINIMIZE=6
        SW_RESTORE = 9
        try:
            user32 = ctypes.windll.user32
            hWnd = user32.GetForegroundWindow()
            user32.ShowWindow(hWnd, SW_MINIMIZE)
            yield
        finally:
            user32.ShowWindow(hWnd, SW_RESTORE)