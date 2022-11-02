"""cancel_order
"""
import pprint
import mojito

with open("../../koreainvestment.key", encoding="utf-8") as f:
    lines = f.readlines()

key = lines[0].strip()
secret = lines[1].strip()
acc_no = "63398082-01"

broker = mojito.KoreaInvestment(
    api_key=key,
    api_secret=secret,
    acc_no=acc_no
)

resp = broker.cancel_order(
    "91252",
    "0000026614",
    "00",
    65000,
    1,
    "Y"
)
pprint.pprint(resp)
