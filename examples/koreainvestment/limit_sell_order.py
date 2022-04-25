import mojito
import pprint

with open("../../koreainvestment.key") as f:
    lines = f.readlines()
key = lines[0].strip()
secret = lines[1].strip()

broker = mojito.KoreaInvestment(api_key=key, api_secret=secret)
resp = broker.create_limit_sell_order(
    acc_no="63398082",
    ticker="005930",
    price=67000,
    quantity=1
)
pprint.pprint(resp)