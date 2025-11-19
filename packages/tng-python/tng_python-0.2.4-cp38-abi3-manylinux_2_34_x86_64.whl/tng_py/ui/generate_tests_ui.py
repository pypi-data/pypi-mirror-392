import json
from pathlib import Path

import tng_utils

from ..config import get_base_url, get_api_key, get_enabled_config
from ..dependency_reader import get_dependency_content_string
from ..save_file import save_test_file
from .go_ui_session import GoUISession


class GenerateTestsUI:
    def __init__(self, cli_mode=False):
        self.cli_mode = cli_mode
        if not cli_mode:
            self.go_ui_session = GoUISession()
            self.go_ui_session.start()

    def show(self):
        """Main test generation flow"""
        while True:
            result = self._show_file_selection()
            if result == "back":
                return "back"
            elif result == "exit":
                return "exit"
            elif result is None:
                # Exit on error
                return "exit"

    def _show_file_selection(self):
        """Show file selection interface"""
        python_files = self._get_user_python_files()

        if not python_files:
            self.go_ui_session.show_no_items("Python files")
            return "back"

        items = [{"name": file.name, "path": str(file.parent)} for file in python_files]

        selected_name = self.go_ui_session.show_list_view("Select Python File", items)

        if selected_name == "back":
            return "back"

        selected_file = None
        for file in python_files:
            if file.name == selected_name:
                selected_file = str(file)
                break

        if not selected_file:
            return "back"

        return self._show_methods_for_file(selected_file)

    def _show_methods_for_file(self, file_path):
        """Show methods for a specific file"""
        methods = self._get_file_methods(file_path)

        if not methods:
            self.go_ui_session.show_no_items("methods")
            return self._show_file_selection()

        file_name = Path(file_path).name
        items = [
            {"name": method["display"], "path": f"Method in {file_name}"}
            for method in methods
        ]

        selected_display = self.go_ui_session.show_list_view(
            f"Select Method for {file_name}", items
        )

        if selected_display == "back":
            return self._show_file_selection()

        if selected_display:
            # Find the method object that matches the selected display name
            selected_method = None
            for method in methods:
                if method["display"] == selected_display:
                    selected_method = method
                    break

            if selected_method:
                result = self._generate_tests_for_method(file_path, selected_method)
                if result and result.get("file_path") and not result.get("error"):
                    self._show_post_generation_menu(result)
                    return self._show_file_selection()
                elif result and result.get("error"):
                    # Exit on error instead of returning to file selection
                    return None
            return self._show_file_selection()
        else:
            return self._show_file_selection()

    def _generate_tests_for_method(self, file_path, selected_method):
        """Generate tests for selected method using Go UI progress"""
        file_name = Path(file_path).name

        # Create display name: class_name#method_name or filename#method_name
        if selected_method.get("class"):
            display_name = f"{selected_method['class']}#{selected_method['name']}"
        else:
            display_name = f"{file_name}#{selected_method['name']}"

        def progress_handler(progress):
            progress.update("Submitting request to API...")

            try:
                base_url = get_base_url()
                api_key = get_api_key()

                # Prepare request data with config and dependency content
                request_data = {
                    "file_path": file_path,
                    "method_name": selected_method["name"],
                    "config": get_enabled_config(),
                    "dependency_content": get_dependency_content_string(),
                }

                if selected_method.get("class"):
                    request_data["class_name"] = selected_method["class"]

                progress.update("Calling API...")
                job_result = tng_utils.submit_test_generation_job(
                    base_url=base_url,
                    api_key=api_key,
                    request_data=json.dumps(request_data),
                )

                job_id = job_result.get("job_id")
                progress.update(f"Job submitted: {job_id}")

                # Poll for job completion with progress updates
                import time

                max_duration = 600  # 10 minutes
                poll_interval = 10  # 10 seconds
                start_time = time.time()

                while True:
                    elapsed = time.time() - start_time

                    # Check timeout
                    if elapsed > max_duration:
                        progress.error(f"Timeout after {max_duration} seconds")
                        tng_utils.trigger_cleanup(base_url, api_key, job_id)
                        return {"error": "Timeout", "result": None}

                    # Update progress with elapsed time
                    percent = min(int((elapsed / max_duration) * 100), 99)
                    progress.update(f"Generating tests... ({int(elapsed)}s)", percent)

                    try:
                        status_response = tng_utils.get_job_status(
                            base_url, api_key, job_id
                        )
                        status = status_response.get("status")

                        if status == "completed":
                            progress.update("Tests generated successfully!")

                            # Save the generated test file
                            test_result = status_response.get("result")
                            file_info = save_test_file(json.dumps(test_result))

                            tng_utils.trigger_cleanup(
                                base_url, api_key, job_id
                            )  # Cleanup job
                            return {
                                "message": "Tests generated successfully!",
                                "result": test_result,
                                "file_info": file_info,
                            }
                        elif status == "failed":
                            error_msg = status_response.get(
                                "error", "Test generation failed"
                            )
                            progress.error(f"Test generation failed: {error_msg}")
                            try:
                                tng_utils.trigger_cleanup(base_url, api_key, job_id)
                            except Exception:
                                pass
                            return {"error": error_msg, "result": None}
                        elif status in ["pending", "processing"]:
                            # Continue polling
                            time.sleep(poll_interval)
                            continue
                        else:
                            # Unknown status, continue polling
                            time.sleep(poll_interval)
                            continue
                    except Exception as poll_error:
                        # Check if we've been polling too long or if it's a permanent error
                        if (
                            elapsed > max_duration * 0.8
                        ):  # If we're in the last 20% of timeout
                            progress.error(
                                f"Permanent error after {int(elapsed)}s: {poll_error}"
                            )
                            try:
                                tng_utils.trigger_cleanup(base_url, api_key, job_id)
                            except:
                                pass
                            return {
                                "error": f"Polling failed: {poll_error}",
                                "result": None,
                            }
                        # Network error, continue polling
                        time.sleep(poll_interval)
                        continue

            except Exception as e:
                progress.error(f"Failed to generate tests: {str(e)}")
                # Try to cleanup if job was created
                try:
                    if "job_id" in locals():
                        tng_utils.trigger_cleanup(base_url, api_key, job_id)
                except Exception:
                    pass  # Ignore cleanup errors
                return {"result": {"error": str(e)}}

        if self.cli_mode:
            # For CLI mode, call progress_handler directly without UI wrapper
            class MockProgress:
                def update(self, message, percent=None):
                    print(f"🔄 {message}")

                def error(self, message):
                    print(f"❌ {message}")

            mock_progress = MockProgress()
            try:
                return progress_handler(mock_progress)
            except Exception as e:
                mock_progress.error(str(e))
                return {"error": str(e), "result": None}
        else:
            # Original UI mode
            result = self.go_ui_session.show_progress(
                f"Generating test for {display_name}", progress_handler
            )

            if result and result.get("file_info"):
                self._show_post_generation_menu(result["file_info"])
                return result
            return None

    def _show_post_generation_menu(self, file_info):
        file_path = file_info.get("file_path") or file_info.get("absolute_path")
        run_command = file_info.get("run_command", f"pytest {file_path}")

        while True:
            choice = self.go_ui_session.show_post_generation_menu(
                file_path, run_command
            )

            if choice == "run_tests":
                self._run_and_show_test_results(run_command)
            elif choice == "copy_command":
                self._copy_command_and_show_success(run_command)
            elif choice == "back":
                break
            else:
                break

    def _copy_command_and_show_success(self, command):
        """Copy command to clipboard and show success"""
        import subprocess
        import sys

        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(["pbcopy"], input=command.encode("utf-8"), check=True)
                self.go_ui_session.show_clipboard_success(command)
            elif sys.platform.startswith("linux"):  # Linux
                try:
                    subprocess.run(
                        ["xclip", "-selection", "clipboard"],
                        input=command.encode("utf-8"),
                        check=True,
                    )
                    self.go_ui_session.show_clipboard_success(command)
                except FileNotFoundError:
                    print(f"\n📋 Copy this command:\n{command}\n")
                    input("Press Enter to continue...")
            else:  # Windows or other
                print(f"\n📋 Copy this command:\n{command}\n")
                input("Press Enter to continue...")
        except Exception as e:
            print(f"\n📋 Copy this command:\n{command}\n")
            input("Press Enter to continue...")

    def _run_and_show_test_results(self, command):
        """Run tests and show results using Go UI"""
        import subprocess

        # Run tests with spinner
        def spinner_handler():
            output = subprocess.run(command, shell=True, capture_output=True, text=True)
            return {
                "success": True,
                "message": "Tests completed",
                "output": output.stdout + output.stderr,
                "exit_code": output.returncode,
            }

        test_output = self.go_ui_session.show_spinner(
            "Running tests...", spinner_handler
        )

        passed, failed, errors, total = self._parse_test_output(
            test_output.get("output", ""), test_output.get("exit_code", 1)
        )

        self.go_ui_session.show_test_results(
            "Test Results",
            passed,
            failed,
            errors,
            total,
            [],  # No detailed results for now
        )

    def _parse_test_output(self, output, exit_code):
        """Parse pytest output to extract test counts"""
        import re

        passed = failed = errors = 0

        passed_match = re.search(r"(\d+) passed", output)
        failed_match = re.search(r"(\d+) failed", output)
        error_match = re.search(r"(\d+) error", output)

        if passed_match:
            passed = int(passed_match.group(1))
        if failed_match:
            failed = int(failed_match.group(1))
        if error_match:
            errors = int(error_match.group(1))

        total = passed + failed + errors

        if total == 0:
            if exit_code == 0:
                passed = 1
                total = 1
            else:
                failed = 1
                total = 1

        return passed, failed, errors, total

    def _get_user_python_files(self):
        """Get Python files that belong to the user's project (not dependencies)"""
        current_dir = Path.cwd()
        python_files = []

        exclude_dirs = {
            "venv",
            "env",
            ".venv",
            ".env",
            "site-packages",
            "dist-packages",
            "__pycache__",
            ".git",
            ".pytest_cache",
            "node_modules",
            "target",
            "build",
            "dist",
            ".mypy_cache",
            ".tox",
            "htmlcov",
            "tests",
            "test",
            "spec",
            "migrations",
        }

        for py_file in current_dir.rglob("*.py"):
            if any(excluded in py_file.parts for excluded in exclude_dirs):
                continue

            if py_file.stat().st_size < 10:
                continue

            python_files.append(py_file)

        # Sort by name for consistent ordering
        return sorted(python_files, key=lambda x: x.name)

    def _get_file_methods(self, file_path):
        """Get method info from Python file using Rust parser."""
        try:
            import tng_utils

            # Use Rust function extractor
            items = tng_utils.extract_functions_from_file(file_path)

            # Convert to format expected by the rest of the code
            methods = []
            for item in items:
                name = item["name"]

                # Check if it's a method (ClassName.method_name) or function
                if "." in name:
                    class_name, method_name = name.split(".", 1)
                    methods.append(
                        {
                            "name": method_name,
                            "class": class_name,
                            "display": name,
                            "type": "method",
                        }
                    )
                else:
                    methods.append(
                        {
                            "name": name,
                            "class": None,
                            "display": name,
                            "type": "function",
                        }
                    )

            return methods
        except Exception:
            return []
