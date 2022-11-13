"""
나스닥 객체 생성
"""
import mojito
import pprint

with open("../../../koreainvestment.key", encoding='utf-8') as f:
    lines = f.readlines()

key = lines[0].strip()
secret = lines[1].strip()
acc_no=lines[2].strip()

broker = mojito.KoreaInvestment(
    api_key=key,
    api_secret=secret,
    acc_no=acc_no,
    exchange='나스닥'
)

price = broker.fetch_price("TSLA")
pprint.pprint(price)
