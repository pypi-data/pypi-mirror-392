import asyncio
import secrets
from decimal import Decimal
from typing import Any, Optional

from diskcache import Cache
from ibapi.client import Contract
from ibapi.execution import Execution
from ibapi.order import Order
from ibapi.order_state import OrderState

from bolt2.trade import Trade, createOrderRef
from bolt2.utils import (EventType, OrderType, TradeState, getCurrTimeMs, inUserThread,
                         isOvernightTradingHourMin, logd, logi)
from bolt2.wrapper import TradeWrapper


@inUserThread
def createContract(sym: str, exchange: str) -> Contract:
  c = Contract()
  c.symbol = sym
  c.currency = 'USD'
  c.exchange = exchange
  c.secType = 'STK'  # Stock
  return c


@inUserThread
def createOrder(action: str, qty: float, orderId: int,
                lmtPrice: Optional[float]) -> Order:
  o = Order()
  o.action = action
  o.totalQuantity = Decimal(qty)
  o.orderId = orderId
  if lmtPrice:
    o.lmtPrice = round(lmtPrice, 2)
    o.orderType = OrderType.LIMIT.value
  else:
    o.orderType = OrderType.MARKET.value
  o.transmit = True
  o.orderRef = ""
  o.tif = "OND"
  o.outsideRth = True
  return o


class TradeManager:

  @inUserThread
  def __init__(self, cache: Cache):
    self.q: asyncio.Queue = asyncio.Queue(maxsize=0)
    self.client: TradeWrapper = TradeWrapper(self.q, timeout=30)
    self.cache: Cache = cache
    self.clientId = 0
    self.callbacks: list[Any] = []
    Trade._cache = cache

  @inUserThread
  async def placeOrderAsync(self, sym: str, lmtPrice: Optional[float], qty: int,
                            action: str, slot: Optional[str]):
    exchange = "OVERNIGHT" if isOvernightTradingHourMin() else "SMART"
    logi(f"placeOrderAsync: {action} {sym} {qty}@{lmtPrice}@{exchange}")
    # pre-conditions
    assert action in ('BUY', 'SELL'), action
    assert qty >= 1, qty
    if exchange == 'OVERNIGHT':
      assert lmtPrice and lmtPrice >= 0.01, lmtPrice
    # create order
    orderId: Optional[int] = await self.client.getNextValidId()
    assert orderId, orderId
    o: Order = createOrder(action=action, qty=qty, orderId=orderId, lmtPrice=lmtPrice)
    c: Contract = createContract(sym=sym, exchange=exchange)
    state: OrderState = OrderState()
    state.status = TradeState.CustomSubmitInitiated.value
    boltId = secrets.randbits(64)
    o.orderRef = createOrderRef(order=o, contract=c, bid=boltId, slot=slot)
    self.cache.set(f"orderId2boltId_{orderId}_{self.clientId}", boltId)
    Trade(boltId=boltId).updateOrderDetails(order=o, orderState=state)
    permId = await self.client.placeOrderAsync(contract=c, order=o, orderId=orderId)
    if permId:
      self.cache.set(f"permId2boltId_{permId}", boltId)

  @inUserThread
  async def runLoop(self):
    shouldRun = True
    cache = self.cache
    while shouldRun:
      await asyncio.sleep(0.001)
      msg = self.q.get()
      logd(f"TradeManager: queue received {msg}")
      trade = None
      match msg:
        case (EventType.EXEC_DETAILS, execution):
          if execution.orderRef.startswith("api"):
            trade = Trade.gg(execution=execution).updateExecution(execution)
            await trade.writeExecution(execution=execution)
        case (EventType.OPEN_ORDER | EventType.COMPLETED_ORDER, order, orderState):
          if order.orderRef.startswith("api"):
            trade = Trade.gg(order=order).updateOrderDetails(order, orderState)
        case (EventType.ORDER_UPDATE, orderStatusData):
          boltId = cache.get(f"permId2boltId_{orderStatusData.permId}", None)
          if boltId and isinstance(boltId, int):
            trade = Trade.gg(boltId=boldId).updateOrderStatus(orderStatusData)
          else:
            boltId = cache.get(f"orderId2boltId_{orderId}_{orderStatusData.clientId}")
            assert boltId and isinstance(boltId, int), boltId
            trade = Trade.gg(boltId=boltId).updateOrderStatus(orderStatusData)
        case (EventType.CONNECTION_CLOSED, *rest):
          shouldRun = False

      if not (trade) and shouldRun:
        logd(f"TradeManager: likely ignored {msg}")

      if self.callbacks and trade:
        await trade.writeTrade()
        _ = [cb(trade) for cb in self.callbacks]
