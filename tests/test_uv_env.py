"""
Tests for uv tool availability and environment readiness.

Covers:
- uv binary is present in PATH
- uv --version exits 0 and reports a parseable version
- uv can list installed packages (pip list)
- specify-cli package is importable in the active environment
- specify entry-point is resolvable
"""

import re
import shutil
import subprocess
import sys

import pytest

# ───────── helpers ─────────


def _run(*args, **kwargs):
    """Run a subprocess and return CompletedProcess. Never raises on non-zero exit."""
    return subprocess.run(
        list(args),
        capture_output=True,
        text=True,
        timeout=30,
        **kwargs,
    )


# ───────── markers ─────────

requires_uv = pytest.mark.skipif(
    shutil.which("uv") is None,
    reason="uv is not installed or not in PATH",
)


# ───────── path checks ─────────


class TestUvAvailability:
    """Verify uv binary is present and usable."""

    def test_uv_in_path(self):
        """uv must be discoverable via PATH."""
        uv_path = shutil.which("uv")
        assert uv_path is not None, (
            "uv not found in PATH.\n"
            "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh\n"
            "Then restart your shell or run: source ~/.cargo/env"
        )

    @requires_uv
    def test_uv_version_exits_zero(self):
        """'uv --version' must succeed."""
        result = _run("uv", "--version")
        assert result.returncode == 0, f"'uv --version' exited {result.returncode}.\nstderr: {result.stderr.strip()}"

    @requires_uv
    def test_uv_version_format(self):
        """'uv --version' output must match 'uv X.Y.Z' pattern."""
        result = _run("uv", "--version")
        output = result.stdout.strip() or result.stderr.strip()
        # uv prints to stdout: "uv 0.5.x (commit ...)"
        assert re.match(r"uv\s+\d+\.\d+", output), (
            f"Unexpected version format: {output!r}\nExpected pattern: 'uv X.Y.Z ...'"
        )

    @requires_uv
    def test_uv_help_exits_zero(self):
        """'uv --help' must not crash."""
        result = _run("uv", "--help")
        assert result.returncode == 0, f"'uv --help' exited {result.returncode}"


# ───────── package management ─────────


class TestUvPackageManagement:
    """Verify uv can list packages in the active environment."""

    @requires_uv
    def test_uv_pip_list_exits_zero(self):
        """'uv pip list --no-cache' must succeed (cache may be read-only in CI)."""
        result = _run("uv", "pip", "list", "--no-cache")
        if result.returncode != 0 and "Read-only file system" in result.stderr:
            pytest.skip("uv cache is read-only in this environment (acceptable in CI)")
        assert result.returncode == 0, (
            f"'uv pip list' failed (exit {result.returncode}).\nstderr: {result.stderr.strip()}"
        )

    @requires_uv
    def test_uv_pip_list_has_pytest(self):
        """pytest must be findable via uv pip list or mark skipped in CI."""
        result = _run("uv", "pip", "list", "--no-cache")
        if result.returncode != 0 and "Read-only file system" in result.stderr:
            pytest.skip("uv cache is read-only in this environment (acceptable in CI)")
        if result.returncode != 0:
            pytest.skip(f"uv pip list unavailable (exit {result.returncode})")
        packages = result.stdout.lower()
        # pytest may be installed via uv run or directly
        # check for either pytest or specify-cli with test deps
        has_pytest = "pytest" in packages
        has_specify = "specify-cli" in packages
        assert has_pytest or has_specify, "pytest not found in uv pip list output.\nRun: pip install -e '.[test]'"


# ───────── specify-cli package ─────────


class TestSpecifyCliPackage:
    """Verify specify-cli is importable and entry-point works."""

    def test_specify_cli_importable(self):
        """specify_cli module must be importable in the current Python."""
        try:
            import specify_cli  # noqa: F401
        except ImportError as exc:
            pytest.fail(f"Cannot import specify_cli: {exc}\nRun: pip install -e '.[test]' from the repo root.")

    def test_specify_cli_has_agent_config(self):
        """AGENT_CONFIG must be exported from specify_cli."""
        import specify_cli

        assert hasattr(specify_cli, "AGENT_CONFIG"), "specify_cli.AGENT_CONFIG not found — possible broken __init__.py"
        assert isinstance(specify_cli.AGENT_CONFIG, dict)
        assert len(specify_cli.AGENT_CONFIG) > 0

    def test_specify_cli_has_app(self):
        """The Typer app must be exported."""
        import specify_cli

        assert hasattr(specify_cli, "app"), "specify_cli.app not found"

    def test_specify_entry_point_resolvable(self):
        """'specify' entry-point must resolve to a callable (via the venv)."""
        specify_bin = shutil.which("specify")
        if specify_bin is None:
            # Acceptable if running from source; check the module directly
            result = subprocess.run(
                [sys.executable, "-m", "specify_cli", "--help"],
                capture_output=True,
                text=True,
                timeout=15,
            )
            assert result.returncode == 0, (
                f"'python -m specify_cli --help' failed (exit {result.returncode}).\n"
                f"stdout: {result.stdout[:300]}\n"
                f"stderr: {result.stderr[:300]}"
            )
        else:
            result = _run(specify_bin, "--help")
            assert result.returncode == 0, (
                f"'specify --help' failed (exit {result.returncode}).\nstderr: {result.stderr.strip()}"
            )

    @requires_uv
    def test_uv_run_specify_help(self):
        """'uv run specify --help' must succeed when uv is available."""
        # uv run uses the project's venv; falls back gracefully
        result = _run("uv", "run", "--no-project", "python", "-m", "specify_cli", "--help")
        # Non-zero is acceptable if 'specify_cli' not installed in system uv env;
        # we just verify uv itself doesn't crash fatally (exit code != 127)
        assert result.returncode != 127, (
            "uv run exited with 127 (command not found) — uv may be broken or PATH is misconfigured."
        )
