import importlib
import threading

import pytest

import bolt2.utils as utils


@pytest.fixture
def fresh_utils():
  """
    Reload the module so its module-level globals (__user_thread_id, etc.)
    are reset for each test that needs a clean state.
    """
  importlib.reload(utils)
  return utils


def test_in_user_thread_raises_if_thread_id_not_set(fresh_utils):
  u = fresh_utils
  # __user_thread_id should be -1 after reload
  assert u.__dict__["__user_thread_id"] == -1

  with pytest.raises(AssertionError, match="__user_thread_id is not set"):

    @u.inUserThread
    def foo():
      return 1


def test_in_user_thread_decorator_runs_and_prints(fresh_utils, capsys):
  u = fresh_utils

  # Set the required user thread id first
  u.setUserThread(threading.get_ident())

  @u.inUserThread
  def add(a, b):
    return a + b

  result = add(1, 2)
  assert result == 3

  captured = capsys.readouterr()
  # function prints same line twice (before and after)
  assert captured.out.count("entering func: add") == 1
  assert captured.out.count("exiting func: add") == 1


def test_in_api_thread_raises_if_thread_id_not_set(fresh_utils):
  u = fresh_utils
  assert u.__dict__["__api_thread_id"] == -1

  with pytest.raises(AssertionError, match="__api_thread_id is not set"):

    @u.inApiThread
    def bar():
      return 1


def test_in_api_thread_decorator_runs_and_prints(fresh_utils, capsys):
  u = fresh_utils

  u.setApiThread(threading.get_ident())

  @u.inApiThread
  def mul(a, b):
    return a * b

  result = mul(3, 4)
  assert result == 12

  captured = capsys.readouterr()
  assert captured.out.count("entering func: mul") == 1
  assert captured.out.count("exiting func: mul") == 1
