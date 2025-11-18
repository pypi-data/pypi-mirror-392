import logging
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from logging.handlers import RotatingFileHandler
from typing import Optional

import pytz


class EventType(Enum):
  EXEC_DETAILS = 0
  ORDER_UPDATE = 1
  OPEN_ORDER = 2
  COMPLETED_ORDER = 3
  CONNECTION_CLOSED = 4
  COMMISSION_DETAILS = 5


class OrderType(Enum):
  LIMIT = "LMT"
  MARKET = "MKT"


class TradeState(Enum):
  PendingCancel = "PendingCancel"
  PendingSubmit = "PendingSubmit"
  PreSubmitted = "PreSubmitted"
  Submitted = "Submitted"
  Cancelled = "Cancelled"
  Filled = "Filled"
  Inactive = "Inactive"
  CustomSubmitInitiated = "CustomSubmitInitiated"
  CustomCancelInitiated = "CustomCancelInitiated"
  # no open order(s) for this trade, so we mark it as dirty.
  DirtyCancelled = "DirtyCancelled"


tradeStateValueSet = set([x.value for x in TradeState])

# EST is the daylight time for New_York. The trading firms follow EST.
_tz_est = pytz.timezone("America/New_York")


def getCurrTimeSeconds():
  return time.time_ns() // 1_000_000_000


def getCurrTimeMs():
  return int(time.time_ns() // 1000_000)


def getCurrTimeNs():
  return int(time.time_ns())


def getCurrTimeHourMinEST(now=None) -> int:
  if now is None:
    now = datetime.now(_tz_est)
  return now.hour * 100 + now.minute


def isRegularTradingHourMin(hour_min_est: Optional[int] = None) -> bool:
  if hour_min_est is None:
    hour_min_est = getCurrTimeHourMinEST()
  # 930 AM to 4 PM EST
  return 930 <= hour_min_est <= 1600


def isOvernightTradingHourMin(hour_min_est: Optional[int] = None) -> bool:
  if hour_min_est is None:
    hour_min_est = getCurrTimeHourMinEST()
  return 2000 <= hour_min_est <= 2400 or (0 <= hour_min_est < 350)


# ---- BELOW ARE NOT USED OFTEN ---

_logger = logging.getLogger("__boltapp__")
_logger.addHandler(logging.StreamHandler(sys.stderr))
_logger.setLevel(logging.INFO)
logi = _logger.info
logd = _logger.debug
loge = _logger.error

__user_thread_id: int = -1
__api_thread_id: int = -1


def setUserThread(id):
  global __user_thread_id
  assert __user_thread_id == -1, "not recommened to switch threads"
  __user_thread_id = id


def setApiThread(id):
  global __api_thread_id
  assert __api_thread_id == -1, "not recommened to switch threads"
  __api_thread_id = id


def inUserThread(func):
  assert __user_thread_id > 0, f"__user_thread_id is not set {__user_thread_id}"

  def wrapper(*args, **kwargs):
    print(f"entering func: {func.__name__}")
    tid = threading.get_ident()
    assert tid == __user_thread_id, f"tid={tid} != __user_thread_id={__user_thread_id}"
    result = func(*args, **kwargs)
    print(f"exiting func: {func.__name__}")
    return result

  return wrapper


def inApiThread(func):
  assert __api_thread_id > 0, f"__api_thread_id is not set {__api_thread_id}"

  def wrapper(*args, **kwargs):
    print(f"entering func: {func.__name__}")
    tid = threading.get_ident()
    assert tid == __api_thread_id, f"tid={tid} != __api_thread_id={__api_thread_id}"
    result = func(*args, **kwargs)
    print(f"exiting func: {func.__name__}")
    return result

  return wrapper


def setupRootLogger(filepath="./app.log"):
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)

  handler = RotatingFileHandler(
      filepath,
      maxBytes=500 * 1024 * 1024,  # 500 MB
      backupCount=10)
  s = "%(asctime)s [%(levelname)s] %(thread)d %(name)s %(filename)s/%(lineno)d  : %(message)s"
  formatter = logging.Formatter(s)
  handler.setFormatter(formatter)

  logger.addHandler(handler)
