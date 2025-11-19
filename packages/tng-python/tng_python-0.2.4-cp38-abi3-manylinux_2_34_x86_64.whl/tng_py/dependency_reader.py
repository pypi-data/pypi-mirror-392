"""
Dependency file reader for TNG Python.

Reads dependency files (requirements.txt, pyproject.toml, etc.) and returns their content
for use in test generation.
"""

from pathlib import Path


def get_dependency_content():
    """Get the complete content of all dependency files.

    Returns:
        dict: Dictionary with file paths as keys and content as values
    """
    content = {}

    # requirements.txt (pip)
    if Path("requirements.txt").exists():
        try:
            with open("requirements.txt", "r", encoding="utf-8") as f:
                content["requirements.txt"] = f.read()
        except Exception:
            pass

    # requirements-dev.txt, requirements-test.txt etc
    for req_file in Path(".").glob("requirements*.txt"):
        if req_file.exists():
            try:
                with open(req_file, "r", encoding="utf-8") as f:
                    content[str(req_file)] = f.read()
            except Exception:
                continue

    # pyproject.toml (poetry, uv, hatch, etc)
    if Path("pyproject.toml").exists():
        try:
            with open("pyproject.toml", "r", encoding="utf-8") as f:
                content["pyproject.toml"] = f.read()
        except Exception:
            pass

    # Pipfile (pipenv)
    if Path("Pipfile").exists():
        try:
            with open("Pipfile", "r", encoding="utf-8") as f:
                content["Pipfile"] = f.read()
        except Exception:
            pass

    # setup.py
    if Path("setup.py").exists():
        try:
            with open("setup.py", "r", encoding="utf-8") as f:
                content["setup.py"] = f.read()
        except Exception:
            pass

    # setup.cfg
    if Path("setup.cfg").exists():
        try:
            with open("setup.cfg", "r", encoding="utf-8") as f:
                content["setup.cfg"] = f.read()
        except Exception:
            pass

    # environment.yml (conda)
    if Path("environment.yml").exists():
        try:
            with open("environment.yml", "r", encoding="utf-8") as f:
                content["environment.yml"] = f.read()
        except Exception:
            pass

    return content


def get_dependency_content_string():
    """Get dependency content as a single concatenated string.

    Returns:
        str: All dependency file contents concatenated with file separators
    """
    content_dict = get_dependency_content()
    if not content_dict:
        return ""

    # Concatenate all content with file separators
    result_parts = []
    for file_path, file_content in content_dict.items():
        result_parts.append(f"=== {file_path} ===")
        result_parts.append(file_content)
        result_parts.append("")  # Empty line between files

    return "\n".join(result_parts)
