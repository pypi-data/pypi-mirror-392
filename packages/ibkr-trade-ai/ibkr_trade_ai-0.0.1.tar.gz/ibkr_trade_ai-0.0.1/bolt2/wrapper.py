import asyncio
import threading
import time
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, Optional

from ibapi.client import EClient
from ibapi.common import OrderId
from ibapi.contract import Contract
from ibapi.execution import Execution, ExecutionFilter
from ibapi.order import Order
from ibapi.order_cancel import OrderCancel
from ibapi.order_state import OrderState
from ibapi.wrapper import EWrapper

from bolt2.utils import EventType, inApiThread, inUserThread, setApiThread


class TradeWrapper(EWrapper, EClient):
  """
  Minimal trading code.

  The following support will be added:
    - getting contract details
    - options
    - account positions
    - account summary
    - portfolio updates
    - market data
    - different order type
  """

  @inUserThread
  def __init__(self, q: asyncio.Queue, timeout: int = 30):
    EWrapper.__init__(self)
    EClient.__init__(self, wrapper=self)
    # NOTE - Ensure that all of the below methods are used in User Thread.
    self.q: asyncio.Queue = q
    self.loop = asyncio.get_running_loop()
    self.response_events = {}
    self.response_data = {}
    self.timeout = timeout
    self.api_thread = None
    self.nextId = -1

  @inUserThread
  async def reConnectAsync(self, host: str, port: int, client_id: int) -> bool:
    self.connect(host, port, client_id)
    # wait for the connection to estabilish
    endTime = time.time() + self.timeout
    while not self.isConnected() and time.time() < endTime:
      await asyncio.sleep(0.5)
    if not self.isConnected():
      raise ConnectionError("Could not connect with TWS API.")
    # Create a thread for message processing
    self.api_thread = threading.Thread(target=self.run)
    self.api_thread.daemon = True
    self.api_thread.start()
    setApiThread(self.api_thread.ident)
    return bool(self.isConnected())

  @inUserThread
  async def waitForEvent(self, eventName: str, reqId: int = -1) -> Optional[Any]:
    event_key = f"{eventName}_{reqId}"
    if event_key not in self.response_events:
      self.response_events[event_key] = asyncio.Event()
    event: asyncio.Event = self.response_events[event_key]
    await event.wait()
    if event_key in self.response_data:
      return self.response_data[event_key]

  @inApiThread
  def putq(self, item):
    future = asyncio.run_coroutine_threadsafe(self.q.put(item), self.loop)
    # Wait for the put operation to complete. It should be quick as q size is unlimited
    _ = future.result()

  @inUserThread
  async def setEventAsync(self, eventName: str, reqId: int = -1, val: Any = None):
    event_key = f"{eventName}_{reqId}"
    self.response_data[event_key] = val
    if event_key in self.response_events:
      self.response_events[event_key].set()

  @inApiThread
  def setEvent(self, eventName: str, reqId: int = -1, val: Any = None):
    future = asyncio.run_coroutine_threadsafe(self.setEventAsync(eventName, reqId, val),
                                              self.loop)
    # block until the result is ready!
    _ = future.result()

  @inApiThread
  def nextValidId(self, orderId: int):
    super().nextValidId(orderId)
    self.setEvent("nextValidId", val=orderId)

  @inUserThread
  async def getNextValidId(self) -> Optional[int]:
    self.reqIds(-1)
    return await self.waitForEvent("nextValidId")

  @inApiThread
  def execDetails(self, reqId: int, contract: Contract, execution: Execution):
    self.setEvent("orderStatus", execution.orderId, execution.permId)
    self.putq((EventType.EXEC_DETAILS, execution))
    super().execDetails(reqId=reqId, contract=contract, execution=execution)

  @inApiThread
  def execDetailsEnd(self, reqId: int):
    self.setEvent("execDetailsEnd", reqId)
    super().execDetailsEnd(reqId=reqId)

  @inUserThread
  async def reqExecutionsAsync(self, execFilter=None, wait=True):
    if (reqId := await self.getNextValidId()):
      execFilter = ExecutionFilter() if not (execFilter) else execFilter
      self.reqExecutions(reqId, execFilter=execFilter)
      if wait:
        await self.waitForEvent("execDetailsEnd", reqId)

  @inApiThread
  def openOrder(self, orderId: OrderId, contract: Contract, order: Order,
                orderState: OrderState):
    self.putq((EventType.OPEN_ORDER, order))
    super().openOrder(orderId, contract, order, orderState)
    self.setEvent("orderStatus", orderId, order.permId)

  @inApiThread
  def openOrderEnd(self):
    super().openOrderEnd()
    self.setEvent("openOrderEnd")

  @inUserThread
  async def openOrderAsync(self, wait=True):
    self.reqOpenOrders()
    if wait:
      await self.waitForEvent("openOrderEnd")

  @inApiThread
  def orderStatus(self, orderId: OrderId, status: str, filled: Decimal,
                  remaining: Decimal, avgFillPrice: float, permId: int, parentId: int,
                  lastFillPrice: float, clientId: int, whyHeld: str,
                  mktCapPrice: float):
    orderStatusData = SimpleNamespace(orderId=orderId,
                                      status=status,
                                      filled=filled,
                                      remaining=remaining,
                                      clientId=clientId,
                                      permId=permId,
                                      lastFillPrice=lastFillPrice,
                                      parentId=parentId)
    self.putq((EventType.ORDER_UPDATE, orderStatusData))
    super().orderStatus(orderId, status, filled, remaining, avgFillPrice, permId,
                        parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)
    self.setEvent("orderStatus", orderId, permId)

  @inApiThread
  def completedOrder(self, contract: Contract, order: Order, orderState: OrderState):
    self.putq((EventType.COMPLETED_ORDER, order, orderState))
    super().completedOrder(contract, order, orderState)
    self.setEvent("orderStatus", order.orderId, order.permId)

  @inApiThread
  def completedOrdersEnd(self):
    super().completedOrdersEnd()
    self.setEvent("completedOrdersEnd")

  @inUserThread
  async def completedOrdersAsync(self, wait=True, apiOnly=True):
    if (reqId := await self.getNextValidId()):
      self.reqCompletedOrders(apiOnly=apiOnly)
      if wait:
        await self.waitForEvent("completedOrdersEnd", reqId)

  @inUserThread
  async def placeOrderAsync(self, contract: Contract, order: Order,
                            orderId: Optional[int]):
    if orderId is None:
      orderId = await self.getNextValidId()
    assert orderId and orderId > 0, orderId
    order.orderId = orderId
    self.placeOrder(orderId, contract, order)
    return await self.waitForEvent("orderStatus", orderId)

  @inUserThread
  async def cancelOrderAsync(self, orderId):
    self.cancelOrder(orderId=orderId, orderCancel=None)  # type: ignore
    return self.waitForEvent("orderStatus", orderId)

  @inApiThread
  def connectionClosed(self):
    if self.api_thread:
      self.api_thread.join()
    setApiThread(-1)
    self.putq((EventType.CONNECTION_CLOSED))

  # @inApiThread
  # def contractDetails(self, reqId: int, contractDetails: ContractDetails):
  #   # TODO - implement this function
  #   super().contractDetails(reqId, contractDetails)

  # @inApiThread
  # def contractDetailsEnd(self, reqId: int):
  #   self.setEvent("contractDetailsEnd", reqId)
  #   super().contractDetailsEnd(reqId)

  # @inUserThread
  # async def getContractDetails(self, contract):
  #   reqId = await self.getNextValidId()
  #   self.reqContractDetails(reqId, contract)
  #   return self.waitForEvent("contractDetailsEnd", reqId)
