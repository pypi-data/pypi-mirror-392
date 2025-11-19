"""Distribution and packaging tests for Bayt SDK

These tests verify:
- Package builds correctly
- Installation works properly
- All modules are importable
- Version metadata is correct
- Dependencies are properly declared

Run with: pytest tests/test_distribution.py -v
"""

import pytest
import sys
import os
import subprocess
import importlib
from pathlib import Path


# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class TestPackageStructure:
    """Test package structure and organization"""

    def test_package_directory_exists(self):
        """Test that baytos.claro package directory exists"""
        package_dir = PROJECT_ROOT / "baytos" / "claro"
        assert package_dir.exists()
        assert package_dir.is_dir()

    def test_init_file_exists(self):
        """Test that __init__.py exists"""
        init_file = PROJECT_ROOT / "baytos" / "claro" / "__init__.py"
        assert init_file.exists()

    def test_required_modules_exist(self):
        """Test that all required modules exist"""
        required_modules = [
            "client.py",
            "models.py",
            "utils.py",
            "exceptions.py",
        ]

        claro_dir = PROJECT_ROOT / "baytos" / "claro"
        for module_name in required_modules:
            module_path = claro_dir / module_name
            assert module_path.exists(), f"Required module {module_name} not found"

    def test_no_pycache_in_package(self):
        """Test that __pycache__ is not included in distribution"""
        # This is more relevant for built distributions
        # but we can check source
        gitignore = PROJECT_ROOT / ".gitignore"

        if gitignore.exists():
            with open(gitignore) as f:
                content = f.read()
            assert "__pycache__" in content or "*.pyc" in content


class TestPackageMetadata:
    """Test package metadata"""

    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists"""
        pyproject = PROJECT_ROOT / "pyproject.toml"
        assert pyproject.exists()

    def test_readme_exists(self):
        """Test that README exists"""
        readme = PROJECT_ROOT / "README.md"
        assert readme.exists()

    def test_license_exists(self):
        """Test that LICENSE exists"""
        license_file = PROJECT_ROOT / "LICENSE"
        assert license_file.exists()

    def test_pyproject_has_required_fields(self):
        """Test that pyproject.toml has required metadata"""
        pyproject = PROJECT_ROOT / "pyproject.toml"

        with open(pyproject) as f:
            content = f.read()

        # Required fields
        assert "name" in content
        assert "version" in content
        assert "description" in content
        assert "authors" in content
        assert "dependencies" in content

    def test_version_format(self):
        """Test that version follows semantic versioning"""
        import re

        # For Python < 3.11, use tomli
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib

        pyproject = PROJECT_ROOT / "pyproject.toml"

        with open(pyproject, "rb") as f:
            config = tomllib.load(f)

        version = config["project"]["version"]

        # Should match semantic versioning pattern
        semver_pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$"
        assert re.match(
            semver_pattern, version
        ), f"Version {version} does not follow semantic versioning"


class TestImports:
    """Test that package imports work correctly"""

    def test_import_claro(self):
        """Test that claro package can be imported"""
        try:
            import baytos.claro

            assert baytos.claro
        except ImportError as e:
            pytest.fail(f"Failed to import baytos.claro: {e}")

    def test_import_client(self):
        """Test that BaytClient can be imported"""
        try:
            from baytos.claro import BaytClient

            assert BaytClient
        except ImportError as e:
            pytest.fail(f"Failed to import BaytClient: {e}")

    def test_import_prompt(self):
        """Test that Prompt can be imported"""
        try:
            from baytos.claro import Prompt

            assert Prompt
        except ImportError as e:
            pytest.fail(f"Failed to import Prompt: {e}")

    def test_import_exceptions(self):
        """Test that exceptions can be imported"""
        try:
            from baytos.claro.exceptions import (
                BaytAPIError,
                BaytAuthError,
                BaytNotFoundError,
                BaytRateLimitError,
                BaytValidationError,
            )

            assert all(
                [
                    BaytAPIError,
                    BaytAuthError,
                    BaytNotFoundError,
                    BaytRateLimitError,
                    BaytValidationError,
                ]
            )
        except ImportError as e:
            pytest.fail(f"Failed to import exceptions: {e}")

    def test_public_api_exports(self):
        """Test that __init__.py exports public API"""
        import baytos.claro

        # Should export these at minimum
        expected_exports = ["BaytClient", "Prompt"]

        for export in expected_exports:
            assert hasattr(
                baytos.claro, export
            ), f"Expected export {export} not found in claro module"

    def test_no_import_errors(self):
        """Test that importing doesn't cause errors"""
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("error")

            try:
                import baytos.claro
                from baytos.claro import BaytClient, Prompt
            except Warning as w:
                pytest.fail(f"Import caused warning: {w}")


