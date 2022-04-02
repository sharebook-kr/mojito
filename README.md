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

현재가 조회

```
import mojito

key = "발급받은 API KEY"
secret = "발급받은 API SECRET"

broker = mojito.KoreaInvestment(api_key=key, api_secret=secret)
resp = broker.fetch_price("J", "005930")
pprint.pprint(resp)

```

일봉 데이터 조회 

```
import mojito

key = "발급받은 API KEY"
secret = "발급받은 API SECRET"

broker = mojito.KoreaInvestment(api_key=key, api_secret=secret)
resp = broker.fetch_daily_price("J", "005930")
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
