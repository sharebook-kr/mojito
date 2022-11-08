import mojito
import pprint

with open("../../koreainvestment.key") as f:
    lines = f.readlines()

key = lines[0].strip()
secret = lines[1].strip()
ACC_NO = "63398082-01"
SYMBOL = "005930"

broker = mojito.KoreaInvestment(
    api_key=key,
    api_secret=secret,
    acc_no=ACC_NO
)

# 현재가 조회
resp = broker.fetch_price(symbol=SYMBOL)
close = int(resp['output']['stck_prpr'])
print(close, type(close))

# 지정가 매수
# 매수가격 = 현재가 - 5000
buy_price = close - 5000
resp = broker.create_limit_buy_order(
    symbol="005930",
    price=buy_price,
    quantity=4
)
pprint.pprint(resp)