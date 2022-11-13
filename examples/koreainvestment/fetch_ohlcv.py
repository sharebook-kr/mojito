import mojito
import pprint
import pandas as pd

with open("../../koreainvestment.key") as f:
    lines = f.readlines()

key = lines[0].strip()
secret = lines[1].strip()
ACC_NO = "63398082-01"

broker = mojito.KoreaInvestment(
    api_key=key,
    api_secret=secret,
    acc_no=ACC_NO
)

resp = broker.fetch_ohlcv(
    symbol="005930",
    timeframe='D',
    adj_price=True
)

pprint.pprint(resp)
print(len(resp['output2']))

df = pd.DataFrame(resp['output2'])
dt = pd.to_datetime(df['stck_bsop_date'], format="%Y%m%d")
df.set_index(dt, inplace=True)
df = df[['stck_oprc', 'stck_hgpr', 'stck_lwpr', 'stck_clpr']]
df.columns = ['open', 'high', 'low', 'close']
df.index.name = "date"
print(df)