class TestDependencies:
    """Test dependency declarations"""

    def test_requests_dependency(self):
        """Test that requests is available"""
        try:
            import requests

            assert requests
        except ImportError:
            pytest.fail("Required dependency 'requests' not installed")

    def test_requests_version(self):
        """Test that requests meets minimum version"""
        import requests
        from packaging import version

        min_version = "2.25.0"
        current_version = requests.__version__

        assert version.parse(current_version) >= version.parse(
            min_version
        ), f"requests {current_version} is below minimum {min_version}"

    def test_no_missing_dependencies(self):
        """Test that all imports work (no missing dependencies)"""
        try:
            import baytos.claro
            from baytos.claro import BaytClient

            # Try to instantiate (with mock key to avoid errors)
            client = BaytClient(
                api_key="sk_test_distribution_mock_key_1234567890abcdefghij"
            )
            assert client

        except ImportError as e:
            pytest.fail(f"Missing dependency: {e}")


class TestPackageBuild:
    """Test package building"""

    @pytest.mark.slow
    def test_package_builds(self):
        """Test that package can be built"""
        # This test actually builds the package
        # Skip in regular runs, enable for pre-release checks

        if not os.getenv("TEST_BUILD_PACKAGE"):
            pytest.skip("Set TEST_BUILD_PACKAGE=1 to run build test")

        # Clean previous builds
        dist_dir = PROJECT_ROOT / "dist"
        if dist_dir.exists():
            import shutil

            shutil.rmtree(dist_dir)

        # Build the package
        result = subprocess.run(
            [sys.executable, "-m", "build"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

        # Should succeed
        assert result.returncode == 0, f"Build failed: {result.stderr}"

        # Should create dist directory with files
        assert dist_dir.exists()
        built_files = list(dist_dir.glob("*"))
        assert len(built_files) > 0, "No distribution files created"

        # Should have both wheel and sdist
        wheels = list(dist_dir.glob("*.whl"))
        sdists = list(dist_dir.glob("*.tar.gz"))

        assert len(wheels) > 0, "No wheel file created"
        assert len(sdists) > 0, "No source distribution created"

    @pytest.mark.slow
    def test_wheel_contents(self):
        """Test that wheel contains expected files"""
        if not os.getenv("TEST_BUILD_PACKAGE"):
            pytest.skip("Set TEST_BUILD_PACKAGE=1 to run build test")

        dist_dir = PROJECT_ROOT / "dist"
        wheels = list(dist_dir.glob("*.whl"))

        if not wheels:
            pytest.skip("No wheel file found")

        wheel_file = wheels[0]

        # Check wheel contents
        import zipfile

        with zipfile.ZipFile(wheel_file) as zf:
            names = zf.namelist()

            # Should contain baytos.claro package
            assert any("baytos/claro/__init__.py" in n for n in names)
            assert any("baytos/claro/client.py" in n for n in names)
            assert any("baytos/claro/models.py" in n for n in names)

            # Should contain metadata
            assert any("METADATA" in n for n in names)

    @pytest.mark.slow
    def test_sdist_contents(self):
        """Test that sdist contains expected files"""
        if not os.getenv("TEST_BUILD_PACKAGE"):
            pytest.skip("Set TEST_BUILD_PACKAGE=1 to run build test")

        dist_dir = PROJECT_ROOT / "dist"
        sdists = list(dist_dir.glob("*.tar.gz"))

        if not sdists:
            pytest.skip("No sdist file found")

        sdist_file = sdists[0]

        # Check sdist contents
        import tarfile

        with tarfile.open(sdist_file) as tf:
            names = tf.getnames()

            # Should contain source files
            assert any("baytos/claro/__init__.py" in n for n in names)
            assert any("baytos/claro/client.py" in n for n in names)

            # Should contain project files
            assert any("pyproject.toml" in n for n in names)
            assert any("README" in n for n in names)


class TestInstallation:
    """Test package installation"""

    @pytest.mark.slow
    def test_package_installs(self):
        """Test that package can be installed"""
        if not os.getenv("TEST_INSTALL_PACKAGE"):
            pytest.skip("Set TEST_INSTALL_PACKAGE=1 to run install test")

        # Create a virtual environment and test installation
        # This is a comprehensive test that should be run manually
        pytest.skip("Manual test: install package in clean venv")

    def test_version_accessible(self):
        """Test that version is accessible after import"""
        import baytos.claro

        # Version should be accessible
        # Either as __version__ or in metadata
        has_version = (
            hasattr(baytos.claro, "__version__")
            or hasattr(baytos.claro, "VERSION")
            or hasattr(baytos.claro, "version")
        )

        # If not directly accessible, should be in metadata
        if not has_version:
            try:
                from importlib.metadata import version

                pkg_version = version("baytos-claro")
                assert pkg_version
            except ImportError:
                pytest.skip("importlib.metadata not available")


class TestCodeQuality:
    """Test code quality for distribution"""

    def test_no_syntax_errors(self):
        """Test that all Python files have valid syntax"""
        claro_dir = PROJECT_ROOT / "baytos" / "claro"

        for py_file in claro_dir.rglob("*.py"):
            with open(py_file) as f:
                code = f.read()

            try:
                compile(code, py_file, "exec")
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {py_file}: {e}")

    def test_no_print_statements_in_library(self):
        """Test that library code doesn't have print statements"""
        claro_dir = PROJECT_ROOT / "baytos" / "claro"

        for py_file in claro_dir.rglob("*.py"):
            # Skip __main__ files
            if "__main__" in str(py_file):
                continue

            with open(py_file) as f:
                content = f.read()

            # Should not have print() calls in library code
            # (except in examples or if behind a debug flag)
            if "print(" in content:
                # Allow commented prints or string "print("
                lines = content.split("\n")
                for line in lines:
                    if "print(" in line and not line.strip().startswith("#"):
                        # This is acceptable if it's for debugging/logging
                        # or in __repr__ methods
                        if "__repr__" not in content and "debug" not in line.lower():
                            pytest.fail(
                                f"Found print() in library code: {py_file}\n"
                                f"Line: {line.strip()}"
                            )

    def test_has_type_hints(self):
        """Test that code includes type hints"""
        # Check at least the main client file has type hints
        client_file = PROJECT_ROOT / "baytos" / "claro" / "client.py"

        with open(client_file) as f:
            content = f.read()

        # Should have type hints
        assert "->" in content, "No return type hints found"
        assert ":" in content and "def " in content, "No parameter type hints found"


class TestDocumentation:
    """Test documentation for distribution"""

    def test_readme_has_installation(self):
        """Test that README includes installation instructions"""
        readme = PROJECT_ROOT / "README.md"

        with open(readme) as f:
            content = f.read()

        # Should mention pip install
        assert "pip install" in content.lower()

    def test_readme_has_usage(self):
        """Test that README includes usage examples"""
        readme = PROJECT_ROOT / "README.md"

        with open(readme) as f:
            content = f.read()

        # Should have code examples
        assert "```python" in content or "```py" in content

    def test_readme_has_api_reference(self):
        """Test that README mentions API or documentation"""
        readme = PROJECT_ROOT / "README.md"

        with open(readme) as f:
            content = f.read()

        # Should mention API or docs
        has_docs = (
            "api" in content.lower()
            or "documentation" in content.lower()
            or "reference" in content.lower()
        )

        assert has_docs


class TestSecurityForDistribution:
    """Test security aspects for distribution"""

    def test_no_secrets_in_code(self):
        """Test that no secrets are committed"""
        import re

        claro_dir = PROJECT_ROOT / "baytos" / "claro"

        for py_file in claro_dir.rglob("*.py"):
            with open(py_file) as f:
                content = f.read()

            # Check for potential API keys
            potential_keys = re.findall(r"b_[a-z]+_[a-zA-Z0-9]{20,}", content)

            for key in potential_keys:
                # Should be obviously fake/example
                assert any(
                    [
                        "example" in content.lower(),
                        "test" in content.lower(),
                        "xxx" in key.lower(),
                    ]
                ), f"Potential real API key in {py_file}"

    def test_no_personal_info_in_metadata(self):
        """Test that no personal info is in public metadata"""
        pyproject = PROJECT_ROOT / "pyproject.toml"

        with open(pyproject) as f:
            content = f.read()

        # Should not contain personal emails (use official ones)
        # This is project-specific, adjust as needed
        assert "@gmail.com" not in content or "support" in content
