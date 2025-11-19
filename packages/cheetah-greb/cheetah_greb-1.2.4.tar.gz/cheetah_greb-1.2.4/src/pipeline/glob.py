"""
Glob tool implementation for file pattern discovery.
"""

from __future__ import annotations

import glob
import os
from pathlib import Path
from typing import List, Optional, Set

from .base import CandidateMatch


class GlobTool:
    """Implements file discovery using glob patterns."""

    def __init__(self, max_results: Optional[int] = None, ignore_file: Optional[str] = None):
        self.max_results = max_results or int(os.getenv('MAX_GLOB_RESULTS', '10'))
        self.ignore_file = ignore_file or self._find_ignore_file()
        self.ignore_patterns = self._load_ignore_patterns()

    def _find_ignore_file(self) -> Optional[str]:
        """Find the ignore file to use for glob operations."""
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

    def find_files(
        self,
        patterns: List[str],
        directory: Optional[str] = None,
        recursive: bool = True,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[str]:
        """
        Find files matching the given patterns.

        Args:
            patterns: List of glob patterns (e.g., ["*.py", "src/**/*.ts"])
            directory: Base directory to search in (default: current directory)
            recursive: Whether to search recursively
            exclude_patterns: Patterns to exclude (e.g., ["*.test.py", "node_modules/**"])

        Returns:
            List of matching file paths
        """
        if directory is None:
            directory = "."

        # Combine user exclude patterns with ignore file patterns
        all_exclude_patterns = self.ignore_patterns.copy()
        if exclude_patterns:
            all_exclude_patterns.extend(exclude_patterns)

        found_files = set()

        for pattern in patterns:
            # Build the full pattern path
            if recursive and not pattern.startswith("**"):
                full_pattern = os.path.join(directory, "**", pattern)
            else:
                full_pattern = os.path.join(directory, pattern)

            # Use glob to find matches
            try:
                matches = glob.glob(full_pattern, recursive=recursive)
                for match in matches:
                    if os.path.isfile(match) and not self._should_exclude(match, all_exclude_patterns):
                        found_files.add(os.path.relpath(match, directory))
            except (OSError, ValueError):
                # Skip invalid patterns
                continue

        # Convert to sorted list and limit results
        result = sorted(list(found_files))
        return result[:self.max_results]

    def find_files_by_extension(
        self,
        extensions: List[str],
        directory: Optional[str] = None,
        max_depth: Optional[int] = None
    ) -> List[str]:
        """
        Find files by extension.

        Args:
            extensions: List of file extensions (e.g., [".py", ".js", ".ts"])
            directory: Base directory to search in
            max_depth: Maximum directory depth to search

        Returns:
            List of matching file paths
        """
        patterns = []
        for ext in extensions:
            if not ext.startswith('.'):
                ext = '.' + ext
            patterns.append(f"*{ext}")

        if max_depth is not None:
            # Create depth-limited patterns
            depth_patterns = []
            for depth in range(max_depth + 1):
                prefix = "*\\" * depth if os.name == 'nt' else "*/" * depth
                for pattern in patterns:
                    depth_patterns.append(prefix + pattern)
            patterns = depth_patterns

        return self.find_files(patterns, directory=directory)

    def find_files_by_name(
        self,
        names: List[str],
        directory: Optional[str] = None,
        exact_match: bool = False
    ) -> List[str]:
        """
        Find files by name.

        Args:
            names: List of file names (e.g., ["package.json", "requirements.txt"])
            directory: Base directory to search in
            exact_match: Whether to require exact name matches

        Returns:
            List of matching file paths
        """
        patterns = []
        for name in names:
            if exact_match:
                patterns.append(f"**/{name}")
            else:
                patterns.append(f"**/*{name}*")

        return self.find_files(patterns, directory=directory)

    def find_directories(
        self,
        patterns: List[str],
        directory: Optional[str] = None
    ) -> List[str]:
        """
        Find directories matching the given patterns.

        Args:
            patterns: List of glob patterns for directories
            directory: Base directory to search in

        Returns:
            List of matching directory paths
        """
        if directory is None:
            directory = "."

        found_dirs = set()

        for pattern in patterns:
            full_pattern = os.path.join(directory, pattern)
            try:
                matches = glob.glob(full_pattern, recursive=True)
                for match in matches:
                    if os.path.isdir(match):
                        found_dirs.add(os.path.relpath(match, directory))
            except (OSError, ValueError):
                continue

        return sorted(list(found_dirs))[:self.max_results]

    def create_candidates_from_files(
        self,
        files: List[str],
        base_directory: Optional[str] = None
    ) -> List[CandidateMatch]:
        """
        Create CandidateMatch objects from a list of files.

        Args:
            files: List of file paths
            base_directory: Base directory for relative paths

        Returns:
            List of CandidateMatch objects
        """
        candidates = []

        for file_path in files:
            # For file-based matches, we use line 1 as a placeholder
            candidate = CandidateMatch(
                path=file_path,
                line_number=1,
                matched_text=f"File: {file_path}",
                context_before="",
                context_after=""
            )
            candidates.append(candidate)

        return candidates[:self.max_results]

    def _should_exclude(self, file_path: str, exclude_patterns: List[str]) -> bool:
        """Check if a file should be excluded based on exclude patterns."""
        import fnmatch

        for pattern in exclude_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
        return False

    def get_common_file_patterns(self, language: Optional[str] = None) -> List[str]:
        """
        Get comprehensive file patterns for specific languages or general development.

        Args:
            language: Specific programming language (e.g., "python", "javascript")

        Returns:
            List of common file patterns
        """
        # Comprehensive language patterns
        language_patterns = {
            "python": ["*.py", "requirements*.txt", "pyproject.toml", "setup.py", "Pipfile", "poetry.lock", "*.pyi", "*.pyx"],
            "javascript": ["*.js", "*.jsx", "*.mjs", "*.cjs", "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "jsconfig.json"],
            "typescript": ["*.ts", "*.tsx", "*.d.ts", "tsconfig.json", "tsconfig.*.json", "package.json", "typechain", "*.typechain"],
            "java": ["*.java", "*.class", "*.jar", "pom.xml", "build.gradle", "settings.gradle", "*.properties", "gradle.properties"],
            "go": ["*.go", "go.mod", "go.sum", "go.work", "*.s", "*.h", "Gopkg.toml", "Gopkg.lock"],
            "rust": ["*.rs", "Cargo.toml", "Cargo.lock", "*.rlib", "rust-toolchain.toml", "build.rs"],
            "cpp": ["*.cpp", "*.cxx", "*.cc", "*.c", "*.h", "*.hpp", "*.hxx", "CMakeLists.txt", "Makefile", "makefile", "*.mk", "conanfile.*", "vcpkg.json"],
            "csharp": ["*.cs", "*.csx", "*.vb", "*.fs", "*.fsx", "project.json", "*.csproj", "*.sln", "packages.config", "Directory.Build.props"],
            "php": ["*.php", "*.phtml", "*.php3", "*.php4", "*.php5", "*.phar", "composer.json", "composer.lock"],
            "ruby": ["*.rb", "*.rbw", "Gemfile", "Gemfile.lock", "*.gemspec", "Rakefile", "config.ru", "*.rake"],
            "swift": ["*.swift", "Package.swift", "Package.resolved", "*.xcodeproj", "*.xcworkspace"],
            "kotlin": ["*.kt", "*.kts", "build.gradle", "gradle.properties", "*.xml"],
            "scala": ["*.scala", "*.sc", "build.sbt", "project/*.scala", "*.xml"],
            "dart": ["*.dart", "pubspec.yaml", "pubspec.lock", "*.g.dart"],
            "lua": ["*.lua", "*.wlua", "*.rockspec", "*.rock"],
            "r": ["*.r", "*.R", "DESCRIPTION", "NAMESPACE", "*.Rd"],
            "perl": ["*.pl", "*.pm", "*.t", "Makefile.PL", "META.*", "cpanfile"],
            "shell": ["*.sh", "*.bash", "*.zsh", "*.fish", "Makefile", "Dockerfile*", "docker-compose*"],
            "sql": ["*.sql", "*.ddl", "*.dml", "*.proc", "*.pkg", "*.pks", "*.trg"],
            "web": ["*.html", "*.htm", "*.css", "*.scss", "*.sass", "*.less", "*.vue", "*.svelte", "*.jsx", "*.tsx"],
            "config": ["*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg", "*.conf", "*.xml", "*.properties"],
        }

        # General patterns for configuration, documentation, and build files
        general_patterns = [
            "*.md", "*.txt", "*.rst", "*.adoc", "*.1", "*.5", "*.7", "*.8",
            "*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg", "*.conf", "*.xml", "*.properties",
            "Dockerfile*", "docker-compose*", "Containerfile*", "*.dockerfile",
            ".env*", ".gitignore", ".gitattributes", ".editorconfig", ".eslintrc*", ".prettierrc*",
            "README*", "CHANGELOG*", "LICENSE*", "CONTRIBUTING*", "CODE_OF_CONDUCT*",
            "Makefile", "makefile", "*.mk", "build.xml", "build.gradle", "pom.xml",
            "*.lock", "*.log", "*.tmp", "*.bak", "*.orig", "*.swp",
        ]

        # Framework-specific patterns
        framework_patterns = {
            "react": ["*.jsx", "*.tsx", "src/components/**", "src/hooks/**", "public/**"],
            "vue": ["*.vue", "src/components/**", "src/views/**", "src/store/**", "vue.config.*"],
            "angular": ["*.ts", "*.html", "angular.json", "src/app/**", "src/assets/**"],
            "django": ["*.py", "settings.py", "urls.py", "wsgi.py", "manage.py", "templates/**", "static/**"],
            "flask": ["*.py", "app.py", "wsgi.py", "templates/**", "static/**", "requirements*.txt"],
            "rails": ["*.rb", "Gemfile", "config/routes.rb", "app/**", "db/**", "spec/**"],
            "spring": ["*.java", "application*.yml", "application*.properties", "src/main/**", "src/test/**"],
            "express": ["*.js", "app.js", "server.js", "routes/**", "middleware/**", "views/**"],
            "next": ["*.js", "*.jsx", "*.ts", "*.tsx", "next.config.*", "pages/**", "components/**"],
            "nuxt": ["*.js", "*.vue", "nuxt.config.*", "pages/**", "components/**", "server/**"],
        }

        if language:
            language_lower = language.lower()

            # Check for exact language match
            if language_lower in language_patterns:
                return language_patterns[language_lower] + general_patterns

            # Check for framework match
            if language_lower in framework_patterns:
                return framework_patterns[language_lower] + general_patterns

            # Check for partial matches
            for lang_key, patterns in language_patterns.items():
                if language_lower in lang_key or lang_key in language_lower:
                    return patterns + general_patterns

        return general_patterns

    def get_language_specific_directories(self, language: str) -> List[str]:
        """
        Get common directory patterns for a specific language.

        Args:
            language: Programming language

        Returns:
            List of directory patterns
        """
        directory_patterns = {
            "python": ["src/**", "lib/**", "tests/**", "test/**", "docs/**", "examples/**", "scripts/**"],
            "javascript": ["src/**", "lib/**", "dist/**", "build/**", "public/**", "test/**", "tests/**", "docs/**"],
            "typescript": ["src/**", "lib/**", "dist/**", "build/**", "types/**", "test/**", "tests/**", "docs/**"],
            "java": ["src/main/**", "src/test/**", "src/main/java/**", "src/main/resources/**", "src/test/java/**"],
            "go": ["cmd/**", "pkg/**", "internal/**", "vendor/**", "test/**", "docs/**"],
            "rust": ["src/**", "tests/**", "benches/**", "examples/**", "docs/**"],
            "cpp": ["src/**", "include/**", "lib/**", "bin/**", "test/**", "tests/**", "build/**", "cmake/**"],
            "csharp": ["src/**", "Source/**", "Test/**", "Tests/**", "Properties/**", "obj/**", "bin/**"],
            "php": ["src/**", "app/**", "lib/**", "vendor/**", "tests/**", "config/**", "public/**"],
            "ruby": ["lib/**", "app/**", "test/**", "spec/**", "config/**", "db/**", "public/**"],
            "swift": ["Sources/**", "Tests/**", "Example/**"],
            "go": ["cmd/**", "pkg/**", "internal/**", "api/**", "web/**", "service/**"],
        }

        return directory_patterns.get(language.lower(), ["src/**", "lib/**", "test/**", "docs/**"])