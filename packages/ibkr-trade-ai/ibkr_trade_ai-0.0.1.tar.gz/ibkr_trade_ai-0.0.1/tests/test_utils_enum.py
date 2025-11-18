import pytest

import bolt2.utils as utils


def test_api_type_enum_values():
  assert utils.EventType.EXEC_DETAILS.value == 0
  assert utils.EventType.ORDER_UPDATE.value == 1
  assert utils.EventType.OPEN_ORDER.value == 2
  assert utils.EventType.COMPLETED_ORDER.value == 3
  assert utils.EventType.CONNECTION_CLOSED.value == 4
  assert utils.EventType.COMMISSION_DETAILS.value == 5


def test_order_type_enum_values():
  assert utils.OrderType.LIMIT.value == "LMT"
  assert utils.OrderType.MARKET.value == "MKT"


def test_trade_state_enum_values():
  assert utils.TradeState.PendingCancel.value == "PendingCancel"
  assert utils.TradeState.PendingSubmit.value == "PendingSubmit"
  assert utils.TradeState.PreSubmitted.value == "PreSubmitted"
  assert utils.TradeState.Submitted.value == "Submitted"
  assert utils.TradeState.Cancelled.value == "Cancelled"
  assert utils.TradeState.Filled.value == "Filled"
  assert utils.TradeState.Inactive.value == "Inactive"
  assert utils.TradeState.CustomSubmitInitiated.value == "CustomSubmitInitiated"
  assert utils.TradeState.CustomCancelInitiated.value == "CustomCancelInitiated"
