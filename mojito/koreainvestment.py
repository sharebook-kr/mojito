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

    def fetch_daily_price(self, market_code: str, ticker: str, period: str='D', adj_price: bool=True) -> dict:
        """주식 현재가 일자별

        Args:
            market_code (str): 시장 분류코드 
            ticker (str): 종목코드
            period (str): "D" (일), "W" (주), "M" (월)
            adj_price (bool, optional): True: 수정주가 반영, False: 수정주가 미반영. Defaults to True.

        Returns:
            dict: _description_
        """
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
            "fid_period_div_code": period
        }
        res = requests.get(url, headers=headers, params=params)
        return res.json()

    def fetch_balance(self, acc_no: str) -> dict:
        """주식잔고조회

        Args:
            acc_no (str): 계좌번호 앞8자리

        Returns:
            dict: _description_
        """
        path = "/uapi/domestic-stock/v1/trading/inquire-balance" 
        url = f"{self.BASE_URL}/{path}"
        headers = {
           "content-type": "application/json", 
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "TTTC8434R"
        }
        params = {
            'CANO': acc_no, 
            'ACNT_PRDT_CD': '01', 
            'AFHR_FLPR_YN': 'N', 
            'OFL_YN': 'N', 
            'INQR_DVSN': '01', 
            'UNPR_DVSN': '01', 
            'FUND_STTL_ICLD_YN': 'N', 
            'FNCG_AMT_AUTO_RDPT_YN': 'N', 
            'PRCS_DVSN': '01', 
            'CTX_AREA_FK100': '', 
            'CTX_AREA_NK100': ''
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

    #resp = ki.fetch_balance("00000000")
    #pprint.pprint(resp)