"""
TUI Screens for Yirifi Data Quality Framework.
"""

from .category_screen import CategoryScreen
from .operation_config_screen import OperationConfigScreen
from .operation_list_screen import OperationListScreen
from .suboperation_screen import SuboperationScreen

# Plugin system screens
from .scripts_list_screen import ScriptsListScreen
from .script_parameters_screen import ScriptParametersScreen
from .script_execution_screen import ScriptExecutionScreen
from .preview_screen import PreviewScreen
from .results_screen import ResultsScreen

__all__ = [
    "CategoryScreen",
    "OperationConfigScreen",
    "OperationListScreen",
    "SuboperationScreen",
    # Plugin screens
    "ScriptsListScreen",
    "ScriptParametersScreen",
    "ScriptExecutionScreen",
    "PreviewScreen",
    "ResultsScreen",
]
