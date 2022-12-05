# 주식잔고조회
import mojito
import pprint

with open("../../koreainvestment.key") as f:
    lines = f.readlines()

key = lines[0].strip()
secret = lines[1].strip()
ACC_NO="63398082-01"

broker = mojito.KoreaInvestment(
    api_key=key,
    api_secret=secret,
    acc_no=ACC_NO
)

resp = broker.check_buy_order(
    symbol="005930",
    price=60000,
    order_type='00'
)
pprint.pprint(resp)

