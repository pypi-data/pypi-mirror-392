import asyncio
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, ClassVar, Optional

from diskcache import Cache
from ibapi.const import UNSET_DECIMAL
from ibapi.contract import Contract
from ibapi.execution import Execution
from ibapi.order import Order
from ibapi.order_state import OrderState

from bolt2.utils import (OrderType, TradeState, getCurrTimeMs, inUserThread,
                         tradeStateValueSet)


@inUserThread
def createOrderRef(order: Order, contract: Contract, bid: int,
                   slot: Optional[str]) -> str:
  d = [
      ('q', order.totalQuantity),
      ('oid', order.orderId),
      ('bid', bid),
      ('exch', contract.exchange),
  ]
  if slot:
    d.append(('slot', order.lmtPrice))
  if order.orderType == OrderType.LIMIT.value:
    d.append(('lp', order.lmtPrice))
  return f"api{order.action}|" + "|".join(f"{k}={v}" for k, v in d)


@inUserThread
def parseOrderRef(orderRef: str) -> SimpleNamespace:
  action, *rest = orderRef.split("|")
  assert action in ('apiBUY', 'apiSELL'), action
  ddd = dict([[*x.split('=')] for x in rest])
  res = SimpleNamespace(ddd)
  res.lmtPrice = None if 'lp' not in ddd else float(res.lp)
  res.orderId, res.boltId = int(res.oid), int(res.bid)
  res.exchange = res.exch if 'exch' in ddd else None
  res.totalQuantity = int(res.q)
  res.slot = None if 'slot' not in ddd else res.slot
  res.action = 'BUY' if action == 'apiBUY' else 'SELL'
  return res


@inUserThread
def prepareQty(q) -> float:
  return float(q) if q and q != UNSET_DECIMAL else 0.0


@dataclass
class Trade_:
  # unique id generated randomly as opposed sequence orderId.
  boltId: int = -1  # required
  orderId: int = -1
  clientId: int = -1
  permId: int = -1
  accountNumStr: str = ""
  orderRef: str = ""
  order: Optional[Order] = None
  status: str = ""
  filledQty: float = 0.0
  totalQuantity: float = 0.0
  side: str = ""
  slot: str = ""
  exchange: str = ""
  lmtPrice: float = -1
  executions: dict[str, Execution] = field(default_factory=dict)
  contract: Optional[Contract] = None


