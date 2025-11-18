"""Code comment parser for extracting translatable content from Python files.

Uses AST (Abstract Syntax Tree) to safely extract:
- Inline comments (# comments)
- Docstrings (function, class, module level)
- String literals in specific contexts

Preserves code structure for accurate reconstruction after translation.
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class CommentNode:
    """Represents a translatable comment in code."""

    node_type: str  # 'inline_comment', 'docstring', 'string_literal'
    content: str  # Original content
    line_number: int  # Line number in source
    column_offset: int  # Column offset
    context: str  # Surrounding context
    translated: Optional[str] = None  # Translation (filled later)


@dataclass
class ParsedCodeFile:
    """Result of parsing a code file."""

    file_path: str
    comments: List[CommentNode] = field(default_factory=list)
    docstrings: List[CommentNode] = field(default_factory=list)
    original_lines: List[str] = field(default_factory=list)
    encoding: str = "utf-8"

    def get_all_translatable(self) -> List[CommentNode]:
        """Get all translatable nodes."""
        return self.comments + self.docstrings

    def total_nodes(self) -> int:
        """Get total number of translatable nodes."""
        return len(self.comments) + len(self.docstrings)


class CodeCommentParser:
    """Parses Python code to extract translatable comments and docstrings.

    Uses AST for accurate parsing while preserving code structure.
    """

    def __init__(self):
        """Initialize parser."""
        self.parsed_files = {}

    def parse_file(self, file_path: str) -> ParsedCodeFile:
        """Parse a Python file to extract comments and docstrings.

        Args:
            file_path: Path to Python file

        Returns:
            ParsedCodeFile with extracted translatable content
        """
        file_path_obj = Path(file_path)

        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file
        try:
            content = file_path_obj.read_text(encoding="utf-8")
            encoding = "utf-8"
        except UnicodeDecodeError:
            # Try alternative encodings
            for enc in ["utf-8-sig", "latin-1", "cp949"]:
                try:
                    content = file_path_obj.read_text(encoding=enc)
                    encoding = enc
                    break
                except:
                    continue
            else:
                raise ValueError(f"Cannot decode file: {file_path}")

        lines = content.splitlines(keepends=True)

        # Parse AST
        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError as e:
            # Return empty result for files with syntax errors
            return ParsedCodeFile(
                file_path=file_path, original_lines=lines, encoding=encoding
            )

        result = ParsedCodeFile(
            file_path=file_path, original_lines=lines, encoding=encoding
        )

        # Extract inline comments
        result.comments = self._extract_inline_comments(lines)

        # Extract docstrings
        result.docstrings = self._extract_docstrings(tree, lines)

        return result

    def _extract_inline_comments(self, lines: List[str]) -> List[CommentNode]:
        """Extract inline # comments from code lines."""
        comments = []

        for line_num, line in enumerate(lines, start=1):
            # Find # comments (not in strings)
            comment_match = re.search(r"#\s*(.+)$", line)

            if comment_match:
                # Check if # is inside a string
                before_comment = line[: comment_match.start()]

                # Simple check: count quotes before #
                single_quotes = before_comment.count("'") - before_comment.count("\\'")
                double_quotes = before_comment.count('"') - before_comment.count('\\"')

                # If odd number of quotes, # is likely in string
                if single_quotes % 2 == 0 and double_quotes % 2 == 0:
                    comment_text = comment_match.group(1).strip()

                    if comment_text:  # Non-empty comment
                        # Get context (surrounding code)
                        context_start = max(0, line_num - 2)
                        context_end = min(len(lines), line_num + 1)
                        context = "".join(lines[context_start:context_end])

                        comments.append(
                            CommentNode(
                                node_type="inline_comment",
                                content=comment_text,
                                line_number=line_num,
                                column_offset=comment_match.start(),
                                context=context.strip(),
                            )
                        )

        return comments

    def _extract_docstrings(self, tree: ast.AST, lines: List[str]) -> List[CommentNode]:
        """Extract docstrings from AST."""
        docstrings = []

        for node in ast.walk(tree):
            # Check for docstrings in functions, classes, modules
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                docstring = ast.get_docstring(node)

                if docstring:
                    # Get line number
                    if hasattr(node, "lineno"):
                        line_num = node.lineno
                    else:
                        line_num = 1  # Module docstring

                    # Get context
                    if isinstance(node, ast.FunctionDef):
                        context_type = f"function: {node.name}"
                    elif isinstance(node, ast.ClassDef):
                        context_type = f"class: {node.name}"
                    else:
                        context_type = "module"

                    docstrings.append(
                        CommentNode(
                            node_type="docstring",
                            content=docstring,
                            line_number=line_num,
                            column_offset=0,
                            context=context_type,
                        )
                    )

        return docstrings

    def parse_directory(
        self, directory: str, recursive: bool = True
    ) -> Dict[str, ParsedCodeFile]:
        """Parse all Python files in a directory.

        Args:
            directory: Directory path
            recursive: Whether to recurse into subdirectories

        Returns:
            Dict mapping file path to ParsedCodeFile
        """
        dir_path = Path(directory)
        results = {}

        if recursive:
            py_files = dir_path.rglob("*.py")
        else:
            py_files = dir_path.glob("*.py")

        for py_file in py_files:
            # Skip __pycache__ and other cache directories
            if "__pycache__" in str(py_file) or ".git" in str(py_file):
                continue

            try:
                result = self.parse_file(str(py_file))
                if (
                    result.total_nodes() > 0
                ):  # Only include files with translatable content
                    results[str(py_file)] = result
            except Exception as e:
                print(f"Warning: Failed to parse {py_file}: {e}")

        return results

    def reconstruct_file(self, parsed_file: ParsedCodeFile) -> str:
        """Reconstruct file content with translated comments/docstrings.

        Args:
            parsed_file: ParsedCodeFile with translations filled

        Returns:
            Reconstructed file content
        """
        lines = parsed_file.original_lines.copy()

        # Apply translations to inline comments
        for comment in parsed_file.comments:
            if comment.translated:
                line_idx = comment.line_number - 1
                if 0 <= line_idx < len(lines):
                    original_line = lines[line_idx]

                    # Find the comment part
                    comment_match = re.search(r"#\s*.+$", original_line)
                    if comment_match:
                        # Replace comment
                        before = original_line[: comment_match.start()]
                        lines[line_idx] = f"{before}# {comment.translated}\n"

        # Apply translations to docstrings
        for docstring in parsed_file.docstrings:
            if docstring.translated:
                # Find and replace docstring
                # This is more complex - would need to track exact position in AST
                # For now, we do a simple replacement
                content = "".join(lines)

                # Quote style detection
                if '"""' in content:
                    quote = '"""'
                else:
                    quote = "'''"

                # Replace first occurrence of original docstring
                original_quoted = f"{quote}{docstring.content}{quote}"
                translated_quoted = f"{quote}{docstring.translated}{quote}"

                content = content.replace(original_quoted, translated_quoted, 1)
                lines = content.splitlines(keepends=True)

        return "".join(lines)
