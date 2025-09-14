from typing import Set

BROWSER_NAMES=set(['msedge.exe','chrome.exe','firefox.exe'])

AVOIDED_APPS:Set[str]=set([
    'Recording toolbar'
])

EXCLUDED_APPS:Set[str]=set([
    'Progman','Shell_TrayWnd',
    'Microsoft.UI.Content.PopupWindowSiteBridge',
    'Windows.UI.Core.CoreWindow',
]).union(AVOIDED_APPS)