import mojito
import pprint

with open("../../koreainvestment.key") as f:
    lines = f.readlines()

key = lines[0].strip()
secret = lines[1].strip()
ACC_NO = "63398082-01"

broker = mojito.KoreaInvestment(
    api_key=key,
    api_secret=secret,
    acc_no=ACC_NO
)

resp = broker.fetch_ohlcv(
    symbol="005930",
    timeframe='D',
    adj_price=True
)
pprint.pprint(resp)
print(len(resp['output2']))
