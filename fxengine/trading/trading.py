import Queue
import os
import threading
import time
import logging
import logging.config

from fxengine.execution.execution import ExecutionAtOANDA, MockExecution
from fxengine.portfolio.portfolio import Portfolio
from fxengine.settings import (INSTRUMENTS, UNITS, BACKTEST, BACKTESTFILE, STREAM_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID,
    API_DOMAIN, LOGGING_CONF)
from fxengine.strategy.strategy import TestRandomStrategy, NewsStrategy
from fxengine.streaming.streaming import StreamingPricesFromFile, StreamingForexPrices_OANDA


def trade(events, strategy, portfolio, execution, stoprequest):
    """
    Carries out an infinite while loop that polls the events queue and
    directs each event to either the strategy component, the execution
    handler or the portfolio.
    """
    while not stoprequest.isSet():
        try:
            event = events.get(True, 0.5)  # block and wait a half second if queue is empty
        except Queue.Empty:
            stoprequest.set()  # If the queue is empty, give up
        else:
            if event is not None:
                if event.type == 'TICK':
                    logger.debug("recv new tick signal: %s", event)
                    strategy.calculate_signals(event)
                    portfolio.execute_tick_event(event)
                elif event.type == 'SIGNAL':
                    logger.info("recv new order signal: %s", event)
                    portfolio.execute_signal_event(event)
                elif event.type == 'ORDER':
                    logger.info("Executing order! %s", event)
                    execution.execute_order(event)
                elif event.type == 'FILL':
                    logger.info("recv new fill event: %s", event)
                    portfolio.execute_fill_event(event)

    while not events.empty():  # execute remaining events
        event = events.get()
        if event is not None:
            if event.type == 'FILL':  # throw everything away except fillevents
                logger.info("recv new fill event: %s", event)
                portfolio.execute_fill_event(event)
            else:
                pass

    # close all positions
    logger.info("Closing all positions")
    portfolio.execute_close_all_positions()
    # and execute the resulting order and fill events
    while not events.empty():
        event = events.get()
        if event is not None:
            if event.type == 'ORDER':
                logger.info("Executing order! %s", event)
                execution.execute_order(event)
            elif event.type == 'Fill':
                logger.info("recv new fill event: %s", event)
                portfolio.execute_fill_event(event)

    logger.info("Balance: %0.2f" % portfolio.balance)
    logger.info("All done!")


if __name__ == "__main__":
    import time
    start = time.time()
    logging.config.fileConfig(LOGGING_CONF)
    logger = logging.getLogger(__name__)  # get a new logger

    events = Queue.Queue()  # Queue for communication between threads
    stop_request = threading.Event()  # For stopping the threads

    # Trade UNITS units of INSTRUMENTS
    instruments = INSTRUMENTS
    units = UNITS

    if BACKTEST:
        # Create the price streaming class
        prices = StreamingPricesFromFile(
            BACKTESTFILE, events, stop_request
        )
        # Create the mock execution handler
        execution = MockExecution(events, prices)
    else:
        # Create the OANDA market price streaming class
        # making sure to provide authentication commands
        prices = StreamingForexPrices_OANDA(
            STREAM_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID,
            instruments, events, stop_request
        )
        # Create the execution handler making sure to
        # provide authentication commands
        execution = ExecutionAtOANDA(API_DOMAIN, ACCESS_TOKEN, ACCOUNT_ID, events)

    # Create the strategy/signal generator, passing the
    # instrument, quantity of units and the events queue
    strategy = NewsStrategy(events)

    # Create the portfolio object that will be used to
    # compare the OANDA positions with the local, to
    # ensure backtesting integrity.
    portfolio = Portfolio(prices, events, equity=units)

    # Create two separate threads: One for the trading loop
    # and another for the market price streaming class
    trade_thread = threading.Thread(target=trade,
                                    args=(events, strategy, portfolio,
                                          execution, stop_request))
    price_thread = threading.Thread(target=prices.stream_to_queue,
                                    args=[])

    # Start both threads
    trade_thread.start()
    price_thread.start()

    # say to the threads if i have pressed ctrl+c
    try:
        while trade_thread.is_alive():
            trade_thread.join(10)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Sending stop request to threads")
        stop_request.set()
        logger.info("Waiting for threads to terminate")
        logging.shutdown()

    stop = time.time()
    print("{:.2f} seconds".format(stop - start))