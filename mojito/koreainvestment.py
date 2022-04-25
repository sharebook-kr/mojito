from curses.ascii import ctrl
from mojito.base.broker import Broker 
import requests 
import json
import multiprocessing as mp
import websockets
import asyncio
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

EXCHANGE_CODE = {
    "홍콩": "HKS",
    "뉴욕": "NYS",
    "나스닥": "NAS",
    "아멕스": "AMS",
    "도쿄": "TSE",
    "상해": "SHS",
    "심천": "SZS",
    "상해지수": "SHI",
    "심천지수": "SZI",
    "호치민": "HSX",
    "하노이": "HNX"
}

# 해외주식 주문
EXCHANGE_CODE2 = {
    "나스닥": "NASD",
    "뉴욕": "NYSE",
    "아멕스": "AMEX",
    "홍콩": "SEHK",
    "상해": "SHAA",
    "심천": "SZAA",
    "도쿄": "TKSE"
}

contract_items = "유가증권단축종목코드|주식체결시간|주식현재가|전일대비부호|전일대비|전일대비율|가중평균주식가격|주식시가|주식최고가|주식최저가|매도호가1|매수호가1|체결거래량|누적거래량|누적거래대금|매도체결건수|매수체결건수|순매수체결건수|체결강도|총매도수량|총매수수량|체결구분|매수비율|전일거래량대비등락율|시가시간|시가대비구분|시가대비|최고가시간|고가대비구분|고가대비|최저가시간|저가대비구분|저가대비|영업일자|신장운영구분코드|거래정지여부|매도호가잔량|매수호가잔량|총매도호가잔량|총매수호가잔량|거래량회전율|전일동시간누적거래량|전일동시간누적거래량비율|시간구분코드|임의종료구분코드|정적VI발동기준가".split("|")
signin_items = "고객ID|계좌번호|주문번호|원주문번호|매도매수구분|정정구분|주문종류|주문조건|주식단축종목코드|체결수량|체결단가|주식체결시간|거부여부|체결여부|접수여부|지점번호|주문수량|계좌명|체결종목명|신용구분|신용대출일자|체결종목명40|주문가격".split("|")


