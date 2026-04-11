import os
import tempfile

from click.testing import CliRunner
from tca.cli import main


class TestCLI:
    def _config_path(self):
        return os.path.join(os.path.dirname(__file__), "..", "examples", "config.yaml")

    def test_run_command(self):
        runner = CliRunner()
        result = runner.invoke(main, ["run", self._config_path(), "--steps", "10"])
        assert result.exit_code == 0, result.output
        assert "average_speed" in result.output or "flow" in result.output

    def test_run_with_output(self):
        runner = CliRunner()
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            outpath = f.name
        try:
            result = runner.invoke(main, ["run", self._config_path(),
                                          "--steps", "10", "--output", outpath])
            assert result.exit_code == 0, result.output
            assert os.path.exists(outpath)
        finally:
            if os.path.exists(outpath):
                os.unlink(outpath)

    def test_invalid_config(self):
        runner = CliRunner()
        result = runner.invoke(main, ["run", "nonexistent.yaml"])
        assert result.exit_code != 0
