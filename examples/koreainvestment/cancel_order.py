import mojito
import pprint

with open("../../koreainvestment.key") as f:
    lines = f.readlines()
key = lines[0].strip()
secret = lines[1].strip()

broker = mojito.KoreaInvestment(api_key=key, api_secret=secret)
resp = broker.cancel_order(
    "63398082", 
    "91252", 
    "0000026614", 
    "00", 
    65000, 
    1, 
    "Y"
)
pprint.pprint(resp)
 