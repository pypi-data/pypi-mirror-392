"""
Read tool implementation for extracting windowed text spans from files.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Dict, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import FileSpan, CandidateMatch


class ReadTool:
    """Implements file reading with context windows and span extraction."""

    def __init__(self, max_file_size: Optional[int] = None, ignore_file: Optional[str] = None):
        self.max_file_size = max_file_size or int(os.getenv('READ_MAX_FILE_SIZE', '5048576'))  # 5MB default from env
        self.ignore_file = ignore_file or self._find_ignore_file()
        self.ignore_patterns = self._load_ignore_patterns()

    def _find_ignore_file(self) -> Optional[str]:
        """Find the ignore file to use for read operations."""
        # FIRST: Check for bundled .rgignore in package directory
        package_dir = Path(__file__).parent.parent  # Go up to op-grep root
        bundled_rgignore = package_dir / '.rgignore'
        if bundled_rgignore.exists():
            return str(bundled_rgignore)
        
        # SECOND: Look for .rgignore in search directory and parent directories
        current_dir = Path.cwd()

        while current_dir != current_dir.parent:
            rgignore_path = current_dir / '.rgignore'
            if rgignore_path.exists():
                return str(rgignore_path)
            current_dir = current_dir.parent

        # THIRD: Also check for .gitignore as fallback
        current_dir = Path.cwd()
        while current_dir != current_dir.parent:
            gitignore_path = current_dir / '.gitignore'
            if gitignore_path.exists():
                return str(gitignore_path)
            current_dir = current_dir.parent

        return None

    def _load_ignore_patterns(self) -> List[str]:
        """Load ignore patterns from the ignore file."""
        patterns = []
        if self.ignore_file and os.path.exists(self.ignore_file):
            try:
                with open(self.ignore_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and comments
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except (OSError, UnicodeDecodeError):
                pass
        return patterns

    def _should_ignore_file(self, file_path: str) -> bool:
        """Check if a file should be ignored based on ignore patterns."""
        import fnmatch

        # Check against ignore patterns
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
            # Also check if any parent directory matches the pattern
            parts = Path(file_path).parts
            for i in range(len(parts)):
                path_part = '/'.join(parts[i:])
                if fnmatch.fnmatch(path_part, pattern):
                    return True
        return False

    def read_file(
        self,
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None,
        window_size: Optional[int] = None,
        encoding: str = "utf-8"
    ) -> FileSpan:
        """
        Read a file or a specific span within a file.

        Args:
            file_path: Path to the file
            start_line: Starting line number (1-based, inclusive)
            end_line: Ending line number (1-based, inclusive)
            window_size: Context window size around the specified lines
            encoding: File encoding

        Returns:
            FileSpan object with the requested content
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check if file should be ignored
        if self._should_ignore_file(file_path):
            raise ValueError(f"File is ignored by ignore patterns: {file_path}")

        if os.path.getsize(file_path) > self.max_file_size:
            raise ValueError(f"File too large: {file_path}")

        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            lines = f.readlines()

        # Adjust line numbers for 0-based indexing
        if start_line is not None:
            start_idx = max(0, start_line - 1)
        else:
            start_idx = 0

        if end_line is not None:
            end_idx = min(len(lines), end_line)
        else:
            end_idx = min(len(lines), start_line + window_size + 1 if start_line is not None and window_size is not None else len(lines))

        # Apply window size if specified
        if window_size is not None and start_line is not None:
            start_idx = max(0, start_idx - window_size)
            end_idx = min(len(lines), start_line + window_size + 1)

        # Extract the relevant lines
        selected_lines = lines[start_idx:end_idx]
        content = ''.join(selected_lines).rstrip()

        # Calculate actual line numbers for the span
        actual_start_line = start_idx + 1
        actual_end_line = start_idx + len(selected_lines)

        return FileSpan(
            path=file_path,
            start_line=actual_start_line,
            end_line=actual_end_line,
            text=content
        )

    def read_spans_from_candidates(
        self,
        candidates: List[CandidateMatch],
        window_size: Optional[int] = None,
        max_spans: Optional[int] = None
    ) -> List[FileSpan]:
        """
        Convert CandidateMatch objects to FileSpan objects with context.

        OPTIMIZED: Uses concurrent file reading for better performance.

        Args:
            candidates: List of CandidateMatch objects
            window_size: Number of context lines around each match
            max_spans: Maximum number of spans to return

        Returns:
            List of FileSpan objects
        """
        # Environment variable is primary source, passed parameter is override only if explicitly provided
        window_size = window_size if window_size is not None else int(os.getenv('CONTEXT_WINDOW_SIZE', '3'))
        max_spans = max_spans if max_spans is not None else int(os.getenv('READ_MAX_SPANS', '500'))

        # Filter and limit candidates first
        unique_candidates = []
        seen_files = set()

        for candidate in candidates:
            if len(unique_candidates) >= max_spans:
                break

            file_path = candidate.path
            # Skip duplicate files
            if file_path in seen_files:
                continue
            # Skip ignored files
            if self._should_ignore_file(file_path):
                continue

            unique_candidates.append(candidate)
            seen_files.add(file_path)

        # Use concurrent file reading for better performance
        spans = []
        # OPTIMIZED: Dynamic scaling based on CPU cores for I/O-bound tasks
        cpu_count = os.cpu_count() or 4
        # For I/O-bound file reading, use 4x CPU cores but respect configured limits
        optimal_workers = min(cpu_count * 4, int(os.getenv('READ_MAX_WORKERS', '64')))
        max_workers = min(len(unique_candidates), optimal_workers)

        if max_workers == 0:
            return spans

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all file reading tasks
            future_to_candidate = {
                executor.submit(
                    self._read_candidate_file,
                    candidate,
                    window_size
                ): candidate
                for candidate in unique_candidates
            }

            # Collect results as they complete
            for future in as_completed(future_to_candidate):
                try:
                    span = future.result()
                    if span:
                        spans.append(span)
                except (FileNotFoundError, ValueError, Exception):
                    # Skip files that can't be read
                    continue

        # Return spans in original order for consistency
        return spans[:max_spans]

    def _read_candidate_file(
        self,
        candidate: CandidateMatch,
        window_size: int
    ) -> Optional[FileSpan]:
        """
        Helper method to read a single candidate file.
        Separated for better concurrency handling.
        """
        try:
            return self.read_file(
                file_path=candidate.path,
                start_line=candidate.line_number,
                end_line=None,
                window_size=window_size
            )
        except (FileNotFoundError, ValueError, Exception):
            return None

    def read_multiple_files(
        self,
        file_paths: List[str],
        max_lines_per_file: Optional[int] = None,
        encoding: str = "utf-8"
    ) -> List[FileSpan]:
        """
        Read multiple files, taking the first N lines from each.

        Args:
            file_paths: List of file paths to read
            max_lines_per_file: Maximum number of lines to read per file
            encoding: Default encoding

        Returns:
            List of FileSpan objects
        """
        spans = []
        max_lines_per_file = max_lines_per_file or int(os.getenv('READ_MAX_LINES_PER_FILE', '100'))

        for file_path in file_paths:
            # Skip ignored files silently
            if self._should_ignore_file(file_path):
                continue
            try:
                span = self.read_file(
                    file_path=file_path,
                    start_line=1,
                    end_line=max_lines_per_file,
                    encoding=encoding
                )
                spans.append(span)
            except (FileNotFoundError, ValueError):
                # Skip files that can't be read
                continue

        return spans

    def search_and_read(
        self,
        file_path: str,
        search_terms: List[str],
        context_lines: Optional[int] = None,
        case_sensitive: bool = False
    ) -> List[FileSpan]:
        """
        Search for terms in a file and return matching spans with context.

        Args:
            file_path: Path to the file
            search_terms: List of terms to search for
            context_lines: Number of context lines around matches
            case_sensitive: Whether search should be case sensitive

        Returns:
            List of FileSpan objects containing matches
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        matches = []
        context_lines = context_lines or int(os.getenv('READ_CONTEXT_LINES', '10'))

        for line_num, line in enumerate(lines, 1):
            line_text = line.strip()
            search_text = line_text if case_sensitive else line_text.lower()

            for term in search_terms:
                search_term = term if case_sensitive else term.lower()

                if search_term in search_text:
                    # Calculate context window
                    start_line = max(1, line_num - context_lines)
                    end_line = min(len(lines), line_num + context_lines)

                    # Create span
                    span = self.read_file(
                        file_path=file_path,
                        start_line=start_line,
                        end_line=end_line
                    )
                    matches.append(span)
                    break  # Move to next line after finding first match

        return matches

    def get_file_metadata(self, file_path: str) -> Dict[str, Union[str, int, float]]:
        """
        Get metadata about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file metadata
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        stat = os.stat(file_path)
        path_obj = Path(file_path)

        return {
            "path": file_path,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "extension": path_obj.suffix,
            "name": path_obj.name,
            "is_binary": self._is_binary_file(file_path)
        }

    def _is_binary_file(self, file_path: str, sample_size: Optional[int] = None) -> bool:
        """
        Check if a file is binary by reading a sample.

        Args:
            file_path: Path to the file
            sample_size: Number of bytes to sample

        Returns:
            True if the file appears to be binary
        """
        sample_size = sample_size or int(os.getenv('READ_BINARY_SAMPLE_SIZE', '1024'))
        with open(file_path, 'rb') as f:
            sample = f.read(sample_size)
            return b'\0' in sample  # Null bytes indicate binary

    def extract_function_or_class(
        self,
        file_path: str,
        target_name: str,
        language: str = "auto"
    ) -> Optional[FileSpan]:
        """
        Extract a specific function or class from a file.

        Args:
            file_path: Path to the file
            target_name: Name of the function or class to extract
            language: Programming language (affects parsing logic). Use "auto" for auto-detection.

        Returns:
            FileSpan containing the function/class, or None if not found
        """
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        # Auto-detect language if not specified
        if language == "auto":
            language = self._detect_language_from_path(file_path)

        # Dispatch to appropriate language handler
        language = language.lower()
        if language == "python":
            return self._extract_python_definition(lines, target_name)
        elif language == "javascript" or language == "js":
            return self._extract_javascript_definition(lines, target_name)
        elif language == "typescript" or language == "ts":
            return self._extract_typescript_definition(lines, target_name)
        elif language == "java":
            return self._extract_java_definition(lines, target_name)
        elif language == "go" or language == "golang":
            return self._extract_go_definition(lines, target_name)
        elif language == "rust" or language == "rs":
            return self._extract_rust_definition(lines, target_name)
        elif language == "cpp" or language == "c++" or language == "c":
            return self._extract_cpp_definition(lines, target_name)
        elif language == "php":
            return self._extract_php_definition(lines, target_name)
        elif language == "ruby" or language == "rb":
            return self._extract_ruby_definition(lines, target_name)
        elif language == "csharp" or language == "c#" or language == "cs":
            return self._extract_csharp_definition(lines, target_name)
        else:
            # Fallback to simple text search for unsupported languages
            return self._extract_generic_definition(lines, target_name, language)

    def _extract_python_definition(self, lines: List[str], target_name: str) -> Optional[FileSpan]:
        """Extract Python function or class definition."""
        import re

        # Look for function or class definitions
        pattern = re.compile(rf'^\s*(def|class)\s+{re.escape(target_name)}\s*\(')

        for i, line in enumerate(lines):
            if pattern.match(line):
                # Find the end of the definition by detecting de-dentation
                start_line = i + 1
                base_indent = len(line) - len(line.lstrip())

                # Look for the end of the block
                end_line = len(lines)
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) <= base_indent:
                        if not lines[j].strip().startswith('#'):  # Ignore comments
                            end_line = j + 1
                            break

                return FileSpan(
                    path="",  # Will be filled by caller
                    start_line=start_line,
                    end_line=end_line,
                    text=''.join(lines[start_line - 1:end_line - 1]).rstrip()
                )

        return None

    def _detect_language_from_path(self, file_path: str) -> str:
        """Auto-detect programming language from file path."""
        path = Path(file_path)
        extension = path.suffix.lower()

        # Language mapping from extensions
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.mjs': 'javascript',
            '.cjs': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.go': 'go',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.cxx': 'cpp',
            '.cc': 'cpp',
            '.c': 'c',
            '.h': 'cpp',
            '.hpp': 'cpp',
            '.php': 'php',
            '.rb': 'ruby',
            '.cs': 'csharp',
            '.vb': 'csharp',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.rs': 'rust',
            '.dart': 'dart',
            '.lua': 'lua',
            '.r': 'r',
            '.m': 'objective-c',
            '.sh': 'shell',
            '.sql': 'sql',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.less': 'less',
            '.xml': 'xml',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.toml': 'toml',
        }

        return extension_map.get(extension, 'unknown')

    def _extract_javascript_definition(self, lines: List[str], target_name: str) -> Optional[FileSpan]:
        """Extract JavaScript function or class definition."""
        import re

        # Multiple function patterns in JavaScript
        patterns = [
            rf'^\s*function\s+{re.escape(target_name)}\s*\([^)]*\)\s*\{{',
            rf'^\s*const\s+{re.escape(target_name)}\s*=\s*(?:async\s+)?\([^)]*\)\s*=>\s*\{{',
            rf'^\s*const\s+{re.escape(target_name)}\s*=\s*(?:async\s+)?function\s*\([^)]*\)',
            rf'^\s*let\s+{re.escape(target_name)}\s*=\s*(?:async\s+)?\([^)]*\)\s*=>\s*\{{',
            rf'^\s*var\s+{re.escape(target_name)}\s*=\s*(?:async\s+)?function\s*\([^)]*\)',
            rf'^\s*{re.escape(target_name)}\s*:\s*(?:async\s+)?function\s*\([^)]*\)',
            rf'^\s*class\s+{re.escape(target_name)}\b',
            rf'^\s*{re.escape(target_name)}\s*=\s*\{{',  # Object method
        ]

        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.search(pattern, line):
                    return self._extract_bracket_block(lines, i, target_name)

        return None

    def _extract_typescript_definition(self, lines: List[str], target_name: str) -> Optional[FileSpan]:
        """Extract TypeScript function or class definition."""
        import re

        patterns = [
            rf'^\s*function\s+{re.escape(target_name)}\s*\([^)]*\)\s*:',
            rf'^\s*(?:public|private|protected)?\s*(?:static)?\s*(?:async)?\s*{re.escape(target_name)}\s*\([^)]*\)\s*:',
            rf'^\s*const\s+{re.escape(target_name)}\s*=\s*(?:async\s+)?\([^)]*\)\s*=>\s*',
            rf'^\s*class\s+{re.escape(target_name)}\b',
            rf'^\s*interface\s+{re.escape(target_name)}\b',
            rf'^\s*type\s+{re.escape(target_name)}\s*=',
            rf'^\s*(?:export\s+)?(?:default\s+)?class\s+{re.escape(target_name)}',
        ]

        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.search(pattern, line):
                    return self._extract_bracket_block(lines, i, target_name)

        return None

    def _extract_java_definition(self, lines: List[str], target_name: str) -> Optional[FileSpan]:
        """Extract Java method or class definition."""
        import re

        patterns = [
            rf'^\s*(?:public|private|protected)?\s*(?:static)?\s*(?:final|abstract|synchronized)?\s*(?:\w+\s+)?{re.escape(target_name)}\s*\([^)]*\)',
            rf'^\s*(?:public|private|protected)?\s*(?:static)?\s*(?:final|abstract)?\s*class\s+{re.escape(target_name)}',
            rf'^\s*(?:public|private|protected)?\s*interface\s+{re.escape(target_name)}',
            rf'^\s*(?:public|private|protected)?\s*enum\s+{re.escape(target_name)}',
        ]

        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.search(pattern, line):
                    return self._extract_bracket_block(lines, i, target_name)

        return None

    def _extract_go_definition(self, lines: List[str], target_name: str) -> Optional[FileSpan]:
        """Extract Go function definition."""
        import re

        patterns = [
            rf'^\s*func\s+(?:\([^)]*\)\s+)?{re.escape(target_name)}\s*\([^)]*\)(?:\s*[^{{]*)?\s*\{{',
            rf'^\s*type\s+{re.escape(target_name)}\s+(?:struct|interface)',
        ]

        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.search(pattern, line):
                    return self._extract_bracket_block(lines, i, target_name)

        return None

    def _extract_rust_definition(self, lines: List[str], target_name: str) -> Optional[FileSpan]:
        """Extract Rust function or struct definition."""
        import re

        patterns = [
            rf'^\s*(?:pub\s+)?(?:async\s+)?(?:unsafe\s+)?fn\s+{re.escape(target_name)}\s*\([^)]*\)(?:\s*->\s*\w+)?',
            rf'^\s*(?:pub\s+)?struct\s+{re.escape(target_name)}',
            r'^\s*(?:pub\s+)?impl\s+.*\s+\{[^}]*\bfn\s+' + re.escape(target_name),
            rf'^\s*(?:pub\s+)?trait\s+{re.escape(target_name)}',
            rf'^\s*(?:pub\s+)?enum\s+{re.escape(target_name)}',
        ]

        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.search(pattern, line):
                    return self._extract_bracket_block(lines, i, target_name)

        return None

    def _extract_cpp_definition(self, lines: List[str], target_name: str) -> Optional[FileSpan]:
        """Extract C++ function or class definition."""
        import re

        patterns = [
            rf'^\s*(?:\w+\s+)*{re.escape(target_name)}\s*\([^)]*\)(?:\s*const)?\s*(?:override\s+)?(?:final\s+)?\{{',
            rf'^\s*(?:virtual\s+)?{re.escape(target_name)}\s*\([^)]*\)(?:\s*=\s*0)?',
            rf'^\s*class\s+{re.escape(target_name)}',
            rf'^\s*struct\s+{re.escape(target_name)}',
            rf'^\s*(?:template\s*<[^>]*>\s*)?class\s+{re.escape(target_name)}',
            rf'^\s*(?:template\s*<[^>]*>\s*)?struct\s+{re.escape(target_name)}',
        ]

        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.search(pattern, line):
                    return self._extract_bracket_block(lines, i, target_name)

        return None

    def _extract_php_definition(self, lines: List[str], target_name: str) -> Optional[FileSpan]:
        """Extract PHP function or class definition."""
        import re

        patterns = [
            rf'^\s*function\s+{re.escape(target_name)}\s*\([^)]*\)',
            rf'^\s*(?:public|private|protected)?\s*(?:static)?\s*function\s+{re.escape(target_name)}\s*\([^)]*\)',
            rf'^\s*class\s+{re.escape(target_name)}',
            rf'^\s*interface\s+{re.escape(target_name)}',
            rf'^\s*trait\s+{re.escape(target_name)}',
        ]

        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.search(pattern, line):
                    return self._extract_bracket_block(lines, i, target_name)

        return None

    def _extract_ruby_definition(self, lines: List[str], target_name: str) -> Optional[FileSpan]:
        """Extract Ruby method or class definition."""
        import re

        patterns = [
            rf'^\s*def\s+(?:self\.)?{re.escape(target_name)}',
            rf'^\s*class\s+{re.escape(target_name)}',
            rf'^\s*module\s+{re.escape(target_name)}',
            rf'^\s*(?:private|protected|public)\s*:.*\ndef\s+{re.escape(target_name)}',
        ]

        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.search(pattern, line):
                    return self._extract_indentation_block(lines, i, target_name)

        return None

    def _extract_csharp_definition(self, lines: List[str], target_name: str) -> Optional[FileSpan]:
        """Extract C# method or class definition."""
        import re

        patterns = [
            rf'^\s*(?:public|private|protected|internal)?\s*(?:static)?\s*(?:async)?\s*(?:virtual|override|abstract)?\s*\w+\s+{re.escape(target_name)}\s*\([^)]*\)',
            rf'^\s*(?:public|private|protected|internal)?\s*(?:static)?\s*(?:abstract)?\s*class\s+{re.escape(target_name)}',
            rf'^\s*(?:public|private|protected|internal)?\s*interface\s+{re.escape(target_name)}',
            rf'^\s*(?:public|private|protected|internal)?\s*struct\s+{re.escape(target_name)}',
            rf'^\s*(?:public|private|protected|internal)?\s*enum\s+{re.escape(target_name)}',
        ]

        for i, line in enumerate(lines):
            for pattern in patterns:
                if re.search(pattern, line):
                    return self._extract_bracket_block(lines, i, target_name)

        return None

    def _extract_generic_definition(self, lines: List[str], target_name: str, language: str) -> Optional[FileSpan]:
        """Generic fallback for unsupported languages."""
        for i, line in enumerate(lines):
            if target_name in line:
                # Return a span around the match
                window = int(os.getenv('READ_GENERIC_WINDOW_SIZE', '10'))
                start_line = max(1, i + 1 - window)
                end_line = min(len(lines), i + 1 + window)
                return self.read_file("", start_line, end_line)
        return None

    def _extract_bracket_block(self, lines: List[str], start_idx: int, target_name: str) -> Optional[FileSpan]:
        """Extract a code block defined by curly braces."""
        # Find the opening brace
        start_line = start_idx + 1
        base_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())

        # Look for the opening brace
        brace_count = 0
        for j in range(start_idx, len(lines)):
            if '{' in lines[j]:
                brace_count += lines[j].count('{')
                if brace_count > 0:
                    start_line = j + 1
                    break

        # Find the matching closing brace
        end_line = len(lines)
        for j in range(start_line - 1, len(lines)):
            brace_count += lines[j].count('{')
            brace_count -= lines[j].count('}')
            if brace_count == 0:
                end_line = j + 1
                break

        return FileSpan(
            path="",  # Will be filled by caller
            start_line=start_line,
            end_line=end_line,
            text=''.join(lines[start_line - 1:end_line - 1]).rstrip()
        )

    def _extract_indentation_block(self, lines: List[str], start_idx: int, target_name: str) -> Optional[FileSpan]:
        """Extract a code block defined by indentation (for Python, Ruby, etc.)."""
        start_line = start_idx + 1
        base_indent = len(lines[start_idx]) - len(lines[start_idx].lstrip())

        # Look for the end of the block by detecting de-dentation
        end_line = len(lines)
        for j in range(start_idx + 1, len(lines)):
            if lines[j].strip() and len(lines[j]) - len(lines[j].lstrip()) <= base_indent:
                if not lines[j].strip().startswith('#'):  # Ignore comments
                    end_line = j + 1
                    break

        return FileSpan(
            path="",  # Will be filled by caller
            start_line=start_line,
            end_line=end_line,
            text=''.join(lines[start_line - 1:end_line - 1]).rstrip()
        )