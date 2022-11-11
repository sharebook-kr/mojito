"""modify_order
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

resp = broker.modify_order(
    org_no="91252",
    order_no="0000138450",
    order_type="00",
    price=60000,
    quantity=4,
    total=True
)
pprint.pprint(resp)
