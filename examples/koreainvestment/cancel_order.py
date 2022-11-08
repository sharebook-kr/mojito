"""cancel_order
"""
import pprint
import mojito

with open("../../koreainvestment.key", encoding="utf-8") as f:
    lines = f.readlines()

key = lines[0].strip()
secret = lines[1].strip()
ACC_NO = "63398082-01"

broker = mojito.KoreaInvestment(
    api_key=key,
    api_secret=secret,
    acc_no=ACC_NO
)

resp = broker.cancel_order(
    order_code="91252",
    order_id="0000026614",
    order_type="00",
    price=65000,
    quantity=1
)
pprint.pprint(resp)
