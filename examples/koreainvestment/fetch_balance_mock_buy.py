# 주식잔고조회
import mojito
import pprint
import time

with open("../../mock.key") as f:
    lines = f.readlines()

key = lines[0].strip()
secret = lines[1].strip()
acc_no = "50074923-01"

broker = mojito.KoreaInvestment(
    api_key=key,
    api_secret=secret,
    acc_no=acc_no,
    mock = True
)

tickers = broker.fetch_tickers()
stock_tickers = tickers[tickers['그룹코드'] == 'ST']

for row in range(70):
    ticker = stock_tickers['단축코드'].iloc[row]

    # buy
    resp = broker.create_market_buy_order(
        ticker=ticker,
        quantity=1
    )

    pprint.pprint(resp)
    time.sleep(1)