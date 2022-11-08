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

result = broker.fetch_today_1m_ohlcv("005930")

df = pd.DataFrame(result['output2'])
dt = pd.to_datetime(df['stck_bsop_date'] + ' ' + df['stck_cntg_hour'], format="%Y%m%d %H%M%S")
df.set_index(dt, inplace=True)
df = df[['stck_oprc', 'stck_hgpr', 'stck_lwpr', 'stck_prpr', 'cntg_vol', 'acml_tr_pbmn']]
#df.columns = ['open', 'high', 'low', 'close', 'volume']
df.columns = ['시가', '고가', '저가', '종가', '거래량', '누적거래대금']
df.index.name = "datetime"
df = df[::-1]
print(df)
