# FxEngine

Simple event based backtester for Forex markets

## Installation (local)

    $ cd $HOME/projects
    $ git clone https://github.com/Oxylo/fxengine
    $ workon env
    $ cd fxengine
    $ pip install -r requirements.txt


## Running

    $ export PYTHONPATH=$HOME/projects  # export Python path
    $ python trading/trading.py

## Description

fxengine is a project for quantitative forex trading at [OANDA](http://www.oanda.com).

It is based on code from [quantstart](http://www.quantstart.com/articles/Forex-Trading-Diary-1-Automated-Forex-Trading-with-the-OANDA-API).
and QuantFxEngine by H.Kopp.

CAUTION: ALGORITHMIC TRADING IS A WAY TO LOSE LOTS OF MONEY VERY FAST. IF YOU DO NOT KNOW; WHAT YOU ARE DOING, DO NOT TRADE ON LIVE ACCOUNTS. Practice accounts are okay.

You can start this stuff with `python trading/trading.py`

Also you probably want to have a look at settings.py.
If you want to trade with OANDA with this programm, you need to have
your account id in the environment variable OANDA_API_ACCOUNT_ID and
your access token in OANDA_API_ACCESS_TOKEN.

Backtesting is also possible if you have a suitable csv-file.

If you want to adjust the logging, look at logging.conf.


## How it works
The main function is in trade/trading.py. We open two threads, one who
streams prices from a file or from a broker in streaming/streaming.py.
This adds TickEvents to the queue which the two threads use to
communicate.

The second thread handles the Events in the queue.
TickEvents get handled by the strategy module, which can then trigger
SignalEvents. The portfolio also looks at TickEvents to track the
price of open positions.

The portfolio class looks at the SignalEvents and if it fits in the
risk assessment, it throws OrderEvents.

OrderEvents get executed by the execution module. That means that we
buy or sell. The execution class then throws FillEvents, which include
the price for which the Order was filled. This can be different from
the price at which the decision to invest was made.

FillEvents get handled by the portfolio to keep track of the current
positions.


# Other
Tests are done with nosetests and are bundled per object in a separate
folder.

# Finally
Please have a look at the docs section if you need some background on the trading process.
