import ast
import inspect
from typing import Callable


BLOCKING_PATTERNS = {
    'time.sleep',
    'requests.get',
    'requests.post',
    'requests.put',
    'requests.delete',
    'requests.patch',
    'requests.request',
    'open',
    'input',
    'os.system',
    'subprocess.run',
    'subprocess.call',
    'subprocess.check_output',
}


class BlockingCallVisitor(ast.NodeVisitor):
    """AST visitor to detect potentially blocking calls in async functions."""

    def __init__(self):
        self.has_blocking = False
        self.blocking_calls = []

    def visit_Call(self, node):
        call_name = self._get_call_name(node)

        if call_name in BLOCKING_PATTERNS:
            self.has_blocking = True
            self.blocking_calls.append(call_name)

        self.generic_visit(node)

    def _get_call_name(self, node):
        """Extract the full name of a function call."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return '.'.join(reversed(parts))
        return ''


def detect_sync_blocking(func: Callable) -> bool:
    """
    Analyze async function source code to detect synchronous blocking operations.

    Args:
        func: Async function to analyze

    Returns:
        True if potentially blocking operations detected, False otherwise
    """
    try:
        source = inspect.getsource(func)
        tree = ast.parse(source)

        visitor = BlockingCallVisitor()
        visitor.visit(tree)

        return visitor.has_blocking

    except (OSError, TypeError):
        return False
