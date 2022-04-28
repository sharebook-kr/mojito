# 모히토 (Mojito)

대한민국 증권사의 Rest API 기반의 Open API에 대한 통합 파이썬 레퍼 모듈입니다. 
통합 모듈이라 칵테일 이름인 모히토를 프로젝트명으로 사용하고 있으며, 돈 벌어서 몰디브가서 모히토 한 잔 하자는 의미도 있습니다. 

![mojito-g60be5b0d7_640](https://user-images.githubusercontent.com/23475470/161363305-93b48dfa-76d0-4ecd-b703-4d7529323dc9.jpg)

# 설치 

```
$ pip install mojito2
```

# 사용법
## 한국투자증권

https://wikidocs.net/book/7845  

현재가 조회

```
import mojito
import pprint

key = "발급받은 API KEY"
secret = "발급받은 API SECRET"

broker = mojito.KoreaInvestment(api_key=key, api_secret=secret)
resp = broker.fetch_price("005930")
pprint.pprint(resp)

```

일봉 데이터 조회 

```
import mojito
import pprint

key = "발급받은 API KEY"
secret = "발급받은 API SECRET"

broker = mojito.KoreaInvestment(api_key=key, api_secret=secret)
resp = broker.fetch_daily_price("005930")
pprint.pprint(resp)
```

잔고 조회 

```
resp = broker.fetch_balance("00000000") # 계좌번호 8자리
pprint.pprint(resp)
```

주문 

```
resp = broker.create_market_buy_order("00000000", "005930", 10) # 계좌번호 8자리, 삼성전자, 10주, 시장
pprint.pprint(resp)
```

```
{'rt_cd': '0',
 'msg_cd': 'APBK0013',
 'msg1': '주문 전송 완료 되었습니다.',
 'output': {'KRX_FWDG_ORD_ORGNO': '91252',
  'ODNO': '0000117057',
  'ORD_TMD': '121052'}}
```

주문 취소

```
resp = broker.cancel_order("00000000", "91252", "0000117057", "00", 60000, 5, "Y") # 계좌번호, KRX_FWDG_ORD_ORGNO, ODNO, 지정가 주문, 가격, 수량, 모두 
print(resp)
```

미국주식 주문

```
broker = KoreaInvestment(key, secret, exchange="NASD")
resp = broker.create_limit_buy_order("63398082", "TQQQ", 35, 1)
print(resp)
```

웹소켓
```
import pprint
import mojito

with open("../../koreainvestment.key", encoding="utf-8") as f:
    lines = f.readlines()
key = lines[0].strip()
secret = lines[1].strip()


if __name__ == "__main__":
    broker_ws = mojito.KoreaInvestmentWS(key, secret, ["H0STCNT0", "H0STASP0"], ["005930", "000660"], user_id="idjhh82")
    broker_ws.start()
    while True:
        data_ = broker_ws.get()
        if data_[0] == '체결':
            print(data_[1])
        elif data_[0] == '호가':
            print(data_[1])
        elif data_[0] == '체잔':
            print(data_[1])
```        
