# 주식잔고조회
import mojito
import pprint

with open("../../mock.key") as f:
    lines = f.readlines()

key = lines[0].strip()
secret = lines[1].strip()
acc_no = "50074923-01"

broker = mojito.KoreaInvestment(
    api_key = key,
    api_secret = secret,
    acc_no = acc_no,
    mock = True
)

resp = broker.fetch_balance()
#pprint.pprint(resp)
for comp in resp['output1']:
    print(comp['pdno'])
    print(comp['prdt_name'])
    print(comp['hldg_qty'])
    print(comp['pchs_amt'])
    print(comp['evlu_amt'])
    print("-" * 40)