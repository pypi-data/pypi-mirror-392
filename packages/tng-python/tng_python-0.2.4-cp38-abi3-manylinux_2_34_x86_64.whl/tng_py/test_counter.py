import ast
import subprocess
from pathlib import Path
from subprocess import TimeoutExpired

import tng_utils


def count_test_methods(test_file_path):
    """Count the number of actual test cases using pytest collection (matches pytest output)"""
    try:
        file_path = Path(test_file_path).resolve()

        if not file_path.exists():
            return 0

        pytest_cmd = None
        for cmd_path in ["pytest", "./venv/bin/pytest"]:
            try:
                subprocess.run([cmd_path, "--version"], capture_output=True, timeout=5)
                pytest_cmd = [cmd_path]
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        if not pytest_cmd:
            try:
                subprocess.run(
                    ["python", "-m", "pytest", "--version"],
                    capture_output=True,
                    timeout=5,
                )
                pytest_cmd = ["python", "-m", "pytest"]
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass

        if not pytest_cmd:
            count = tng_utils.count_test_methods(str(file_path))
            return count

        result = subprocess.run(
            pytest_cmd + ["--collect-only", "-q", str(file_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")

            for line in lines:
                line = line.strip()
                if ".py:" in line and line.split(":")[-1].strip().isdigit():
                    parts = line.split(":")
                    if len(parts) >= 2:
                        count_str = parts[-1].strip()
                        try:
                            return int(count_str)
                        except ValueError:
                            continue

            test_count = 0
            for line in lines:
                line = line.strip()
                if "::" in line and ("test_" in line or "Test" in line):
                    # Skip summary lines
                    if not any(
                        skip in line.lower()
                        for skip in [
                            "collected",
                            "test session",
                            "platform",
                            "rootdir",
                            "plugins",
                        ]
                    ):
                        test_count += 1

            if test_count == 0:
                for line in lines:
                    if "collected" in line.lower():
                        import re

                        match = re.search(r"collected (\d+) items?", line.lower())
                        if match:
                            test_count = int(match.group(1))
                            break

            return test_count if test_count > 0 else 1  # At least 1 if file exists
        else:
            count = tng_utils.count_test_methods(str(file_path))
            return count

    except TimeoutExpired:
        return fallback_count_test_methods(test_file_path)
    except Exception:
        return fallback_count_test_methods(test_file_path)


def fallback_count_test_methods(test_file_path):
    """Fallback method to count test methods using Python AST"""
    try:
        file_path = Path(test_file_path).resolve()
        if not file_path.exists():
            return 0

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        tree = ast.parse(content)
        count = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                count += 1

        return count
    except Exception:
        return 0
