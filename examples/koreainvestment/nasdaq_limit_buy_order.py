import mojito
import pprint

with open("../../koreainvestment.key", encoding='utf-8') as f:
    lines = f.readlines()
key = lines[0].strip()
secret = lines[1].strip()

broker = mojito.KoreaInvestment(api_key=key, api_secret=secret, exchange='나스닥')
resp = broker.create_limit_buy_order(
    acc_no="63398082",
    ticker="TQQQ",
    price=30,
    quantity=5
)
pprint.pprint(resp)