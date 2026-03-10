"""Tests for code cleanup — task #029.

Validates that the codebase meets quality standards:
- No print() in src/ (except app.py Streamlit usage)
- No orphan TODO/FIXME/HACK/XXX comments
- Module docstrings present in all src/*.py files
- Public functions have docstrings
- No unused imports (ruff F401)
- ruff check passes cleanly
- Import blocks properly sorted (ruff I001)
- No lines exceed 100 characters (ruff E501)
"""

import ast
import re
import subprocess
from pathlib import Path

import pytest

SRC_DIR = Path("src")
TESTS_DIR = Path("tests")
# app.py is excluded from print() check because it uses Streamlit (st.*)
PRINT_EXCLUDED_FILES = {"app.py"}


class TestNoPrintStatements:
    """#029 — No print() calls in src/ (except app.py)."""

    def _get_src_files(self):
        return sorted(f for f in SRC_DIR.glob("*.py") if f.name not in PRINT_EXCLUDED_FILES)

    def test_no_print_in_src_modules(self):
        """Each src/*.py file (except app.py) must not contain print() calls."""
        violations = []
        for filepath in self._get_src_files():
            source = filepath.read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    if isinstance(func, ast.Name) and func.id == "print":
                        violations.append(f"{filepath}:{node.lineno}")
        assert violations == [], f"print() found in src/: {violations}"

    def test_app_py_no_bare_print(self):
        """app.py should only use st.* calls, not bare print()."""
        app_path = SRC_DIR / "app.py"
        if not app_path.exists():
            pytest.skip("app.py does not exist")
        source = app_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        bare_prints = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "print":
                    bare_prints.append(node.lineno)
        assert bare_prints == [], f"Bare print() in app.py at lines: {bare_prints}"


class TestNoOrphanComments:
    """#029 — No TODO/FIXME/HACK/XXX orphan comments."""

    PATTERN = re.compile(r"#\s*(TODO|FIXME|HACK|XXX)\b", re.IGNORECASE)

    def _scan_dir(self, directory):
        violations = []
        for filepath in sorted(directory.rglob("*.py")):
            for i, line in enumerate(filepath.read_text(encoding="utf-8").splitlines(), 1):
                if self.PATTERN.search(line):
                    violations.append(f"{filepath}:{i}: {line.strip()}")
        return violations

    def test_no_orphan_comments_in_src(self):
        """No TODO/FIXME/HACK/XXX comments in src/."""
        violations = self._scan_dir(SRC_DIR)
        assert violations == [], f"Orphan comments in src/: {violations}"

    def test_no_orphan_comments_in_tests(self):
        """No TODO/FIXME/HACK/XXX comments in tests/."""
        violations = self._scan_dir(TESTS_DIR)
        assert violations == [], f"Orphan comments in tests/: {violations}"


class TestModuleDocstrings:
    """#029 — Every src/*.py file must have a module-level docstring."""

    def test_all_src_modules_have_docstrings(self):
        """Each src/*.py must start with a module docstring."""
        missing = []
        for filepath in sorted(SRC_DIR.glob("*.py")):
            source = filepath.read_text(encoding="utf-8")
            tree = ast.parse(source)
            docstring = ast.get_docstring(tree)
            if not docstring:
                missing.append(str(filepath))
        assert missing == [], f"Missing module docstrings: {missing}"


class TestPublicFunctionDocstrings:
    """#029 — Every public function in src/ must have a docstring."""

    def test_all_public_functions_have_docstrings(self):
        """Public functions (not starting with _) must have docstrings."""
        missing = []
        for filepath in sorted(SRC_DIR.glob("*.py")):
            source = filepath.read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name.startswith("_"):
                        continue
                    ds = ast.get_docstring(node)
                    if not ds:
                        missing.append(f"{filepath}:{node.lineno} {node.name}")
        assert missing == [], f"Public functions missing docstrings: {missing}"


class TestRuffCompliance:
    """#029 — ruff check src/ tests/ must pass with zero errors."""

    def test_ruff_check_clean(self):
        """ruff check src/ tests/ returns 0 errors, 0 warnings."""
        result = subprocess.run(
            ["ruff", "check", "src/", "tests/"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"ruff check failed with {result.returncode}:\n{result.stdout}\n{result.stderr}"
        )

    def test_no_unused_imports(self):
        """No F401 (unused import) violations detected by ruff."""
        result = subprocess.run(
            ["ruff", "check", "src/", "tests/", "--select", "F401"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Unused imports found:\n{result.stdout}"

    def test_imports_sorted(self):
        """No I001 (unsorted imports) violations detected by ruff."""
        result = subprocess.run(
            ["ruff", "check", "src/", "tests/", "--select", "I001"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Unsorted imports found:\n{result.stdout}"

    def test_no_lines_too_long(self):
        """No E501 (line too long) violations detected by ruff."""
        result = subprocess.run(
            ["ruff", "check", "src/", "tests/", "--select", "E501"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Lines too long found:\n{result.stdout}"


class TestNoRegression:
    """#029 — Full test suite must still pass (no regression)."""

    def test_full_suite_passes(self):
        """Running pytest on the full suite yields zero failures."""
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/", "-q", "--tb=no",
             "--ignore=tests/test_code_cleanup.py"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"Test suite has failures:\n{result.stdout}\n{result.stderr}"
        )