class KoreaInvestmentWS(mp.Process):
    def __init__(self, api_key: str, api_secret: str, tr_id_list: list, tr_key_list: list, user_id: str=None):
        super().__init__() 
        self.api_key = api_key 
        self.api_secret = api_secret
        self.tr_id_list = tr_id_list 
        self.tr_key_list = tr_key_list
        self.user_id = user_id
        self.queue = mp.Queue()

    def run(self):
        asyncio.run(self.ws_client())

    async def ws_client(self):
        uri = "ws://ops.koreainvestment.com:21000"

        async with websockets.connect(uri, ping_interval=None) as websocket:
            header = {
                "appKey": self.api_key,
                "appSecret": self.api_secret, 
                "custtype": "P",
                "tr_type": "1",
                "content": "utf-8"
            }
            body = {
                "tr_id": None, 
                "tr_key": None, 
            }
            fmt = {
                "header": header, 
                "body": {
                    "input": body
                } 
            }

            # 주식체결, 주식호가 등록 
            for tr_id in self.tr_id_list:
                for tr_key in self.tr_key_list:
                    fmt["body"]["input"]["tr_id"] = tr_id 
                    fmt["body"]["input"]["tr_key"] = tr_key 
                    subscribe_data = json.dumps(fmt)
                    await websocket.send(subscribe_data)

            # 체결 통보 등록 
            if self.user_id is not None:
                fmt["body"]["input"]["tr_id"] = "H0STCNI0"
                fmt["body"]["input"]["tr_key"] = self.user_id 
                subscribe_data = json.dumps(fmt)
                await websocket.send(subscribe_data)

            while True:
                data = await websocket.recv()

                if data[0] == '0':
                    # 주식체결, 오더북
                    tokens = data.split('|')  
                    if tokens[1] == "H0STCNT0":     # 주식 체결 데이터
                        self.parse_contract(tokens[2], tokens[3])
                    elif tokens[1] == "H0STASP0":
                        self.parse_orderbook(tokens[3])
                    
                    #self.queue.put(data)
                elif data[0] == '1':
                    tokens = data.split('|')  
                    if tokens[1] == "H0STCNI0":
                        self.parse_signin_notice(tokens[3])
                else:
                    ctrl_data = json.loads(data)
                    tr_id = ctrl_data["header"]["tr_id"]

                    if tr_id != "PINGPONG":
                        rt_cd = ctrl_data["body"]["rt_cd"]
                        if rt_cd == '1':
                            break
                        elif rt_cd == '0':
                            if tr_id in ["H0STASP0", "K0STCNI9", "H0STCNI0", "H0STCNI9"]:
                                self.aes_key = ctrl_data["body"]["output"]["key"]
                                self.aes_iv  = ctrl_data["body"]["output"]["iv"]

                    elif tr_id == "PINGPONG":
                        await websocket.send(data)

    def parse_signin_notice(self, data):
        aes_dec_str = self.aes_cbc_base64_dec(data)
        tokens = aes_dec_str.split('^')

        for i, item in enumerate(signin_items):
            print("%s [%s]" % (item, tokens[i]))

    def aes_cbc_base64_dec(self, cipher_text: str):
        cipher = AES.new(self.aes_key.encode('utf-8'), AES.MODE_CBC, self.aes_iv.encode('utf-8'))
        return bytes.decode(unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size))

    def parse_contract(self, count: str, data: str):
        tokens = data.split('^')
        index = 0 

        for i in range(int(count)):
            for item in contract_items:
                print(item, tokens[index]) 
                index += 1 
            print("----------")

    def parse_orderbook(self, data: str):
        recvvalue = data.split('^')

        print("유가증권 단축 종목코드 [" + recvvalue[0] + "]")
        print("영업시간 [" + recvvalue[1] + "]" + "시간구분코드 [" + recvvalue[2] + "]")
        print("======================================")
        print("매도호가10 [%s]    잔량10 [%s]" % (recvvalue[12], recvvalue[32]))
        print("매도호가09 [%s]    잔량09 [%s]" % (recvvalue[11], recvvalue[31]))
        print("매도호가08 [%s]    잔량08 [%s]" % (recvvalue[10], recvvalue[30]))
        print("매도호가07 [%s]    잔량07 [%s]" % (recvvalue[9], recvvalue[29]))
        print("매도호가06 [%s]    잔량06 [%s]" % (recvvalue[8], recvvalue[28]))
        print("매도호가05 [%s]    잔량05 [%s]" % (recvvalue[7], recvvalue[27]))
        print("매도호가04 [%s]    잔량04 [%s]" % (recvvalue[6], recvvalue[26]))
        print("매도호가03 [%s]    잔량03 [%s]" % (recvvalue[5], recvvalue[25]))
        print("매도호가02 [%s]    잔량02 [%s]" % (recvvalue[4], recvvalue[24]))
        print("매도호가01 [%s]    잔량01 [%s]" % (recvvalue[3], recvvalue[23]))
        print("--------------------------------------")
        print("매수호가01 [%s]    잔량01 [%s]" % (recvvalue[13], recvvalue[33]))
        print("매수호가02 [%s]    잔량02 [%s]" % (recvvalue[14], recvvalue[34]))
        print("매수호가03 [%s]    잔량03 [%s]" % (recvvalue[15], recvvalue[35]))
        print("매수호가04 [%s]    잔량04 [%s]" % (recvvalue[16], recvvalue[36]))
        print("매수호가05 [%s]    잔량05 [%s]" % (recvvalue[17], recvvalue[37]))
        print("매수호가06 [%s]    잔량06 [%s]" % (recvvalue[18], recvvalue[38]))
        print("매수호가07 [%s]    잔량07 [%s]" % (recvvalue[19], recvvalue[39]))
        print("매수호가08 [%s]    잔량08 [%s]" % (recvvalue[20], recvvalue[40]))
        print("매수호가09 [%s]    잔량09 [%s]" % (recvvalue[21], recvvalue[41]))
        print("매수호가10 [%s]    잔량10 [%s]" % (recvvalue[22], recvvalue[42]))
        print("======================================")
        print("총매도호가 잔량        [%s]" % (recvvalue[43]))
        print("총매도호가 잔량 증감   [%s]" % (recvvalue[54]))
        print("총매수호가 잔량        [%s]" % (recvvalue[44]))
        print("총매수호가 잔량 증감   [%s]" % (recvvalue[55]))
        print("시간외 총매도호가 잔량 [%s]" % (recvvalue[45]))
        print("시간외 총매수호가 증감 [%s]" % (recvvalue[46]))
        print("시간외 총매도호가 잔량 [%s]" % (recvvalue[56]))
        print("시간외 총매수호가 증감 [%s]" % (recvvalue[57]))
        print("예상 체결가            [%s]" % (recvvalue[47]))
        print("예상 체결량            [%s]" % (recvvalue[48]))
        print("예상 거래량            [%s]" % (recvvalue[49]))
        print("예상체결 대비          [%s]" % (recvvalue[50]))
        print("부호                   [%s]" % (recvvalue[51]))
        print("예상체결 전일대비율    [%s]" % (recvvalue[52]))
        print("누적거래량             [%s]" % (recvvalue[53]))
        print("주식매매 구분코드      [%s]" % (recvvalue[58]))


    def get(self):
        data = self.queue.get()
        return data


