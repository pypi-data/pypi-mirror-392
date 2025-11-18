# test_logging_setup.py
import logging
from logging.handlers import RotatingFileHandler

from bolt2.utils import setupRootLogger


def test_setup_root_logger_adds_rotating_file_handler(tmp_path):
  log_file = tmp_path / "app.log"
  logger = logging.getLogger()

  setupRootLogger(str(log_file))

  assert logger.level == logging.INFO

  handlers = logger.handlers
  assert any(isinstance(h, RotatingFileHandler) for h in handlers)

  handler = next(h for h in handlers if isinstance(h, RotatingFileHandler))
  assert handler.baseFilename == str(log_file)

  logger.info("hello world")
  handler.flush()
  content = log_file.read_text()
  assert "hello world" in content