class Trade(Trade_):
  # NOTE -
  # Keep only class variables in this class.
  _bid2trade: ClassVar[dict[int, Trade]] = field(default_factory=dict)
  _cache: ClassVar[Optional[Cache]] = None

  @classmethod
  @inUserThread
  def gg(cls,
         boltId: Optional[int] = None,
         order: Optional[Order] = None,
         execution: Optional[Execution] = None) -> Trade:
    if boltId is None and (order or execution):
      permId = order.permId if order else execution.permId  # type: ignore
      assert permId > 0, permId
      assert cls._cache, "_cache is not set"
      boltId = int(cls._cache.get(f"permId2boltId_{permId}", None) or 0)  # type: ignore
      if boltId is None:
        orderRef = order.orderRef if order else execution.orderRef  # type: ignore
        boltId = parseOrderRef(orderRef=orderRef).boltId
        cls._cache.set(f"permId2boltId_{permId}", boltId)  # cache it here
    assert boltId and isinstance(boltId, int) and boltId > 0, boltId
    if boltId not in cls._bid2trade:
      # create a new instance of trade object
      t = Trade(boltId=boltId, order=order)
      _ = t.updateExecution(execution=execution) if execution else None
      cls._bid2trade[boltId] = t
    return cls._bid2trade[boltId]

  @inUserThread
  def fillValuesList(self, t: Any):
    for x in ('orderId', 'permId', 'clientId'):
      if getattr(self, x) <= 0 and hasattr(t, x):
        setattr(self, x, getattr(t, x))
    for x in ('side', 'orderRef', 'exchange', 'slot'):
      if not (getattr(self, x)) and hasattr(t, x):
        setattr(self, x, getattr(t, x))
    if not (self.side) and hasattr(t, 'action'):
      self.side = t.action
    if self.totalQuantity <= 0 and hasattr(t, 'totalQuantity'):
      self.totalQuantity = t.totalQuantity

  async def writeTrade(self):
    k = f"trade_{self.boltId}"
    assert Trade._cache
    vv = Trade._cache.get(k)
    vv = SimpleNamespace(vv) if vv and isinstance(vv, dict) else None
    if not (vv) or not (vv.orderId == self.orderId \
                        and vv.permId == self.permId \
                          and int(vv.totalQuantity) == int(self.totalQuantity) \
                            and int(vv.filledQty) == int(self.filledQty) \
                              and vv.status == self.status):
      vv = ('orderId', 'permId', 'clientId', 'orderRef', 'boltId', 'filledQty',
            'exchange', 'totalQuantity', 'lmtPrice', 'status', 'side', 'slot')
      vv = {k: getattr(self, k) for k in vv if hasattr(self, k)}
      vv['execIdList'] = [e.execId for e in self.executions.values()]
      Trade._cache.set(k, vv)
      k = f"backup_trade_{self.boltId}_{getCurrTimeMs()}"
      Trade._cache.set(k, vv)

  async def readTrade(self):
    k = f"trade_{self.boltId}"
    assert Trade._cache
    vv = Trade._cache.get(k)
    if vv and isinstance(vv, dict):
      execIdList = vv.pop('execIdList')
      for k, v in vv.items():
        setattr(self, k, v)
      for execId in execIdList:
        e = Execution()
        e.execId = execId
        await self.readExecution(e)
        self.updateExecution(execution=e)

  async def writeExecution(self, execution: Execution):
    k = f"execution_{execution.execId}"
    assert Trade._cache
    if k not in Trade._cache:
      vv = ('orderId', 'permId', 'clientId', 'orderRef', 'execId', 'shares', 'exchange',
            'acctNumber', 'avgPrice', 'price', 'side')
      vv = {k: getattr(execution, k) for k in vv if hasattr(execution, k)}
      Trade._cache.set(k, vv)

  async def readExecution(self, execution: Execution):
    k = f"execution_{execution.execId}"
    assert Trade._cache
    vv = Trade._cache.get(k)
    if vv and isinstance(vv, dict):
      for k, v in vv.items():
        setattr(execution, k, v)

  @inUserThread
  def updateExecution(self, execution: Execution) -> Trade:
    self.executions[execution.execId] = execution
    q: float = sum(float(e.shares) for e in self.executions.values())
    self.filledQty = max(q, self.filledQty)
    self.fillValuesList(execution)
    return self

  @inUserThread
  def updateOrderDetails(self, order: Order, orderState: OrderState) -> Trade:
    assert orderState in tradeStateValueSet, orderState
    self.order = order
    self.status, self.side = orderState.status, order.action
    self.filledQty = max(prepareQty(order.filledQuantity), self.filledQty)
    self.fillValuesList(order)
    return self

  @inUserThread
  def updateOrderStatus(self, orderStatusData: SimpleNamespace) -> Trade:
    assert orderStatusData.status in tradeStateValueSet, orderStatusData
    self.status = orderStatusData.status
    self.filledQty = max(self.filledQty, prepareQty(orderStatusData.filledQty))
    self.fillValuesList(orderStatusData)
    return self

  @inUserThread
  @property
  def isDone(self) -> bool:
    if self.totalQuantity > 0 and int(self.totalQuantity) == int(self.filledQty):
      return True
    return self.status in (TradeState.Cancelled.value, TradeState.Filled.value,
                           TradeState.DirtyCancelled.value)

  @inUserThread
  @property
  def avgFillPrice(self) -> float:
    raise NotImplementedError

  @inUserThread
  async def cancelOrder(self, client):
    if self.isDone:
      return
    if (self.status and self.status
        in (TradeState.PendingCancel.value, TradeState.CustomCancelInitiated.value,
            TradeState.DirtyCancelled.value)):
      return
    self.status = TradeState.CustomCancelInitiated.value
    assert self.orderId > 0, self.orderId
    await client.cancelOrderAsync(orderId=self.orderId)
    await asyncio.sleep(0.05)
