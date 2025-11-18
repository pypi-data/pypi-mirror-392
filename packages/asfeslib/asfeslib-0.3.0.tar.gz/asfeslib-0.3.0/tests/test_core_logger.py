import io
import sys
from asfeslib.core.logger import Logger

def test_logger_basic(capsys):
    log = Logger(name="pytest-test")
    log.info("Test info")
    log.debug("Test debug")
    log.error("Test error")

    captured = capsys.readouterr()
    output = captured.err or captured.out

    assert "Test info" in output
    assert "Test error" in output
    assert "[INFO]" in output

def test_logger_no_duplicate_handlers(capsys):
    log1 = Logger(name="pytest-dup")
    log2 = Logger(name="pytest-dup")

    log1.info("Once only")

    captured = capsys.readouterr()
    output = captured.err or captured.out

    assert output.count("Once only") == 1


def test_logger_log_to_file(tmp_path):
    log_path = tmp_path / "test_logger.log"

    log = Logger(name="pytest-file", log_to_file=True, log_file=log_path)
    log.info("File info")
    log.error("File error")

    content = log_path.read_text(encoding="utf-8")

    assert "File info" in content
    assert "File error" in content
    assert "[INFO]" in content