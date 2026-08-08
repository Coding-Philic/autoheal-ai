"""Project language and framework detection."""

from __future__ import annotations

from pathlib import Path
from typing import Optional


# File extension → language mapping
LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".rb": "ruby",
    ".php": "php",
    ".cs": "csharp",
    ".cpp": "cpp",
    ".c": "c",
    ".swift": "swift",
    ".kt": "kotlin",
    ".dart": "dart",
    ".r": "r",
    ".scala": "scala",
    ".ex": "elixir",
    ".exs": "elixir",
}

# Framework detection rules: (file_to_check, content_pattern, framework_name)
FRAMEWORK_RULES: dict[str, list[tuple[str, str, str]]] = {
    "python": [
        ("requirements.txt", "fastapi", "FastAPI"),
        ("requirements.txt", "django", "Django"),
        ("requirements.txt", "flask", "Flask"),
        ("requirements.txt", "tornado", "Tornado"),
        ("requirements.txt", "starlette", "Starlette"),
        ("pyproject.toml", "fastapi", "FastAPI"),
        ("pyproject.toml", "django", "Django"),
        ("pyproject.toml", "flask", "Flask"),
        ("Pipfile", "fastapi", "FastAPI"),
        ("Pipfile", "django", "Django"),
        ("Pipfile", "flask", "Flask"),
        ("manage.py", "django", "Django"),
    ],
    "javascript": [
        ("package.json", '"next"', "Next.js"),
        ("package.json", '"express"', "Express"),
        ("package.json", '"fastify"', "Fastify"),
        ("package.json", '"koa"', "Koa"),
        ("package.json", '"react"', "React"),
        ("package.json", '"vue"', "Vue"),
        ("package.json", '"angular"', "Angular"),
        ("package.json", '"svelte"', "Svelte"),
        ("package.json", '"nuxt"', "Nuxt"),
        ("package.json", '"nest"', "NestJS"),
    ],
    "typescript": [
        ("package.json", '"next"', "Next.js"),
        ("package.json", '"express"', "Express"),
        ("package.json", '"fastify"', "Fastify"),
        ("package.json", '"nest"', "NestJS"),
        ("package.json", '"angular"', "Angular"),
    ],
    "go": [
        ("go.mod", "gin-gonic", "Gin"),
        ("go.mod", "gorilla/mux", "Gorilla Mux"),
        ("go.mod", "fiber", "Fiber"),
        ("go.mod", "echo", "Echo"),
    ],
    "rust": [
        ("Cargo.toml", "actix", "Actix"),
        ("Cargo.toml", "rocket", "Rocket"),
        ("Cargo.toml", "axum", "Axum"),
        ("Cargo.toml", "warp", "Warp"),
    ],
    "ruby": [
        ("Gemfile", "rails", "Ruby on Rails"),
        ("Gemfile", "sinatra", "Sinatra"),
    ],
    "java": [
        ("pom.xml", "spring-boot", "Spring Boot"),
        ("build.gradle", "spring-boot", "Spring Boot"),
        ("pom.xml", "quarkus", "Quarkus"),
    ],
    "php": [
        ("composer.json", "laravel", "Laravel"),
        ("composer.json", "symfony", "Symfony"),
    ],
}

# Directories to exclude from scanning
EXCLUDE_DIRS = {
    "node_modules", ".venv", "venv", "__pycache__", ".git",
    "dist", "build", ".autoheal", ".tox", ".mypy_cache",
    ".pytest_cache", "target", "vendor", ".next",
}


