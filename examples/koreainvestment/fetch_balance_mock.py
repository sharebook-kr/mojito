# 주식잔고조회
import mojito
import pprint

with open("../../mock.key") as f:
    lines = f.readlines()

key = lines[0].strip()
secret = lines[1].strip()
acc_no = "50074923"

broker = mojito.KoreaInvestment(
    api_key = key,
    api_secret = secret,
    acc_no = acc_no
    mock = True
)

resp = broker.fetch_balance()
pprint.pprint(resp)
