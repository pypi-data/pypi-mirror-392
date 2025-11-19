"""AST parsing utilities for Python source code analysis."""

import ast
from collections.abc import Iterator
from pathlib import Path
from typing import Optional


class ASTWalker:
    """Walks Python AST nodes for a given codebase.

    This class provides functionality to traverse Python files in a directory
    and parse them into AST nodes for analysis.
    """

    def __init__(self, root_path: Path) -> None:
        """Initialize the AST walker.

        Args:
            root_path: Root directory to start walking from
        """
        self.root_path = root_path

    def walk_files(self) -> Iterator[tuple[Path, ast.Module]]:
        """Walk through Python files and yield parsed AST modules.

        Yields:
            Tuple of (file_path, ast_module) for each valid Python file

        Raises:
            SyntaxError: If a Python file cannot be parsed
        """
        for py_file in self._find_python_files():
            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content, filename=str(py_file))
                yield py_file, tree
            except SyntaxError as e:
                # Log but continue processing other files
                print(f"Warning: Failed to parse {py_file}: {e}")
                continue
            except Exception as e:
                print(f"Warning: Error reading {py_file}: {e}")
                continue

    def _find_python_files(self) -> Iterator[Path]:
        """Find all Python files in the root path.

        Yields:
            Path objects for each .py file found

        Note:
            Excludes common non-source directories like .git, __pycache__, etc.
        """
        exclude_dirs = {
            ".git",
            ".venv",
            "venv",
            ".tox",
            ".pytest_cache",
            "__pycache__",
            "build",
            "dist",
            ".eggs",
            "*.egg-info",
            ".mypy_cache",
            ".ruff_cache",
        }

        for item in self.root_path.rglob("*.py"):
            # Skip excluded directories
            if any(excluded in item.parts for excluded in exclude_dirs):
                continue
            yield item

    @staticmethod
    def get_function_end_line(node: ast.FunctionDef) -> int:
        """Get the ending line number of a function definition.

        Args:
            node: AST FunctionDef node

        Returns:
            Line number where the function ends
        """
        if not node.body:
            return node.lineno

        # Find the maximum line number in the function body
        max_line = node.lineno
        for child in ast.walk(node):
            if hasattr(child, "lineno"):
                max_line = max(max_line, child.lineno)
            if hasattr(child, "end_lineno") and child.end_lineno:
                max_line = max(max_line, child.end_lineno)

        return max_line

    @staticmethod
    def get_decorator_name(decorator: ast.expr) -> Optional[str]:
        """Extract the name from a decorator expression.

        Args:
            decorator: AST decorator expression

        Returns:
            Decorator name as string, or None if unable to extract
        """
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return f"{ASTWalker._get_attr_chain(decorator.func)}"
        elif isinstance(decorator, ast.Attribute):
            return f"{ASTWalker._get_attr_chain(decorator)}"
        return None

    @staticmethod
    def _get_attr_chain(node: ast.Attribute) -> str:
        """Get the full attribute chain from an Attribute node.

        Args:
            node: AST Attribute node

        Returns:
            Full attribute chain as a string (e.g., 'module.submodule.attr')
        """
        parts = [node.attr]
        current = node.value

        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value

        if isinstance(current, ast.Name):
            parts.append(current.id)

        return ".".join(reversed(parts))
