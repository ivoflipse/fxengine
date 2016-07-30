class Event(object):
    pass


class TickEvent(Event):
    """
    Events with prices
        Attributes:
        instrument: e.g. EUR_USD
        time: timestamp from price
        bid: Bid price
        ask: Ask price
    """
    def __init__(self, instrument, time, bid, ask):
        self.type = 'TICK'
        self.instrument = instrument
        self.time = time
        self.bid = bid
        self.ask = ask

    def __str__(self):
        return "type: {}, instrument: {}, time: {}, bid: {}, ask: {}".format(
            self.type, self.instrument, self.time, self.bid, self.ask
        )

    def __repr__(self):
        return str(self)


class SignalEvent(Event):
    """
    Events for good trading opportunities if they fit in our risk
    management
    Attributes
        instrument: e.g. EUR_USD
        side: 'LONG' or 'SHORT'
        price: callable
    """
    def __init__(self, instrument, side, current_price, current_time, buy=None, expiry=None):
        self.type = 'SIGNAL'
        self.instrument = instrument
        self.side = side
        self.current_price = current_price
        self.current_time = current_time
        self.buy = buy
        self.expiry = expiry

    def __str__(self):
        return "type: {}, instrument: {}, side: {}, current_time: {}, current_price: {}".format(
            self.type, self.instrument, self.side, self.current_time, self.current_price
        )

    def __repr__(self):
        return str(self)


class OrderEvent(Event):
    """
    Events for buy or sell orders which should be executed
    Attributes:
        instrument: e.g. "EUR_USD"
        units: How much we want to buy/sell
        side: 'buy' or 'sell'
    """
    def __init__(self, instrument, units, side, current_price=None, current_time=None, buy=None, expiry=None):
        self.type = 'ORDER'
        self.instrument = instrument
        self.units = units
        self.side = side
        self.current_price = current_price
        self.current_time = current_time
        self.buy = buy
        self.expiry = expiry

    def __str__(self):
        return "type: {}, instrument: {}, units: {}, side: {}, current_time: {}, current_price: {}".format(
            self.type, self.instrument, self.units, self.side, self.current_time, self.current_price
        )

    def __repr__(self):
        return str(self)


class FillEvent(Event):
    """
    This event signals that an order has been filled.
    Attributes:
        instrument: e.g. "EUR_USD"
        units: How much we have bought/sold
        side: 'LONG' or 'SHORT'
        price: the price for which the instrument was bought/sold
    """
    def __init__(self, instrument, units, side, price):
        self.type = 'FILL'
        self.instrument = instrument
        self.units = units
        self.side = side
        self.price = price

    def __str__(self):
        return "type: {}, instrument: {}, units: {}, side: {}, price: {}".format(
            self.type, self.instrument, self.units, self.side, self.price
        )

    def __repr__(self):
        return str(self)
