"""AST parsing utilities for Python source code analysis."""

import ast
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Optional


class ASTWalker:
    """Walks Python AST nodes for a given codebase.

    This class provides functionality to traverse Python files in a directory
    and parse them into AST nodes for analysis.
    """

    def __init__(
        self,
        root_path: Path,
        include_patterns: Optional[list[str]] = None,
        exclude_patterns: Optional[list[str]] = None,
    ) -> None:
        """Initialize the AST walker.

        Args:
            root_path: Root directory to start walking from
            include_patterns: List of regex patterns for files to include
            exclude_patterns: List of regex patterns for files to exclude
        """
        self.root_path = root_path
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []

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
            Also filters based on include/exclude patterns if provided.
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

            # Apply include/exclude filters
            if not self._should_include_file(item):
                continue

            yield item

    def _should_include_file(self, file_path: Path) -> bool:
        """Check if a file should be included based on include/exclude patterns.

        Args:
            file_path: Path to check

        Returns:
            True if file should be included, False otherwise
        """
        # Get relative path from root for pattern matching
        try:
            rel_path = file_path.relative_to(self.root_path)
        except ValueError:
            # File is not relative to root path, include it
            rel_path = file_path

        path_str = str(rel_path)

        # If exclude patterns are specified, check them first
        if self.exclude_patterns:
            for pattern in self.exclude_patterns:
                if re.search(pattern, path_str):
                    return False

        # If include patterns are specified, file must match at least one
        if self.include_patterns:
            for pattern in self.include_patterns:
                if re.search(pattern, path_str):
                    return True
            # No include pattern matched
            return False

        # No patterns specified or only exclude patterns (and didn't match)
        return True

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
