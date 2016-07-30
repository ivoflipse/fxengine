import os

ENVIRONMENTS = {
    "streaming": {
        "real": "stream-fxtrade.oanda.com",
        "practice": "stream-fxpractice.oanda.com",
        "sandbox": "stream-sandbox.oanda.com"
    },
    "api": {
        "real": "api-fxtrade.oanda.com",
        "practice": "api-fxpractice.oanda.com",
        "sandbox": "api-sandbox.oanda.com"
    }
}

DOMAIN = "practice"
STREAM_DOMAIN = ENVIRONMENTS["streaming"][DOMAIN]
API_DOMAIN = ENVIRONMENTS["api"][DOMAIN]
ACCESS_TOKEN = os.environ.get('OANDA_API_ACCESS_TOKEN', None)
ACCOUNT_ID = os.environ.get('OANDA_API_ACCOUNT_ID', None)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(os.curdir)))

# Backtesting on a file
BACKTEST = True
BACKTESTFILE = os.path.join(PROJECT_ROOT, 'data', 'testdata.csv')

# Instruments
INSTRUMENTS = ["EUR_USD", "EUR_CHF"]
# Units to track in Portfolio,i.e., size of account
UNITS = 10000

LOGGING_CONF = os.path.join(PROJECT_ROOT, "logging.conf")
