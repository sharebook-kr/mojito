import mojito
import pprint

with open("../../koreainvestment.key") as f:
    lines = f.readlines()
key = lines[0].strip()
secret = lines[1].strip()

broker = mojito.KoreaInvestment(api_key=key, api_secret=secret)
resp = broker.fetch_balance("63398082")
pprint.pprint(resp)
