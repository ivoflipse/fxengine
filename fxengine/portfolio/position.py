class Position(object):
    """
    A position in a market
    Attributes:
        side: LONG or SHORT
        market: e.g. EUR_USD
        units: number of units of the currency
        exposure: exposure
        avg_price: average price for multiple purchases
        cur_price: current price of the whole position
        profit_base: current profit or loss
        profit_perc: current profit or loss in percent
    """

    def __init__(self, side, market, units, exposure, avg_price, cur_price):
        self.side = side
        self.market = market
        self.units = units
        self.exposure = exposure
        self.avg_price = avg_price
        self.cur_price = cur_price
        self.profit_base = self.calculate_profit_base()
        self.profit_perc = self.calculate_profit_perc()

    def calculate_pips(self):
        mult = 1.0
        if self.side == "SHORT":
            mult = -1.0
        return mult * (self.cur_price - self.avg_price)

    def calculate_profit_base(self):
        """
        calculates the current profit or loss
        """
        pips = self.calculate_pips()
        return pips * self.exposure / self.cur_price

    def calculate_profit_perc(self):
        """
        calculates the current profit or loss in percent
        """
        return self.profit_base / self.exposure * 100.0

    def update_position_price(self, cur_price):
        """
        updates the profit attributes of the position
        """
        self.cur_price = cur_price
        self.profit_base = self.calculate_profit_base()
        self.profit_perc = self.calculate_profit_perc()
