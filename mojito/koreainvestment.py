from mojito.base.broker import Broker 
import requests 
import json


class KoreaInvestment(Broker):
    BASE_URL = "https://openapi.koreainvestment.com:9443"
    BASE_URL_TEST = "https://openapivts.koreainvestment.com:29443"

    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key 
        self.api_secret = api_secret
        self.issue_access_token() 

    def issue_access_token(self):
        """접근토큰발급
        """
        path = "oauth2/tokenP"
        headers = {"content-type":"application/json"}
        body = {
            "grant_type":"client_credentials",
            "appkey": self.api_key, 
            "appsecret": self.api_secret
        }
        url = f"{self.BASE_URL}/{path}"
        resp = requests.post(url, headers=headers, data=json.dumps(body))
        self.access_token = 'Bearer {}'.format(resp.json()["access_token"])

    def fetch_price(self, market_code: str, ticker: str) -> dict:
        """주식현재가시세

        Args:
            market_code (str): 시장 분류코드
            ticker (str): 종목코드

        Returns:
            dict: API 개발 가이드 참조 
        """
        path = "uapi/domestic-stock/v1/quotations/inquire-price"
        url = f"{self.BASE_URL}/{path}"
        headers = {
           "content-type": "application/json", 
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHKST01010100"
        }
        params = {
            "fid_cond_mrkt_div_code": market_code,
            "fid_input_iscd": ticker
        }
        res = requests.get(url, headers=headers, params=params)
        return res.json()

    def fetch_daily_price(self, market_code: str, ticker: str, adj_price: bool=True) -> dict:
        path = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
        url = f"{self.BASE_URL}/{path}"
        headers = {
           "content-type": "application/json", 
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHKST01010400"
        }

        adj_param = "1" if adj_price else "0"
        params = {
            "fid_cond_mrkt_div_code": market_code,
            "fid_input_iscd": ticker,
            "fid_org_adj_prc": adj_param,
            "fid_period_div_code":"D"
        }
        res = requests.get(url, headers=headers, params=params)
        return res.json()


if __name__ == "__main__":
    import pprint

    with open("../koreainvestment.key") as f:
        lines = f.readlines()
    
    key = lines[0].strip()
    secret = lines[1].strip()

    ki = KoreaInvestment(key, secret)
    
    #resp = ki.fetch_price("J", "005930")
    #pprint.pprint(resp)
    
    #resp = ki.fetch_daily_price("J", "005930")
    #pprint.pprint(resp)