"""Code content lens for extracta - analyzes source code across multiple languages."""

import ast
import json
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..base_lens import BaseLens


class CodeLens(BaseLens):
    """Lens for extracting and analyzing source code files."""

    # Language detection by file extension
    LANGUAGE_EXTENSIONS = {
        "python": [".py", ".pyw", ".pyi"],
        "javascript": [".js", ".mjs", ".cjs"],
        "typescript": [".ts", ".tsx"],
        "html": [".html", ".htm", ".xhtml"],
        "css": [".css", ".scss", ".sass", ".less"],
        "php": [".php"],  # For WordPress themes/plugins
        "java": [".java"],
        "cpp": [".cpp", ".cc", ".cxx", ".c++", ".hpp", ".hxx"],
        "c": [".c", ".h"],
        "csharp": [".cs"],
        "ruby": [".rb"],
        "go": [".go"],
        "rust": [".rs"],
        "swift": [".swift"],
        "kotlin": [".kt"],
        "scala": [".scala"],
        "r": [".r", ".R"],
        "matlab": [".m"],
        "shell": [".sh", ".bash", ".zsh"],
        "sql": [".sql"],
        "yaml": [".yaml", ".yml"],
        "json": [".json"],
        "xml": [".xml"],
        "markdown": [".md", ".markdown"],
        "jupyter": [".ipynb"],  # Jupyter notebooks
    }

    # Reverse mapping for quick lookup
    EXTENSION_TO_LANGUAGE = {}
    for lang, exts in LANGUAGE_EXTENSIONS.items():
        for ext in exts:
            EXTENSION_TO_LANGUAGE[ext] = lang

    def __init__(
        self, enable_static_analysis: bool = True, enable_execution: bool = False
    ):
        """Initialize code lens.

        Args:
            enable_static_analysis: Whether to perform static analysis
            enable_execution: Whether to allow code execution (use with caution)
        """
        self.enable_static_analysis = enable_static_analysis
        self.enable_execution = enable_execution

    def extract(self, file_path: Path) -> Dict[str, Any]:
        """Extract code content and metadata."""
        try:
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"File not found: {file_path}",
                    "data": {},
                }

            # Detect language
            language = self._detect_language(file_path)

            # Read content
            content = self._read_file_content(file_path)

            # Basic metadata
            metadata = self._extract_metadata(file_path, content, language)

            # Language-specific analysis
            analysis = self._analyze_by_language(content, language, file_path)

            return {
                "success": True,
                "data": {
                    "content_type": "code",
                    "language": language,
                    "file_path": str(file_path),
                    "content": content,
                    "metadata": metadata,
                    "analysis": analysis,
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e), "data": {}}

    def _detect_language(self, file_path: Path) -> str:
        """Detect programming language from file extension and content."""
        # First try extension
        ext = file_path.suffix.lower()
        if ext in self.EXTENSION_TO_LANGUAGE:
            return self.EXTENSION_TO_LANGUAGE[ext]

        # Special case for Jupyter notebooks
        if file_path.suffix.lower() == ".ipynb":
            return "jupyter"

        # Fallback to content analysis (could be enhanced)
        return "unknown"

    def _read_file_content(self, file_path: Path) -> str:
        """Read file content with appropriate encoding."""
        try:
            # Try UTF-8 first
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Fallback to latin-1 for binary files that might be miscategorized
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    return f.read()
            except:
                return ""  # Can't read as text

    def _extract_metadata(
        self, file_path: Path, content: str, language: str
    ) -> Dict[str, Any]:
        """Extract basic metadata from code file."""
        lines = content.split("\n")
        total_lines = len(lines)

        # Count non-empty lines
        code_lines = sum(1 for line in lines if line.strip())

        # Estimate comment lines (basic heuristic)
        comment_lines = 0
        if language == "python":
            comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        elif language in [
            "javascript",
            "typescript",
            "java",
            "cpp",
            "c",
            "csharp",
            "php",
        ]:
            comment_lines = sum(
                1 for line in lines if line.strip().startswith(("//", "/*"))
            )

        return {
            "file_size": file_path.stat().st_size,
            "total_lines": total_lines,
            "code_lines": code_lines,
            "comment_lines": comment_lines,
            "blank_lines": total_lines - code_lines,
            "language": language,
        }

    def _analyze_by_language(
        self, content: str, language: str, file_path: Path
    ) -> Dict[str, Any]:
        """Perform language-specific analysis."""
        if language == "python":
            return self._analyze_python(content, file_path)
        elif language == "jupyter":
            return self._analyze_jupyter(content, file_path)
        elif language in ["javascript", "typescript"]:
            return self._analyze_javascript(content, file_path)
        elif language == "html":
            return self._analyze_html(content, file_path)
        elif language == "css":
            return self._analyze_css(content, file_path)
        elif language == "sql":
            return self._analyze_sql(content, file_path)
        else:
            # Generic analysis for unsupported languages
            return self._analyze_generic(content, language)

    def _analyze_python(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze Python code."""
        analysis = {
            "functions": [],
            "classes": [],
            "imports": [],
            "complexity": {},
            "style_issues": [],
        }

        if not self.enable_static_analysis:
            return analysis

        try:
            import ast

            tree = ast.parse(content, filename=str(file_path))

            # Extract functions and classes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis["functions"].append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "args": len(node.args.args),
                            "has_docstring": self._has_docstring(node),
                        }
                    )
                elif isinstance(node, ast.ClassDef):
                    analysis["classes"].append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "methods": len(
                                [n for n in node.body if isinstance(n, ast.FunctionDef)]
                            ),
                        }
                    )
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis["imports"].append(
                            {
                                "module": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno,
                            }
                        )
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        analysis["imports"].append(
                            {
                                "module": f"{node.module}.{alias.name}"
                                if node.module
                                else alias.name,
                                "alias": alias.asname,
                                "line": node.lineno,
                            }
                        )

            # Basic complexity analysis
            analysis["complexity"] = {
                "function_count": len(analysis["functions"]),
                "class_count": len(analysis["classes"]),
                "import_count": len(analysis["imports"]),
            }

        except SyntaxError as e:
            analysis["syntax_errors"] = [
                {
                    "line": e.lineno or 0,
                    "message": str(e),
                }
            ]

        return analysis

    def _analyze_jupyter(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze Jupyter notebook with delegation to other lenses."""
        analysis = {
            "cells": [],
            "metadata": {},
            "total_cells": 0,
            "code_cells": 0,
            "markdown_cells": 0,
            "delegated_analyses": {},
        }

        try:
            nb_data = json.loads(content)

            analysis["metadata"] = nb_data.get("metadata", {})
            cells = nb_data.get("cells", [])

            analysis["total_cells"] = len(cells)

            # Collect all code and markdown content for delegation
            all_code = []
            all_markdown = []

            for i, cell in enumerate(cells):
                cell_info = {
                    "index": i,
                    "type": cell.get("cell_type", "unknown"),
                    "lines": len(cell.get("source", [])),
                    "outputs": len(cell.get("outputs", []))
                    if cell.get("cell_type") == "code"
                    else 0,
                }

                if cell.get("cell_type") == "code":
                    analysis["code_cells"] += 1
                    code_content = "".join(cell.get("source", []))
                    all_code.append(code_content)
                    cell_info["functions"] = self._extract_functions_from_code(
                        code_content
                    )

                elif cell.get("cell_type") == "markdown":
                    analysis["markdown_cells"] += 1
                    markdown_content = "".join(cell.get("source", []))
                    all_markdown.append(markdown_content)

                analysis["cells"].append(cell_info)

            # Delegate to other lenses for comprehensive analysis
            if all_code:
                combined_code = "\n\n".join(all_code)
                analysis["delegated_analyses"]["code"] = self._analyze_python(
                    combined_code, file_path
                )

            if all_markdown:
                combined_markdown = "\n\n".join(all_markdown)
                # Could delegate to document_lens here
                analysis["delegated_analyses"]["markdown"] = {
                    "content": combined_markdown,
                    "word_count": len(combined_markdown.split()),
                    "sections": combined_markdown.count("#"),  # Count headers
                }

        except json.JSONDecodeError:
            analysis["parse_error"] = "Invalid JSON in notebook file"

        return analysis

    def _analyze_javascript(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code."""
        # Placeholder for JS/TS analysis
        return {
            "functions": self._extract_functions_js(content),
            "classes": [],  # Could be enhanced
            "imports": self._extract_imports_js(content),
            "note": "JavaScript/TypeScript analysis is basic - enhance with proper parser",
        }

    def _analyze_html(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze HTML content."""
        # Basic HTML analysis
        analysis = {
            "tags": {},
            "has_doctype": "<!DOCTYPE" in content.upper(),
            "has_title": "<title>" in content.lower(),
            "scripts": content.count("<script"),
            "styles": content.count("<style") + content.count("<link"),
        }

        # Count common tags
        import re

        tags = re.findall(r"<(\w+)", content.lower())
        for tag in tags:
            analysis["tags"][tag] = analysis["tags"].get(tag, 0) + 1

        return analysis

    def _analyze_css(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze CSS content."""
        # Basic CSS analysis
        analysis = {
            "selectors": len(re.findall(r"[^{}]+(?=\s*{)", content)),
            "properties": len(re.findall(r"[^:]+(?=\s*:)", content)),
            "rules": content.count("{"),
            "media_queries": content.count("@media"),
        }

        return analysis

    def _analyze_sql(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Analyze SQL content with basic parsing and structure analysis."""
        analysis = {
            "statements": [],
            "statement_types": {},
            "tables": set(),
            "columns": set(),
            "functions": set(),
            "joins": [],
            "conditions": [],
            "syntax_issues": [],
            "complexity_metrics": {},
            "security_concerns": [],
        }

        try:
            # Split content into individual statements
            statements = self._split_sql_statements(content)

            for stmt in statements:
                stmt_info = self._analyze_sql_statement(stmt.strip())
                if stmt_info:
                    # Convert sets to lists for JSON serialization
                    stmt_info["tables"] = list(stmt_info.get("tables", []))
                    stmt_info["columns"] = list(stmt_info.get("columns", []))
                    stmt_info["functions"] = list(stmt_info.get("functions", []))

                    analysis["statements"].append(stmt_info)

                    # Aggregate statistics
                    stmt_type = stmt_info.get("type", "unknown")
                    analysis["statement_types"][stmt_type] = (
                        analysis["statement_types"].get(stmt_type, 0) + 1
                    )

                    # Collect tables, columns, etc.
                    analysis["tables"].update(stmt_info.get("tables", []))
                    analysis["columns"].update(stmt_info.get("columns", []))
                    analysis["functions"].update(stmt_info.get("functions", []))
                    analysis["joins"].extend(stmt_info.get("joins", []))
                    analysis["conditions"].extend(stmt_info.get("conditions", []))

            # Convert sets to lists for JSON serialization
            analysis["tables"] = list(analysis["tables"])
            analysis["columns"] = list(analysis["columns"])
            analysis["functions"] = list(analysis["functions"])

            # Calculate complexity metrics
            analysis["complexity_metrics"] = {
                "total_statements": len(analysis["statements"]),
                "unique_tables": len(analysis["tables"]),
                "unique_columns": len(analysis["columns"]),
                "join_count": len(analysis["joins"]),
                "condition_count": len(analysis["conditions"]),
                "avg_statement_length": sum(
                    len(s.get("raw_sql", "")) for s in analysis["statements"]
                )
                / max(len(analysis["statements"]), 1),
            }

            # Basic security analysis
            analysis["security_concerns"] = self._analyze_sql_security(content)

        except Exception as e:
            analysis["parse_error"] = str(e)

        return analysis

    def _split_sql_statements(self, content: str) -> List[str]:
        """Split SQL content into individual statements."""
        # Remove comments first
        content = self._remove_sql_comments(content)

        # Split on semicolons, but be careful with semicolons in strings
        statements = []
        current_stmt = ""
        in_string = False
        string_char = None

        for char in content:
            if not in_string:
                if char in ("'", '"'):
                    in_string = True
                    string_char = char
                elif char == ";":
                    if current_stmt.strip():
                        statements.append(current_stmt.strip())
                    current_stmt = ""
                    continue
            else:
                if char == string_char and (
                    not current_stmt or current_stmt[-1] != "\\"
                ):
                    in_string = False
                    string_char = None

            current_stmt += char

        # Add final statement if exists
        if current_stmt.strip():
            statements.append(current_stmt.strip())

        return statements

    def _remove_sql_comments(self, content: str) -> str:
        """Remove SQL comments (both -- and /* */ style)."""
        # Remove single-line comments
        content = re.sub(r"--.*$", "", content, flags=re.MULTILINE)

        # Remove multi-line comments
        content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

        return content

    def _analyze_sql_statement(self, stmt: str) -> Optional[Dict[str, Any]]:
        """Analyze a single SQL statement."""
        if not stmt.strip():
            return None

        stmt_upper = stmt.upper()
        analysis = {
            "raw_sql": stmt,
            "type": "unknown",
            "tables": set(),
            "columns": set(),
            "functions": set(),
            "joins": [],
            "conditions": [],
        }

        # Determine statement type
        if stmt_upper.startswith("SELECT"):
            analysis["type"] = "select"
            self._analyze_select_statement(stmt, analysis)
        elif stmt_upper.startswith("INSERT"):
            analysis["type"] = "insert"
            self._analyze_insert_statement(stmt, analysis)
        elif stmt_upper.startswith("UPDATE"):
            analysis["type"] = "update"
            self._analyze_update_statement(stmt, analysis)
        elif stmt_upper.startswith("DELETE"):
            analysis["type"] = "delete"
            self._analyze_delete_statement(stmt, analysis)
        elif stmt_upper.startswith(
            ("CREATE TABLE", "CREATE TEMP TABLE", "CREATE TEMPORARY TABLE")
        ):
            analysis["type"] = "create_table"
            self._analyze_create_table_statement(stmt, analysis)
        elif stmt_upper.startswith("ALTER TABLE"):
            analysis["type"] = "alter_table"
            self._analyze_alter_table_statement(stmt, analysis)
        elif stmt_upper.startswith("DROP TABLE"):
            analysis["type"] = "drop_table"
            self._analyze_drop_table_statement(stmt, analysis)
        elif stmt_upper.startswith("CREATE INDEX"):
            analysis["type"] = "create_index"
        elif stmt_upper.startswith("CREATE VIEW"):
            analysis["type"] = "create_view"

        return analysis

    def _analyze_select_statement(self, stmt: str, analysis: Dict[str, Any]) -> None:
        """Analyze SELECT statement."""
        # Extract tables from FROM clause
        from_match = re.search(
            r"\bFROM\s+(.+?)(?:\bWHERE\b|\bGROUP\s+BY\b|\bORDER\s+BY\b|\bLIMIT\b|$)",
            stmt,
            re.IGNORECASE | re.DOTALL,
        )
        if from_match:
            from_clause = from_match.group(1)
            tables = self._extract_table_names(from_clause)
            analysis["tables"].update(tables)

        # Extract columns from SELECT clause
        select_match = re.search(
            r"\bSELECT\s+(.+?)\bFROM\b", stmt, re.IGNORECASE | re.DOTALL
        )
        if select_match:
            select_clause = select_match.group(1)
            columns = self._extract_column_names(select_clause)
            analysis["columns"].update(columns)

        # Extract JOINs
        join_pattern = r"\b(INNER\s+)?(?:LEFT|RIGHT|FULL|OUTER)?\s*JOIN\s+(\w+)"
        joins = re.findall(join_pattern, stmt, re.IGNORECASE)
        analysis["joins"].extend([join[1] for join in joins])

        # Extract WHERE conditions
        where_match = re.search(
            r"\bWHERE\s+(.+?)(?:\bGROUP\s+BY\b|\bORDER\s+BY\b|\bLIMIT\b|$)",
            stmt,
            re.IGNORECASE | re.DOTALL,
        )
        if where_match:
            where_clause = where_match.group(1)
            conditions = self._extract_conditions(where_clause)
            analysis["conditions"].extend(conditions)

        # Extract functions
        functions = self._extract_sql_functions(stmt)
        analysis["functions"].update(functions)

    def _analyze_insert_statement(self, stmt: str, analysis: Dict[str, Any]) -> None:
        """Analyze INSERT statement."""
        # Extract table name
        table_match = re.search(r"\bINSERT\s+INTO\s+(\w+)", stmt, re.IGNORECASE)
        if table_match:
            analysis["tables"].add(table_match.group(1))

        # Extract columns
        columns_match = re.search(r"\(\s*([^)]+)\s*\)", stmt)
        if columns_match:
            columns = self._extract_column_names(columns_match.group(1))
            analysis["columns"].update(columns)

    def _analyze_update_statement(self, stmt: str, analysis: Dict[str, Any]) -> None:
        """Analyze UPDATE statement."""
        # Extract table name
        table_match = re.search(r"\bUPDATE\s+(\w+)", stmt, re.IGNORECASE)
        if table_match:
            analysis["tables"].add(table_match.group(1))

        # Extract SET columns
        set_match = re.search(
            r"\bSET\s+(.+?)(?:\bWHERE\b|$)", stmt, re.IGNORECASE | re.DOTALL
        )
        if set_match:
            set_clause = set_match.group(1)
            columns = self._extract_column_names(set_clause)
            analysis["columns"].update(columns)

        # Extract WHERE conditions
        where_match = re.search(r"\bWHERE\s+(.+?)$", stmt, re.IGNORECASE | re.DOTALL)
        if where_match:
            conditions = self._extract_conditions(where_match.group(1))
            analysis["conditions"].extend(conditions)

    def _analyze_delete_statement(self, stmt: str, analysis: Dict[str, Any]) -> None:
        """Analyze DELETE statement."""
        # Extract table name
        table_match = re.search(r"\bDELETE\s+FROM\s+(\w+)", stmt, re.IGNORECASE)
        if table_match:
            analysis["tables"].add(table_match.group(1))

        # Extract WHERE conditions
        where_match = re.search(r"\bWHERE\s+(.+?)$", stmt, re.IGNORECASE | re.DOTALL)
        if where_match:
            conditions = self._extract_conditions(where_match.group(1))
            analysis["conditions"].extend(conditions)

    def _analyze_create_table_statement(
        self, stmt: str, analysis: Dict[str, Any]
    ) -> None:
        """Analyze CREATE TABLE statement."""
        # Extract table name
        table_match = re.search(
            r"\bCREATE\s+(?:TEMP\s+)?TABLE\s+(\w+)", stmt, re.IGNORECASE
        )
        if table_match:
            analysis["tables"].add(table_match.group(1))

        # Extract column definitions
        columns_match = re.search(r"\(\s*(.+)\s*\)", stmt, re.DOTALL)
        if columns_match:
            column_defs = columns_match.group(1)
            # Extract column names (simplified)
            column_names = re.findall(r"(\w+)\s+[\w\s()]+(?:,|$)", column_defs)
            analysis["columns"].update(column_names)

    def _analyze_alter_table_statement(
        self, stmt: str, analysis: Dict[str, Any]
    ) -> None:
        """Analyze ALTER TABLE statement."""
        # Extract table name
        table_match = re.search(r"\bALTER\s+TABLE\s+(\w+)", stmt, re.IGNORECASE)
        if table_match:
            analysis["tables"].add(table_match.group(1))

    def _analyze_drop_table_statement(
        self, stmt: str, analysis: Dict[str, Any]
    ) -> None:
        """Analyze DROP TABLE statement."""
        # Extract table name
        table_match = re.search(r"\bDROP\s+TABLE\s+(\w+)", stmt, re.IGNORECASE)
        if table_match:
            analysis["tables"].add(table_match.group(1))

    def _extract_table_names(self, clause: str) -> List[str]:
        """Extract table names from SQL clause."""
        # Simple extraction - could be enhanced for aliases, subqueries, etc.
        tables = re.findall(r"\b(\w+)\b", clause)
        # Filter out SQL keywords
        sql_keywords = {
            "SELECT",
            "FROM",
            "WHERE",
            "JOIN",
            "INNER",
            "LEFT",
            "RIGHT",
            "FULL",
            "OUTER",
            "ON",
            "GROUP",
            "BY",
            "ORDER",
            "HAVING",
            "LIMIT",
            "AS",
            "AND",
            "OR",
            "NOT",
            "IN",
            "IS",
            "NULL",
            "LIKE",
            "BETWEEN",
        }
        return [
            table
            for table in tables
            if table.upper() not in sql_keywords and len(table) > 1
        ]

    def _extract_column_names(self, clause: str) -> List[str]:
        """Extract column names from SQL clause."""
        # Extract identifiers that could be columns
        columns = re.findall(r"\b(\w+)\b", clause)
        # Filter out SQL keywords and functions
        sql_keywords = {
            "SELECT",
            "FROM",
            "WHERE",
            "AS",
            "AND",
            "OR",
            "NOT",
            "IN",
            "IS",
            "NULL",
            "LIKE",
            "BETWEEN",
            "COUNT",
            "SUM",
            "AVG",
            "MIN",
            "MAX",
            "DISTINCT",
            "ALL",
        }
        return [
            col for col in columns if col.upper() not in sql_keywords and len(col) > 1
        ]

    def _extract_conditions(self, clause: str) -> List[str]:
        """Extract WHERE conditions."""
        # Simple extraction of comparison conditions
        conditions = re.findall(r'\w+\s*[=<>!]+\s*[\'"\w]+', clause)
        return conditions

    def _extract_sql_functions(self, stmt: str) -> List[str]:
        """Extract SQL function calls."""
        # Common SQL functions
        functions = re.findall(
            r"\b(COUNT|SUM|AVG|MIN|MAX|CONCAT|SUBSTRING|DATE|NOW|CURRENT_TIMESTAMP|COALESCE|NULLIF)\s*\(",
            stmt,
            re.IGNORECASE,
        )
        return list(set(functions))

    def _analyze_sql_security(self, content: str) -> List[str]:
        """Basic SQL security analysis."""
        concerns = []

        # Check for potential SQL injection patterns (in application code, not SQL)
        if "SELECT" in content.upper() and (
            "+" in content or "format(" in content.lower()
        ):
            concerns.append(
                "Potential string concatenation in SELECT - consider parameterized queries"
            )

        # Check for dangerous operations
        dangerous_patterns = [
            (r"\bDROP\s+DATABASE\b", "DROP DATABASE statement found"),
            (r"\bTRUNCATE\s+TABLE\b", "TRUNCATE TABLE can be dangerous"),
            (
                r"\bDELETE\s+FROM\s+\w+\s+WHERE\s+1\s*=\s*1",
                "DELETE without specific WHERE clause",
            ),
        ]

        for pattern, message in dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                concerns.append(message)

        return concerns

    def _analyze_generic(self, content: str, language: str) -> Dict[str, Any]:
        """Generic analysis for unsupported languages."""
        return {
            "language": language,
            "line_count": len(content.split("\n")),
            "character_count": len(content),
            "note": f"Generic analysis only - {language} support not implemented",
        }

    # Helper methods
    def _has_docstring(self, node) -> bool:
        """Check if a function/class has a docstring."""
        if not node.body:
            return False
        first_stmt = node.body[0]
        # Check for docstring (Python 3.8+ uses ast.Constant)
        if not isinstance(first_stmt, ast.Expr):
            return False

        if isinstance(first_stmt.value, ast.Constant) and isinstance(
            first_stmt.value.value, str
        ):
            return True

        return False

        # Try ast.Constant first (Python 3.8+)
        if isinstance(first_stmt.value, ast.Constant) and isinstance(
            first_stmt.value.value, str
        ):
            return True

        # Fallback for older Python versions
        try:
            return isinstance(first_stmt.value, ast.Str)
        except AttributeError:
            return False

    def _extract_functions_from_code(self, code: str) -> List[Dict[str, Any]]:
        """Extract function definitions from code string."""
        functions = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "args": len(node.args.args),
                        }
                    )
        except:
            pass
        return functions

    def _extract_functions_js(self, content: str) -> List[Dict[str, Any]]:
        """Basic JavaScript function extraction."""
        functions = []
        # Simple regex-based extraction (could be enhanced with proper JS parser)
        import re

        func_matches = re.findall(r"function\s+(\w+)\s*\([^)]*\)", content)
        for func in func_matches:
            functions.append({"name": func, "type": "function"})
        return functions

    def _extract_imports_js(self, content: str) -> List[Dict[str, Any]]:
        """Basic JavaScript import extraction."""
        imports = []
        import re

        # ES6 imports
        es6_matches = re.findall(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', content)
        for module in es6_matches:
            imports.append({"module": module, "type": "es6"})

        # CommonJS requires
        cjs_matches = re.findall(
            r'(?:const|let|var)\s+\w+\s*=\s*require\([\'"]([^\'"]+)[\'"]\)', content
        )
        for module in cjs_matches:
            imports.append({"module": module, "type": "commonjs"})

        return imports
