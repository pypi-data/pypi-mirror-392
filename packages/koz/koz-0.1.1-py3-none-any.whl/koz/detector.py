"""Monkeypatch detection logic."""

import ast
from pathlib import Path
from typing import Optional

from koz.parser import ASTWalker
from koz.schema import PatchInfo, PatchType


class PatchDetector:
    """Detects monkeypatching patterns in Python AST.

    This detector identifies three types of patches:
    1. fastcore.patch_to() decorator usage
    2. Direct attribute assignment monkeypatching
    3. functools.wraps decorator in __init__ methods
    """

    def __init__(self) -> None:
        """Initialize the patch detector."""
        pass

    def detect_patches(self, file_path: Path, tree: ast.Module) -> list[PatchInfo]:
        """Detect all patches in an AST module.

        Args:
            file_path: Path to the source file
            tree: Parsed AST module

        Returns:
            List of detected patches
        """
        patches: list[PatchInfo] = []

        # Detect decorator-based patches (patch_to and wraps)
        patches.extend(self._detect_decorator_patches(file_path, tree))

        # Detect direct assignment patches
        patches.extend(self._detect_direct_assignment_patches(file_path, tree))

        return patches

    def _detect_decorator_patches(
        self, file_path: Path, tree: ast.Module
    ) -> list[PatchInfo]:
        """Detect patches using decorators (patch_to and wraps).

        Args:
            file_path: Path to the source file
            tree: Parsed AST module

        Returns:
            List of detected decorator-based patches
        """
        patches: list[PatchInfo] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue

            # Check for patch_to decorator
            patch_info = self._check_patch_to_decorator(file_path, node)
            if patch_info:
                patches.append(patch_info)
                continue

            # Check for wraps decorator in __init__ methods
            patch_info = self._check_wraps_decorator(file_path, node)
            if patch_info:
                patches.append(patch_info)

        return patches

    def _check_patch_to_decorator(
        self, file_path: Path, node: ast.FunctionDef
    ) -> Optional[PatchInfo]:
        """Check if a function uses the patch_to decorator.

        Args:
            file_path: Path to the source file
            node: Function definition node

        Returns:
            PatchInfo if patch_to decorator is found, None otherwise
        """
        for decorator in node.decorator_list:
            decorator_name = ASTWalker.get_decorator_name(decorator)

            if decorator_name and "patch_to" in decorator_name:
                # Extract target class from decorator arguments
                target_class = self._extract_patch_to_target(decorator)

                if target_class:
                    return PatchInfo(
                        target_class=target_class,
                        target_method=node.name,
                        file_path=str(file_path),
                        line_start=node.lineno,
                        line_end=ASTWalker.get_function_end_line(node),
                        patch_type=PatchType.PATCH_TO,
                        timestamp=None,
                        author=None,
                    )

        return None

    def _extract_patch_to_target(self, decorator: ast.expr) -> Optional[str]:
        """Extract the target class from a patch_to decorator.

        Args:
            decorator: Decorator AST node

        Returns:
            Target class name or None
        """
        if isinstance(decorator, ast.Call) and decorator.args:
            # patch_to(ClassName)
            arg = decorator.args[0]
            if isinstance(arg, ast.Name):
                return arg.id
            elif isinstance(arg, ast.Attribute):
                return ASTWalker._get_attr_chain(arg)

        return None

    def _check_wraps_decorator(
        self, file_path: Path, node: ast.FunctionDef
    ) -> Optional[PatchInfo]:
        """Check if a function uses functools.wraps in an __init__ method.

        This pattern is used for monkeypatching methods during class initialization.

        Args:
            file_path: Path to the source file
            node: Function definition node

        Returns:
            PatchInfo if wraps decorator pattern is found, None otherwise
        """
        # Only check __init__ methods
        if node.name != "__init__":
            return None

        # Look for wraps decorator usage inside __init__
        for child in ast.walk(node):
            if isinstance(child, ast.FunctionDef) and child != node:
                for decorator in child.decorator_list:
                    decorator_name = ASTWalker.get_decorator_name(decorator)

                    if decorator_name and "wraps" in decorator_name:
                        # Try to determine the target from decorator argument
                        target_method = self._extract_wraps_target(decorator)

                        if target_method:
                            # Try to find the class this __init__ belongs to
                            target_class = self._find_enclosing_class(node, child)

                            return PatchInfo(
                                target_class=target_class or "Unknown",
                                target_method=target_method,
                                file_path=str(file_path),
                                line_start=child.lineno,
                                line_end=ASTWalker.get_function_end_line(child),
                                patch_type=PatchType.WRAPS_DECORATOR,
                                timestamp=None,
                                author=None,
                            )

        return None

    def _extract_wraps_target(self, decorator: ast.expr) -> Optional[str]:
        """Extract the target method from a wraps decorator.

        Args:
            decorator: Decorator AST node

        Returns:
            Target method name or None
        """
        if isinstance(decorator, ast.Call) and decorator.args:
            arg = decorator.args[0]
            if isinstance(arg, ast.Attribute):
                return arg.attr
            elif isinstance(arg, ast.Name):
                return arg.id

        return None

    def _find_enclosing_class(
        self, init_node: ast.FunctionDef, inner_node: ast.FunctionDef
    ) -> Optional[str]:
        """Find the class that encloses an __init__ method.

        Args:
            init_node: The __init__ method node
            inner_node: Inner function node

        Returns:
            Class name or None
        """
        # This is a simplified approach - would need full tree traversal
        # to properly determine enclosing class
        return "Unknown"

    def _detect_direct_assignment_patches(
        self, file_path: Path, tree: ast.Module
    ) -> list[PatchInfo]:
        """Detect direct attribute assignment monkeypatching.

        Patterns like: SomeClass.method = new_function

        Args:
            file_path: Path to the source file
            tree: Parsed AST module

        Returns:
            List of detected direct assignment patches
        """
        patches: list[PatchInfo] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                patch_info = self._check_direct_assignment(file_path, node)
                if patch_info:
                    patches.append(patch_info)

        return patches

    def _check_direct_assignment(
        self, file_path: Path, node: ast.Assign
    ) -> Optional[PatchInfo]:
        """Check if an assignment is a direct monkeypatch.

        Args:
            file_path: Path to the source file
            node: Assignment node

        Returns:
            PatchInfo if direct monkeypatch is found, None otherwise
        """
        # Look for pattern: Class.method = value
        for target in node.targets:
            if isinstance(target, ast.Attribute):
                if isinstance(target.value, ast.Name):
                    # Simple case: ClassName.method = ...
                    return PatchInfo(
                        target_class=target.value.id,
                        target_method=target.attr,
                        file_path=str(file_path),
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        patch_type=PatchType.DIRECT_ASSIGNMENT,
                        timestamp=None,
                        author=None,
                    )
                elif isinstance(target.value, ast.Attribute):
                    # Nested case: module.ClassName.method = ...
                    class_chain = ASTWalker._get_attr_chain(target.value)
                    return PatchInfo(
                        target_class=class_chain,
                        target_method=target.attr,
                        file_path=str(file_path),
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        patch_type=PatchType.DIRECT_ASSIGNMENT,
                        timestamp=None,
                        author=None,
                    )

        return None
