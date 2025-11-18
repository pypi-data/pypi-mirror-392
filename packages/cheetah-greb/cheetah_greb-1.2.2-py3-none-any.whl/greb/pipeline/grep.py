"""
Grep tool implementation using ripgrep for fast text search.
"""

from __future__ import annotations

import os
import re
import subprocess
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

from .base import CandidateMatch


class GrepTool:
    """Implements fast text search using ripgrep."""

    def __init__(self, max_results: Optional[int] = None, ignore_file: Optional[str] = None):
        self.max_results = max_results or int(os.getenv('MAX_GREP_RESULTS', '10000'))
        self.rg_command = self._find_rg_command()
        self.ignore_file = ignore_file or self._find_ignore_file()

    def _find_ignore_file(self) -> Optional[str]:
        """Find the ignore file to use for ripgrep."""
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

    def _find_rg_command(self) -> str:
        """Find bundled ripgrep executable in the package."""
        import platform
        import os
        from pathlib import Path

        # Use bundled ripgrep binary
        package_dir = Path(__file__).parent.parent
        system = platform.system().lower()
        machine = platform.machine().lower()

        # Determine the right binary path based on platform
        if system == "windows":
            rg_path = package_dir / "binaries" / "rg.exe"
        elif system == "darwin":  # macOS
            if machine in ["arm64", "aarch64"]:
                rg_path = package_dir / "binaries" / "rg-darwin-arm64"
            else:
                rg_path = package_dir / "binaries" / "rg-darwin-amd64"
        elif system == "linux":
            rg_path = package_dir / "binaries" / "rg-linux-amd64"
        else:
            raise RuntimeError(f"Unsupported platform: {system}")

        if not rg_path.exists():
            raise RuntimeError(
                f"Bundled ripgrep not found at {rg_path}. "
                f"Please reinstall the cheetah-grep package."
            )

        # Make executable on Unix systems
        if system != "windows":
            os.chmod(rg_path, 0o755)

        # Test if it works
        try:
            result = subprocess.run(
                [str(rg_path), "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=False
            )
            if result.returncode == 0:
                              return str(rg_path)
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError) as e:
            raise RuntimeError(
                f"Bundled ripgrep failed to execute: {e}. "
                f"Please reinstall the cheetah-grep package."
            )

        raise RuntimeError(
            f"Bundled ripgrep at {rg_path} is not working. "
            f"Please reinstall the cheetah-grep package."
        )

    def search(
        self,
        query: str,
        directory: Optional[str] = None,
        file_patterns: Optional[List[str]] = None,
        case_sensitive: bool = False,
        context_lines: int = 2
    ) -> List[CandidateMatch]:
        """
        Search for a query string in files using ripgrep.

        Args:
            query: The search query string
            directory: Directory to search in (default: current directory)
            file_patterns: File patterns to include (e.g., ["*.py", "*.ts"])
            case_sensitive: Whether to perform case-sensitive search
            context_lines: Number of context lines around matches

        Returns:
            List of CandidateMatch objects
        """
        return self._search_with_ripgrep(query, directory, file_patterns, case_sensitive, context_lines)

    def _search_with_ripgrep(
        self,
        query: str,
        directory: Optional[str] = None,
        file_patterns: Optional[List[str]] = None,
        case_sensitive: bool = False,
        context_lines: int = 2
    ) -> List[CandidateMatch]:
        """Search using ripgrep when available."""
        cmd = [self.rg_command, "--json", "--no-heading", "--line-number"]

        # Add context lines
        if context_lines > 0:
            cmd.extend(["--context", str(context_lines)])

        # Add case sensitivity
        if case_sensitive:
            cmd.append("--case-sensitive")
        else:
            cmd.append("--ignore-case")

        # Add ignore file if found
        if self.ignore_file:
            cmd.extend(["--ignore-file", self.ignore_file])

        # Add file patterns
        if file_patterns:
            for pattern in file_patterns:
                cmd.extend(["--glob", pattern])

        # Add max results limit
        cmd.extend(["--max-count", str(self.max_results)])

        # Add query
        cmd.append(query)

        # Add directory
        if directory:
            cmd.append(directory)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )

            if result.returncode != 0 and result.returncode != 1:
                # Return code 1 means no matches found, which is OK
                raise RuntimeError(f"ripgrep failed: {result.stderr}")

            return self._parse_rg_output(result.stdout)

        except subprocess.TimeoutExpired:
            raise RuntimeError("Search timed out after 30 seconds")

    
    def _parse_rg_output(self, output: Optional[str]) -> List[CandidateMatch]:
        """Parse ripgrep JSON output into CandidateMatch objects."""
        matches = []

        if not output or not output.strip():
            return matches

        # Track context for each match
        context_buffer: Dict[str, List[Dict[str, Any]]] = {}

        for line in output.strip().split('\n'):
            try:
                import json
                data = json.loads(line)

                if data.get("type") == "match":
                    path = data["data"]["path"]["text"]
                    line_number = data["data"]["line_number"]
                    matched_text = data["data"]["lines"]["text"].strip()

                    # Get context from buffer if available
                    context_before = ""
                    context_after = ""

                    if path in context_buffer:
                        context_items = context_buffer[path]
                        for item in context_items:
                            if item["line_number"] < line_number:
                                context_before += item["text"] + "\n"
                            else:
                                context_after += item["text"] + "\n"

                    match = CandidateMatch(
                        path=path,
                        line_number=line_number,
                        matched_text=matched_text,
                        context_before=context_before.strip(),
                        context_after=context_after.strip()
                    )
                    matches.append(match)

                    # Clear context for this file
                    if path in context_buffer:
                        del context_buffer[path]

                elif data.get("type") == "context":
                    path = data["data"]["path"]["text"]
                    line_number = data["data"]["line_number"]
                    text = data["data"]["lines"]["text"].strip()

                    if path not in context_buffer:
                        context_buffer[path] = []
                    context_buffer[path].append({
                        "line_number": line_number,
                        "text": text
                    })

            except (json.JSONDecodeError, KeyError) as e:
                # Skip malformed lines
                continue

        return matches

    def search_patterns(
        self,
        patterns: List[str],
        directory: Optional[str] = None
    ) -> List[CandidateMatch]:
        """
        Search for multiple patterns and combine results.

        Args:
            patterns: List of regex patterns to search for
            directory: Directory to search in

        Returns:
            Combined list of CandidateMatch objects
        """
        all_matches = []

        for pattern in patterns:
            matches = self.search(
                query=pattern,
                directory=directory,
                case_sensitive=True  # Patterns are usually case-sensitive
            )
            all_matches.extend(matches)

        # Remove duplicates and sort by relevance
        unique_matches = self._deduplicate_matches(all_matches)
        return sorted(unique_matches, key=lambda m: (m.path, m.line_number))[:self.max_results]

    def _deduplicate_matches(self, matches: List[CandidateMatch]) -> List[CandidateMatch]:
        """Remove duplicate matches from the results."""
        seen = set()
        unique_matches = []

        for match in matches:
            key = (match.path, match.line_number, match.matched_text)
            if key not in seen:
                seen.add(key)
                unique_matches.append(match)

        return unique_matches