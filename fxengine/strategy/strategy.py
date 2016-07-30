import random
import dateutil.parser
import datetime

from fxengine.event.event import SignalEvent


class TestRandomStrategy(object):
    def __init__(self, events):
        self.events = events
        self.ticks = 0
        random.seed(5)

    def calculate_signals(self, event):
        if event.type == 'TICK':
            self.ticks += 1
            if self.ticks % 5 == 0:
                side = random.choice(["buy", "sell"])
                order = SignalEvent(event.instrument, side=side)
                self.events.put(order)


class NewsStrategy(object):
    def __init__(self, events):
        self.events = events
        # Switch to OrderedDict and make sure the times are sorted
        self.time_stamps = {
            "2015-02-14T10:30:18.694014Z": False
        }
        self.threshold = 0.0002  # TODO Pick a better moment + threshold!

    def calculate_signals(self, event):
        if event.type == "TICK":
            current_time = dateutil.parser.parse(event.time)

            # Once ordered, remove yourself from the dict
            for time_stamp, ordered in self.time_stamps.items():
                if ordered:
                    continue

                order_time = dateutil.parser.parse(time_stamp)
                if order_time > current_time:
                    break

                # Only place an order, when it hasn't already been processed and its time is due
                expiry_time = current_time + datetime.timedelta(hours=1)
                order = SignalEvent(
                    event.instrument,
                    side="buy",
                    current_time=current_time,
                    current_price=event.bid,
                    buy=above(event.bid + self.threshold),
                    expiry=expires_by(expiry_time)
                )
                self.events.put(order)
                order = SignalEvent(
                    event.instrument,
                    side='sell',
                    current_time=current_time,
                    current_price=event.bid,
                    buy=below(event.bid - self.threshold),
                    expiry=expires_by(expiry_time)
                )
                self.events.put(order)
                # Make sure to mark it as ordered
                self.time_stamps[time_stamp] = True

            # Remove any orders that have been ordered
            self.time_stamps = {time_stamp: ordered
                                for time_stamp, ordered in self.time_stamps.items()
                                if not ordered}


def expires_by(stop):
    def expired(start):  # TODO Add tests!
        return start > stop

    return expired


def above(threshold):
    def reached(price):
        return price > threshold

    return reached


def below(threshold):
    def reached(price):
        return price < threshold

    return reached