class ProjectDetector:
    """Detect project language, framework, and dependencies."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    def detect(self) -> dict:
        """Detect project info and return as dict."""
        language = self._detect_language()
        framework = self._detect_framework(language)
        dependencies = self._detect_dependencies(language)

        return {
            "language": language,
            "framework": framework,
            "dependencies": dependencies,
            "project_dir": str(self.project_dir),
        }

    def _detect_language(self) -> str:
        """Detect primary language by counting source files."""
        counts: dict[str, int] = {}

        for ext, lang in LANGUAGE_MAP.items():
            try:
                files = list(self.project_dir.rglob(f"*{ext}"))
                files = [
                    f for f in files
                    if not any(part in EXCLUDE_DIRS for part in f.parts)
                ]
                if files:
                    counts[lang] = counts.get(lang, 0) + len(files)
            except (PermissionError, OSError):
                continue

        if not counts:
            return "unknown"

        return max(counts, key=counts.get)  # type: ignore[arg-type]

    def _detect_framework(self, language: str) -> Optional[str]:
        """Detect framework based on dependency files."""
        rules = FRAMEWORK_RULES.get(language, [])

        for file_name, pattern, framework in rules:
            file_path = self.project_dir / file_name
            if file_path.exists():
                try:
                    content = file_path.read_text(errors="ignore").lower()
                    if pattern.lower() in content:
                        return framework
                except (PermissionError, OSError):
                    pass

        return None

    def _detect_dependencies(self, language: str) -> dict[str, str]:
        """Parse dependency files and return name → version mapping."""
        deps: dict[str, str] = {}

        if language == "python":
            deps.update(self._parse_requirements_txt())
            deps.update(self._parse_pyproject_toml())
        elif language in ("javascript", "typescript"):
            deps.update(self._parse_package_json())
        elif language == "go":
            deps.update(self._parse_go_mod())
        elif language == "rust":
            deps.update(self._parse_cargo_toml())
        elif language == "ruby":
            deps.update(self._parse_gemfile())

        return deps

    def _parse_requirements_txt(self) -> dict[str, str]:
        """Parse requirements.txt."""
        path = self.project_dir / "requirements.txt"
        if not path.exists():
            return {}

        deps: dict[str, str] = {}
        try:
            for line in path.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    for sep in ["==", ">=", "<=", "~=", "!="]:
                        if sep in line:
                            name, version = line.split(sep, 1)
                            deps[name.strip()] = version.strip()
                            break
                    else:
                        if line and not line.startswith("["):
                            deps[line.split("[")[0].strip()] = "latest"
        except (PermissionError, OSError):
            pass
        return deps

    def _parse_pyproject_toml(self) -> dict[str, str]:
        """Parse pyproject.toml dependencies."""
        import sys

        path = self.project_dir / "pyproject.toml"
        if not path.exists():
            return {}

        try:
            if sys.version_info >= (3, 11):
                import tomllib
            else:
                try:
                    import tomli as tomllib  # type: ignore[no-redef]
                except ImportError:
                    return {}

            with open(path, "rb") as f:
                data = tomllib.load(f)

            deps: dict[str, str] = {}
            # Poetry style
            poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
            for name, version in poetry_deps.items():
                if name.lower() != "python":
                    if isinstance(version, str):
                        deps[name] = version
                    elif isinstance(version, dict):
                        deps[name] = version.get("version", "latest")

            # PEP 621 style
            pep_deps = data.get("project", {}).get("dependencies", [])
            for dep in pep_deps:
                parts = dep.split(">=")
                if len(parts) == 2:
                    deps[parts[0].strip()] = parts[1].strip()
                else:
                    deps[dep.strip().split("[")[0]] = "latest"

            return deps
        except Exception:
            return {}

    def _parse_package_json(self) -> dict[str, str]:
        """Parse package.json dependencies."""
        import json

        path = self.project_dir / "package.json"
        if not path.exists():
            return {}

        try:
            data = json.loads(path.read_text())
            deps: dict[str, str] = {}
            for section in ["dependencies", "devDependencies"]:
                for name, version in data.get(section, {}).items():
                    deps[name] = version
            return deps
        except Exception:
            return {}

    def _parse_go_mod(self) -> dict[str, str]:
        """Parse go.mod."""
        path = self.project_dir / "go.mod"
        if not path.exists():
            return {}

        deps: dict[str, str] = {}
        in_require = False
        try:
            for line in path.read_text().splitlines():
                line = line.strip()
                if line.startswith("require ("):
                    in_require = True
                elif line == ")":
                    in_require = False
                elif in_require and line:
                    parts = line.split()
                    if len(parts) >= 2:
                        deps[parts[0]] = parts[1]
        except (PermissionError, OSError):
            pass
        return deps

    def _parse_cargo_toml(self) -> dict[str, str]:
        """Parse Cargo.toml dependencies."""
        import sys

        path = self.project_dir / "Cargo.toml"
        if not path.exists():
            return {}

        try:
            if sys.version_info >= (3, 11):
                import tomllib
            else:
                try:
                    import tomli as tomllib  # type: ignore[no-redef]
                except ImportError:
                    return {}

            with open(path, "rb") as f:
                data = tomllib.load(f)
            deps: dict[str, str] = {}
            for name, version in data.get("dependencies", {}).items():
                if isinstance(version, str):
                    deps[name] = version
                elif isinstance(version, dict):
                    deps[name] = version.get("version", "latest")
            return deps
        except Exception:
            return {}

    def _parse_gemfile(self) -> dict[str, str]:
        """Parse Gemfile (basic)."""
        path = self.project_dir / "Gemfile"
        if not path.exists():
            return {}

        deps: dict[str, str] = {}
        try:
            for line in path.read_text().splitlines():
                line = line.strip()
                if line.startswith("gem "):
                    parts = line.replace("'", "").replace('"', "").split(",")
                    name = parts[0].replace("gem ", "").strip()
                    version = parts[1].strip() if len(parts) > 1 else "latest"
                    deps[name] = version
        except (PermissionError, OSError):
            pass
        return deps