class KoreaInvestment(Broker):
    def __init__(self, api_key: str, api_secret: str, exchange: str="서울"):
        """생성자

        Args:
            api_key (str): 발급받은 API key 
            api_secret (str): 발급받은 API secret
            exchange (str): "나스닥", "뉴욕", "아멕스", "홍콩", "상해", "심천", "도쿄" 
        """
        self.BASE_URL = "https://openapi.koreainvestment.com:9443"
        self.api_key = api_key 
        self.api_secret = api_secret
        self.exchange = exchange
        self.issue_access_token() 

    def set_sandbox_mode(self, mode: bool=True):
        """테스트(모의투자) 서버 사용 설정

        Args:
            mode (bool, optional): True: 테스트서버, False: 실서버 Defaults to True.
        """
        if mode:
            self.BASE_URL = "https://openapivts.koreainvestment.com:29443"
        else:
            self.BASE_URL = "https://openapi.koreainvestment.com:9443"

    def issue_access_token(self):
        """접근토큰발급
        """
        path = "oauth2/tokenP"
        url = f"{self.BASE_URL}/{path}"
        headers = {"content-type":"application/json"}
        data = {
            "grant_type":"client_credentials",
            "appkey": self.api_key, 
            "appsecret": self.api_secret
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        self.access_token = 'Bearer {}'.format(resp.json()["access_token"])

    def issue_hashkey(self, data: dict):
        """해쉬키 발급

        Args:
            data (dict): POST 요청 데이터

        Returns:
            _type_: _description_
        """
        path = "uapi/hashkey"
        url = f"{self.BASE_URL}/{path}"
        headers = {
           "content-type": "application/json", 
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "User-Agent": "Mozilla/5.0"
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        haskkey = resp.json()["HASH"] 
        return haskkey

    def fetch_price(self, ticker: str) -> dict:
        if self.exchange == "서울":
            return self.fetch_domestic_price("J", ticker)
        else:
            return self.fetch_oversea_price(ticker)

    def fetch_domestic_price(self, market_code: str, ticker: str) -> dict:
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
        resp = requests.get(url, headers=headers, params=params)
        return resp.json()

    def fetch_oversea_price(self, ticker: str) -> dict:
        """해외주식 현재체결가 

        Args:
            market_code (str): 시장 분류코드
            ticker (str): 종목코드

        Returns:
            dict: API 개발 가이드 참조 
        """
        path = "uapi/overseas-price/v1/quotations/price"
        url = f"{self.BASE_URL}/{path}"
        headers = {
           "content-type": "application/json", 
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "HHDFS00000300"
        }
        
        exchange_code = EXCHANGE_CODE[self.exchange]
        params = {
            "AUTH": "",
            "EXCD": exchange_code,
            "SYMB": ticker 
        }
        resp = requests.get(url, headers=headers, params=params)
        return resp.json()

    def fetch_daily_price(self, ticker: str, period: str='D', adj_price: bool=True) -> dict:
        """주식 현재가 일자별

        Args:
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
            "fid_cond_mrkt_div_code": "J",
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
        path = "uapi/domestic-stock/v1/trading/inquire-balance" 
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

    def create_order(self, side: str, acc_no: str, ticker: str, price: int, quantity: int, order_type: str) -> dict:
        path = "uapi/domestic-stock/v1/trading/order-cash" 
        url = f"{self.BASE_URL}/{path}"

        tr_id = "TTTC0802U" if side == "buy" else "TTTC0801U"
        unpr = "0" if order_type == "01" else str(price)

        data = {
            "CANO": acc_no, 
            "ACNT_PRDT_CD": "01",
            "PDNO": ticker, 
            "ORD_DVSN": order_type, 
            "ORD_QTY": str(quantity),
            "ORD_UNPR": unpr
        }
        hashkey = self.issue_hashkey(data)
        headers = {
           "content-type": "application/json", 
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": tr_id, 
           "custtype": "P",
           "hashkey" : hashkey
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        return resp.json()

    def create_market_buy_order(self, acc_no: str, ticker: str, quantity: int) -> dict:
        return self.create_order("buy", acc_no, ticker, 0, quantity, "01")

    def create_market_sell_order(self, acc_no: str, ticker: str, quantity: int) -> dict:
        return self.create_order("sell", acc_no, ticker, 0, quantity, "01")

    def create_limit_buy_order(self, acc_no: str, ticker: str, price: int, quantity: str) -> dict:
        if self.exchange == "서울":
            resp = self.create_order("buy", acc_no, ticker, price, quantity, "00")
        else:
            resp = self.create_oversea_order("buy", acc_no, ticker, price, quantity, "00")

        return resp

    def create_limit_sell_order(self, acc_no: str, ticker: str, price: int, quantity: str) -> dict:
        if self.exchange == "서울":
            resp = self.create_order("sell", acc_no, ticker, price, quantity, "00")
        else:
            resp = self.create_oversea_order("sell", acc_no, ticker, price, quantity, "00")
        return resp

    def cancel_order(self, acc_no: str, order_code: str, order_id: str, order_type: str, price: int, quantity: int, all: str="Y"):
        return self.update_order(acc_no, order_code, order_id, order_type, price, quantity, all, is_change=False)

    def modify_order(self, acc_no: str, order_code: str, order_id: str, order_type: str, price: int, quantity: int, all: str="Y"):
        return self.update_order(acc_no, order_code, order_id, order_type, price, quantity, all, is_change=True)
        
    def update_order(self, acc_no: str, order_code: str, order_id: str, order_type: str, price: int, quantity: int, all: str="Y", is_change: bool=True):
        path = "uapi/domestic-stock/v1/trading/order-rvsecncl"
        url = f"{self.BASE_URL}/{path}"
        param = "01" if is_change else "02"
        data = {
            "CANO": acc_no, 
            "ACNT_PRDT_CD": "01",
            "KRX_FWDG_ORD_ORGNO": order_code,
            "ORGN_ODNO": order_id,
            "ORD_DVSN": order_type, 
            "RVSE_CNCL_DVSN_CD": param, 
            "ORD_QTY": str(quantity),
            "ORD_UNPR": str(price),
            "QTY_ALL_ORD_YN": all 
        }
        hashkey = self.issue_hashkey(data)
        headers = {
           "content-type": "application/json", 
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "TTTC0803U",
           "hashkey" : hashkey
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        return resp.json()

    def fetch_open_order(self, acc_no: str, param: dict):
        """주식 정정/취소가능 주문 조회

        Args:
            acc_no (str): 8자리 계좌번호 
            param (dict): 세부 파라미터

        Returns:
            _type_: _description_
        """
        path = "uapi/domestic-stock/v1/trading/inquire-psbl-rvsecncl"
        url = f"{self.BASE_URL}/{path}"

        fk100 = param["CTX_AREA_FK100"]
        nk100 = param["CTX_AREA_NK100"]
        type1 = param["INQR_DVSN_1"]
        type2 = param["INQR_DVSN_2"]

        headers = {
           "content-type": "application/json", 
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "TTTC8036R"
        }

        params = {
            "CANO": acc_no, 
            "ACNT_PRDT_CD": "01",
            "CTX_AREA_FK100": fk100,
            "CTX_AREA_NK100": nk100,
            "INQR_DVSN_1": type1, 
            "INQR_DVSN_2": type2
        }

        resp = requests.get(url, headers=headers, params=params) 
        return resp.json()

    def create_oversea_order(self, side: str, acc_no: str, ticker: str, price: int, quantity: int, order_type: str) -> dict:
        path = "uapi/overseas-stock/v1/trading/order" 
        url = f"{self.BASE_URL}/{path}"

        if side == "buy":
            tr_id = "JTTT1002U"
        else:
            tr_ide = "JTTT1006U"
        
        exchange_cd = EXCHANGE_CODE2[self.exchange]
        data = {
            "CANO": acc_no, 
            "ACNT_PRDT_CD": "01",
            "OVRS_EXCG_CD": exchange_cd, 
            "PDNO": ticker, 
            "ORD_QTY": str(quantity),
            "OVRS_ORD_UNPR": str(price), 
            "ORD_SVR_DVSN_CD": "0",
            "ORD_DVSN": order_type 
        }
        hashkey = self.issue_hashkey(data)
        headers = {
           "content-type": "application/json", 
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": tr_id, 
           "hashkey" : hashkey
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        return resp.json()


if __name__ == "__main__":
    import pprint

    with open("../koreainvestment.key") as f:
        lines = f.readlines()
    
    key = lines[0].strip()
    secret = lines[1].strip()

    broker = KoreaInvestment(key, secret)
    #broker = KoreaInvestment(key, secret, exchange="나스닥")
    
    #resp = broker.fetch_price("005930")
    #pprint.pprint(resp)
    
    #resp = broker.fetch_daily_price("005930")
    #pprint.pprint(resp)

    #resp = broker.fetch_balance("00000000")
    #pprint.pprint(resp)
    
    #resp = broker.create_market_buy_order("63398082", "005930", 10)
    #pprint.pprint(resp)

    #resp = broker.cancel_order("63398082", "91252", "0000117057", "00", 60000, 5, "Y")
    #print(resp)
    
    #resp = broker.create_limit_buy_order("63398082", "TQQQ", 35, 1)
    #print(resp)

    # 실시간주식 체결가 
    broker_ws = KoreaInvestmentWS(key, secret, ["H0STCNT0", "H0STASP0"], ["005930", "000660"], user_id="idjhh82")
    #broker_ws = KoreaInvestmentWS(key, secret, ["H0STCNT0"], "005930")
    broker_ws.start()
    while True:
        data = broker_ws.get()
        print(data)

    # 실시간주식호가
    #broker_ws = KoreaInvestmentWS(key, secret, "H0STASP0", "005930")
    #broker_ws.start()
    #for i in range(3):
    #    data = broker_ws.get()
    #    print(data)

    # 실시간주식체결통보 
    #broker_ws = KoreaInvestmentWS(key, secret, "H0STCNI0", "user_id")
    #broker_ws.start()
    #for i in range(3):
    #    data = broker_ws.get()
    #    print(data)

