'''
한국투자증권 python wrapper
'''
import json
import pickle
import asyncio
from base64 import b64decode
from multiprocessing import Process, Queue
import datetime
import requests
import zipfile
import os
import pandas as pd
import websockets
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

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
# 해외주식 잔고
EXCHANGE_CODE2 = {
    "나스닥": "NASD",
    "뉴욕": "NYSE",
    "아멕스": "AMEX",
    "홍콩": "SEHK",
    "상해": "SHAA",
    "심천": "SZAA",
    "도쿄": "TKSE"
}

CURRENCY_CODE = {
    "나스닥": "USD",
    "뉴욕": "USD",
    "아멕스": "USD",
    "홍콩": "HKD",
    "상해": "CNY",
    "심천": "CNY",
    "도쿄": "JPY"
}

execution_items = [
    "유가증권단축종목코드", "주식체결시간", "주식현재가", "전일대비부호", "전일대비",
    "전일대비율", "가중평균주식가격", "주식시가", "주식최고가", "주식최저가",
    "매도호가1", "매수호가1", "체결거래량", "누적거래량", "누적거래대금",
    "매도체결건수", "매수체결건수", "순매수체결건수", "체결강도", "총매도수량",
    "총매수수량", "체결구분", "매수비율", "전일거래량대비등락율", "시가시간",
    "시가대비구분", "시가대비", "최고가시간", "고가대비구분", "고가대비",
    "최저가시간", "저가대비구분", "저가대비", "영업일자", "신장운영구분코드",
    "거래정지여부", "매도호가잔량", "매수호가잔량", "총매도호가잔량", "총매수호가잔량",
    "거래량회전율", "전일동시간누적거래량", "전일동시간누적거래량비율", "시간구분코드",
    "임의종료구분코드", "정적VI발동기준가"
]

orderbook_items = [
    "유가증권 단축 종목코드",
    "영업시간",
    "시간구분코드",
    "매도호가01",
    "매도호가02",
    "매도호가03",
    "매도호가04",
    "매도호가05",
    "매도호가06",
    "매도호가07",
    "매도호가08",
    "매도호가09",
    "매도호가10",
    "매수호가01",
    "매수호가02",
    "매수호가03",
    "매수호가04",
    "매수호가05",
    "매수호가06",
    "매수호가07",
    "매수호가08",
    "매수호가09",
    "매수호가10",
    "매도호가잔량01",
    "매도호가잔량02",
    "매도호가잔량03",
    "매도호가잔량04",
    "매도호가잔량05",
    "매도호가잔량06",
    "매도호가잔량07",
    "매도호가잔량08",
    "매도호가잔량09",
    "매도호가잔량10",
    "매수호가잔량01",
    "매수호가잔량02",
    "매수호가잔량03",
    "매수호가잔량04",
    "매수호가잔량05",
    "매수호가잔량06",
    "매수호가잔량07",
    "매수호가잔량08",
    "매수호가잔량09",
    "매수호가잔량10",
    "총매도호가 잔량", # 43
    "총매수호가 잔량",
    "시간외 총매도호가 잔량",
    "시간외 총매수호가 증감",
    "예상 체결가",
    "예상 체결량",
    "예상 거래량",
    "예상체결 대비",
    "부호",
    "예상체결 전일대비율",
    "누적거래량",
    "총매도호가 잔량 증감",
    "총매수호가 잔량 증감",
    "시간외 총매도호가 잔량",
    "시간외 총매수호가 증감",
    "주식매매 구분코드"
]

notice_items = [
    "고객ID", "계좌번호", "주문번호", "원주문번호", "매도매수구분", "정정구분", "주문종류",
    "주문조건", "주식단축종목코드", "체결수량", "체결단가", "주식체결시간", "거부여부",
    "체결여부", "접수여부", "지점번호", "주문수량", "계좌명", "체결종목명", "신용구분",
    "신용대출일자", "체결종목명40", "주문가격"
]


class KoreaInvestmentWS(Process):
    """WebSocket
    """
    def __init__(self, api_key: str, api_secret: str, tr_id_list: list,
                 tr_key_list: list, user_id: str = None):
        """_summary_
        Args:
            api_key (str): _description_
            api_secret (str): _description_
            tr_id_list (list): _description_
            tr_key_list (list): _description_
            user_id (str, optional): _description_. Defaults to None.
        """
        super().__init__()
        self.api_key = api_key
        self.api_secret = api_secret
        self.tr_id_list = tr_id_list
        self.tr_key_list = tr_key_list
        self.user_id = user_id
        self.aes_key = None
        self.aes_iv = None
        self.queue = Queue()

    def run(self):
        """_summary_
        """
        asyncio.run(self.ws_client())

    async def ws_client(self):
        """_summary_
        """
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
                        self.parse_execution(tokens[2], tokens[3])
                    elif tokens[1] == "H0STASP0":
                        self.parse_orderbook(tokens[3])
                elif data[0] == '1':
                    tokens = data.split('|')
                    if tokens[1] == "H0STCNI0":
                        self.parse_notice(tokens[3])
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

    def aes_cbc_base64_dec(self, cipher_text: str):
        """_summary_
        Args:
            cipher_text (str): _description_
        Returns:
            _type_: _description_
        """
        cipher = AES.new(self.aes_key.encode('utf-8'), AES.MODE_CBC, self.aes_iv.encode('utf-8'))
        return bytes.decode(unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size))

    def parse_notice(self, notice_data: str):
        """_summary_
        Args:
            notice_data (_type_): 주식 체잔 데이터
        """
        aes_dec_str = self.aes_cbc_base64_dec(notice_data)
        tokens = aes_dec_str.split('^')
        notice_data = dict(zip(notice_items, tokens))
        self.queue.put(['체잔', notice_data])

    def parse_execution(self, count: str, execution_data: str):
        """주식현재가 실시간 주식 체결가 데이터 파싱
        Args:
            count (str): the number of data
            execution_data (str): 주식 체결 데이터
        """
        tokens = execution_data.split('^')
        for i in range(int(count)):
            parsed_data = dict(zip(execution_items, tokens[i * 46: (i + 1) * 46]))
            self.queue.put(['체결', parsed_data])

    def parse_orderbook(self, orderbook_data: str):
        """_summary_
        Args:
            orderbook_data (str): 주식 호가 데이터
        """
        recvvalue = orderbook_data.split('^')
        orderbook = dict(zip(orderbook_items, recvvalue))
        self.queue.put(['호가', orderbook])

    def get(self):
        """get data from the queue

        Returns:
            _type_: _description_
        """
        data = self.queue.get()
        return data

    def terminate(self):
        if self.is_alive():
            self.kill()


class KoreaInvestment:
    '''
    한국투자증권 REST API
    '''
    def __init__(self, api_key: str, api_secret: str, acc_no: str,
                 exchange: str = "서울", mock: bool = False):
        """생성자
        Args:
            api_key (str): 발급받은 API key
            api_secret (str): 발급받은 API secret
            acc_no (str): 계좌번호 체계의 앞 8자리-뒤 2자리
            exchange (str): "서울", "나스닥", "뉴욕", "아멕스", "홍콩", "상해", "심천",
                            "도쿄", "하노이", "호치민"
            mock (bool): True (mock trading), False (real trading)
        """
        self.mock = mock
        self.set_base_url(mock)
        self.api_key = api_key
        self.api_secret = api_secret

        # account number
        self.acc_no = acc_no
        self.acc_no_prefix = acc_no.split('-')[0]
        self.acc_no_postfix = acc_no.split('-')[1]

        self.exchange = exchange

        # access token
        self.access_token = None
        if self.check_access_token():
            self.load_access_token()
        else:
            self.issue_access_token()

    def set_base_url(self, mock: bool = True):
        """테스트(모의투자) 서버 사용 설정
        Args:
            mock(bool, optional): True: 테스트서버, False: 실서버 Defaults to True.
        """
        if mock:
            self.base_url = "https://openapivts.koreainvestment.com:29443"
        else:
            self.base_url = "https://openapi.koreainvestment.com:9443"

    def issue_access_token(self):
        """OAuth인증/접근토큰발급
        """
        path = "oauth2/tokenP"
        url = f"{self.base_url}/{path}"
        headers = {"content-type": "application/json"}
        data = {
            "grant_type": "client_credentials",
            "appkey": self.api_key,
            "appsecret": self.api_secret
        }

        resp = requests.post(url, headers=headers, data=json.dumps(data))
        resp_data = resp.json()
        self.access_token = f'Bearer {resp_data["access_token"]}'

        # add extra information for the token verification
        now = datetime.datetime.now()
        resp_data['timestamp'] = int(now.timestamp()) + resp_data["expires_in"]
        resp_data['api_key'] = self.api_key
        resp_data['api_secret'] = self.api_secret

        # dump access token
        with open("token.dat", "wb") as f:
            pickle.dump(resp_data, f)

    def check_access_token(self):
        """check access token

        Returns:
            Bool: True: token is valid, False: token is not valid
        """
        try:
            f = open("token.dat", "rb")
            data = pickle.load(f)
            f.close()

            expire_epoch = data['timestamp']
            now_epoch = int(datetime.datetime.now().timestamp())
            status = False

            if ((now_epoch - expire_epoch > 0) or
                (data['api_key'] != self.api_key) or
                (data['api_secret'] != self.api_secret)):
                status = False
            else:
                status = True
            return status
        except IOError:
            return False

    def load_access_token(self):
        """load access token
        """
        with open("token.dat", "rb") as f:
            data = pickle.load(f)
            self.access_token = f'Bearer {data["access_token"]}'

    def issue_hashkey(self, data: dict):
        """해쉬키 발급
        Args:
            data (dict): POST 요청 데이터
        Returns:
            _type_: _description_
        """
        path = "uapi/hashkey"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json",
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "User-Agent": "Mozilla/5.0"
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        haskkey = resp.json()["HASH"]
        return haskkey

    def fetch_price(self, symbol: str) -> dict:
        """fetch price

        Args:
            symbol (str): 종목코드

        Returns:
            dict: _description_
        """
        if self.exchange == "서울":
            return self.fetch_domestic_price("J", symbol)
        else:
            return self.fetch_oversea_price(symbol)

    def fetch_domestic_price(self, market_code: str, symbol: str) -> dict:
        """주식현재가시세
        Args:
            market_code (str): 시장 분류코드
            symbol (str): 종목코드
        Returns:
            dict: API 개발 가이드 참조
        """
        path = "uapi/domestic-stock/v1/quotations/inquire-price"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHKST01010100"
        }
        params = {
            "fid_cond_mrkt_div_code": market_code,
            "fid_input_iscd": symbol
        }
        resp = requests.get(url, headers=headers, params=params)
        return resp.json()

    def fetch_oversea_price(self, symbol: str) -> dict:
        """해외주식 현재체결가
        Args:
            symbol (str): 종목코드
        Returns:
            dict: API 개발 가이드 참조
        """
        path = "uapi/overseas-price/v1/quotations/price"
        url = f"{self.base_url}/{path}"
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
            "SYMB": symbol
        }
        resp = requests.get(url, headers=headers, params=params)
        return resp.json()

    def fetch_today_1m_ohlcv(self, symbol: str, to: str=""):
        """국내주식시세/주식당일분봉조회

        Args:
            symbol (str): 6자리 종목코드
            to (str, optional): "HH:MM:00". Defaults to "".
        """
        result = {}
        now = datetime.datetime.now()

        if to == "":
            to = now.strftime("%H%M%S")

            # kospi market end time
            if to > "153000":
                to = "153000"

        output = self._fetch_today_1m_ohlcv(symbol, to)
        output2 = output['output2']
        last_hour = output2[-1]['stck_cntg_hour']

        result['output1'] = output['output1']
        result['output2'] = output2

        while last_hour > "090100":
            # last minute
            dt1 = datetime.datetime(
                year=now.year,
                month=now.month,
                day=now.day,
                hour=int(last_hour[:2]),
                minute=int(last_hour[2:4])
            )
            delta = datetime.timedelta(minutes=1)

            # 1 minute ago
            dt2 = dt1 - delta
            to = dt2.strftime("%H%M%S")

            # request 1minute ohlcv
            output = self._fetch_today_1m_ohlcv(symbol, to)
            output2 = output['output2']
            last_hour = output2[-1]['stck_cntg_hour']

            result['output2'].extend(output2)

        return result

    def _fetch_today_1m_ohlcv(self, symbol: str, to: str):
        """국내주식시세/주식당일분봉조회

        Args:
            symbol (str): 6자리 종목코드
            to (str): "HH:MM:SS"
        """
        path = "/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json; charset=utf-8",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "FHKST03010200",
           "tr_cont": "",
        }

        params = {
            "fid_etc_cls_code": "",
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": symbol,
            "fid_input_hour_1": to,
            "fid_pw_data_incu_yn": "Y"
        }
        res = requests.get(url, headers=headers, params=params)
        return res.json()

    def fetch_ohlcv(self, symbol: str, timeframe: str = 'D', adj_price: bool = True) -> dict:
        """국내주식시세/주식 현재가 일자별
        Args:
            symbol (str): 종목코드
            timeframe (str): "D" (일), "W" (주), "M" (월)
            adj_price (bool, optional): True: 수정주가 반영, False: 수정주가 미반영. Defaults to True.
        Returns:
            dict: _description_
        """
        path = "uapi/domestic-stock/v1/quotations/inquire-daily-price"
        url = f"{self.base_url}/{path}"
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
            "fid_input_iscd": symbol,
            "fid_org_adj_prc": adj_param,
            "fid_period_div_code": timeframe
        }
        res = requests.get(url, headers=headers, params=params)
        return res.json()

    def fetch_symbols(self):
        """fetch symbols from the exchange

        Returns:
            pd.DataFrame: pandas dataframe
        """
        if self.exchange == "서울":
            df = self.fetch_kospi_symbols()
            kospi_df = df[['단축코드', '한글명', '그룹코드']].copy()
            kospi_df['시장'] = '코스피'

            df = self.fetch_kosdaq_symbols()
            kosdaq_df = df[['단축코드', '한글명', '그룹코드']].copy()
            kosdaq_df['시장'] = '코스닥'

            df = pd.concat([kospi_df, kosdaq_df], axis=0)

        return df

    def download_master_file(self, base_dir: str, file_name: str, url: str):
        """download master file

        Args:
            base_dir (str): download directory
            file_name (str: filename
            url (str): url
        """
        os.chdir(base_dir)

        # delete legacy master file
        if os.path.exists(file_name):
            os.remove(file_name)

        # download master file
        resp = requests.get(url)
        with open(file_name, "wb") as f:
            f.write(resp.content)

        # unzip
        kospi_zip = zipfile.ZipFile(file_name)
        kospi_zip.extractall()
        kospi_zip.close()

    def parse_kospi_master(self, base_dir: str):
        """parse kospi master file

        Args:
            base_dir (str): directory where kospi code exists

        Returns:
            _type_: _description_
        """
        file_name = base_dir + "/kospi_code.mst"
        tmp_fil1 = base_dir + "/kospi_code_part1.tmp"
        tmp_fil2 = base_dir + "/kospi_code_part2.tmp"

        wf1 = open(tmp_fil1, mode="w")
        wf2 = open(tmp_fil2, mode="w")

        with open(file_name, mode="r", encoding="cp949") as f:
            for row in f:
                rf1 = row[0:len(row) - 228]
                rf1_1 = rf1[0:9].rstrip()
                rf1_2 = rf1[9:21].rstrip()
                rf1_3 = rf1[21:].strip()
                wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + '\n')
                rf2 = row[-228:]
                wf2.write(rf2)

        wf1.close()
        wf2.close()

        part1_columns = ['단축코드', '표준코드', '한글명']
        df1 = pd.read_csv(tmp_fil1, header=None, names=part1_columns)

        field_specs = [
            2, 1, 4, 4, 4,
            1, 1, 1, 1, 1,
            1, 1, 1, 1, 1,
            1, 1, 1, 1, 1,
            1, 1, 1, 1, 1,
            1, 1, 1, 1, 1,
            1, 9, 5, 5, 1,
            1, 1, 2, 1, 1,
            1, 2, 2, 2, 3,
            1, 3, 12, 12, 8,
            15, 21, 2, 7, 1,
            1, 1, 1, 1, 9,
            9, 9, 5, 9, 8,
            9, 3, 1, 1, 1
        ]

        part2_columns = [
            '그룹코드', '시가총액규모', '지수업종대분류', '지수업종중분류', '지수업종소분류',
            '제조업', '저유동성', '지배구조지수종목', 'KOSPI200섹터업종', 'KOSPI100',
            'KOSPI50', 'KRX', 'ETP', 'ELW발행', 'KRX100',
            'KRX자동차', 'KRX반도체', 'KRX바이오', 'KRX은행', 'SPAC',
            'KRX에너지화학', 'KRX철강', '단기과열', 'KRX미디어통신', 'KRX건설',
            'Non1', 'KRX증권', 'KRX선박', 'KRX섹터_보험', 'KRX섹터_운송',
            'SRI', '기준가', '매매수량단위', '시간외수량단위', '거래정지',
            '정리매매', '관리종목', '시장경고', '경고예고', '불성실공시',
            '우회상장', '락구분', '액면변경', '증자구분', '증거금비율',
            '신용가능', '신용기간', '전일거래량', '액면가', '상장일자',
            '상장주수', '자본금', '결산월', '공모가', '우선주',
            '공매도과열', '이상급등', 'KRX300', 'KOSPI', '매출액',
            '영업이익', '경상이익', '당기순이익', 'ROE', '기준년월',
            '시가총액', '그룹사코드', '회사신용한도초과', '담보대출가능', '대주가능'
        ]

        df2 = pd.read_fwf(tmp_fil2, widths=field_specs, names=part2_columns)
        df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True)

        # clean temporary file and dataframe
        del (df1)
        del (df2)
        os.remove(tmp_fil1)
        os.remove(tmp_fil2)
        return df

    def parse_kosdaq_master(self, base_dir: str):
        """parse kosdaq master file

        Args:
            base_dir (str): directory where kosdaq code exists

        Returns:
            _type_: _description_
        """
        file_name = base_dir + "/kosdaq_code.mst"
        tmp_fil1 = base_dir +  "/kosdaq_code_part1.tmp"
        tmp_fil2 = base_dir +  "/kosdaq_code_part2.tmp"

        wf1 = open(tmp_fil1, mode="w")
        wf2 = open(tmp_fil2, mode="w")
        with open(file_name, mode="r", encoding="cp949") as f:
            for row in f:
                rf1 = row[0:len(row) - 222]
                rf1_1 = rf1[0:9].rstrip()
                rf1_2 = rf1[9:21].rstrip()
                rf1_3 = rf1[21:].strip()
                wf1.write(rf1_1 + ',' + rf1_2 + ',' + rf1_3 + '\n')

                rf2 = row[-222:]
                wf2.write(rf2)

        wf1.close()
        wf2.close()

        part1_columns = ['단축코드', '표준코드', '한글명']
        df1 = pd.read_csv(tmp_fil1, header=None, names=part1_columns)

        field_specs = [
            2, 1, 4, 4, 4,      # line 20
            1, 1, 1, 1, 1,      # line 27
            1, 1, 1, 1, 1,      # line 32
            1, 1, 1, 1, 1,      # line 38
            1, 1, 1, 1, 1,      # line 43
            1, 9, 5, 5, 1,      # line 48
            1, 1, 2, 1, 1,      # line 54
            1, 2, 2, 2, 3,      # line 64
            1, 3, 12, 12, 8,    # line 69
            15, 21, 2, 7, 1,    # line 75
            1, 1, 1, 9, 9,      # line 80
            9, 5, 9, 8, 9,      # line 85
            3, 1, 1, 1
        ]

        part2_columns = [
            '그룹코드', '시가총액규모', '지수업종대분류', '지수업종중분류', '지수업종소분류', # line 20
            '벤처기업', '저유동성', 'KRX', 'ETP', 'KRX100',  # line 27
            'KRX자동차', 'KRX반도체', 'KRX바이오', 'KRX은행', 'SPAC',   # line 32
            'KRX에너지화학', 'KRX철강', '단기과열', 'KRX미디어통신', 'KRX건설', # line 38
            '투자주의', 'KRX증권', 'KRX선박', 'KRX섹터_보험', 'KRX섹터_운송',   # line 43
            'KOSDAQ150', '기준가', '매매수량단위', '시간외수량단위', '거래정지',    # line 48
            '정리매매', '관리종목', '시장경고', '경고예고', '불성실공시',   # line 54
            '우회상장', '락구분', '액면변경', '증자구분', '증거금비율',     # line 64
            '신용가능', '신용기간', '전일거래량', '액면가', '상장일자',     # line 69
            '상장주수', '자본금', '결산월', '공모가', '우선주',     # line 75
            '공매도과열', '이상급등', 'KRX300', '매출액', '영업이익',   # line 80
            '경상이익', '당기순이익', 'ROE', '기준년월', '시가총액',    # line 85
            '그룹사코드', '회사신용한도초과', '담보대출가능', '대주가능'
        ]

        df2 = pd.read_fwf(tmp_fil2, widths=field_specs, names=part2_columns)
        df = pd.merge(df1, df2, how='outer', left_index=True, right_index=True)

        # clean temporary file and dataframe
        del (df1)
        del (df2)
        os.remove(tmp_fil1)
        os.remove(tmp_fil2)
        return df

    def fetch_kospi_symbols(self):
        """코스피 종목 코드

        Returns:
            DataFrame:
        """
        base_dir = os.getcwd()
        file_name = "kospi_code.mst.zip"
        url = "https://new.real.download.dws.co.kr/common/master/" + file_name
        self.download_master_file(base_dir, file_name, url)
        df = self.parse_kospi_master(base_dir)
        return df

    def fetch_kosdaq_symbols(self):
        """코스닥 종목 코드

        Returns:
            DataFrame:
        """
        base_dir = os.getcwd()
        file_name = "kosdaq_code.mst.zip"
        url = "https://new.real.download.dws.co.kr/common/master/" + file_name
        self.download_master_file(base_dir, file_name, url)
        df = self.parse_kosdaq_master(base_dir)
        return df

    def fetch_balance(self) -> dict:
        """잔고 조회

        Args:

        Returns:
            dict: response data
        """
        if self.exchange == '서울':
            output = {}

            data = self.fetch_balance_domestic()
            output['output1'] = data['output1']
            output['output2'] = data['output2']

            while data['tr_cont'] == 'M':
                fk100 = data['ctx_area_fk100']
                nk100 = data['ctx_area_nk100']

                data = self.fetch_balance_domestic(fk100, nk100)
                output['output1'].extend(data['output1'])
                output['output2'].extend(data['output2'])

            return output
        else:
            return self.fetch_balance_oversea()

    def fetch_balance_domestic(self, ctx_area_fk100: str = "", ctx_area_nk100: str = "") -> dict:
        """국내주식주문/주식잔고조회
        Args:
            ctx_area_fk100 (str): 연속조회검색조건100
            ctx_areak_nk100 (str): 연속조회키100
        Returns:
            dict: _description_
        """
        path = "uapi/domestic-stock/v1/trading/inquire-balance"
        url = f"{self.base_url}/{path}"
        headers = {
           "content-type": "application/json",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "VTTC8434R" if self.mock else "TTTC8434R"
        }
        params = {
            'CANO': self.acc_no_prefix,
            'ACNT_PRDT_CD': self.acc_no_postfix,
            'AFHR_FLPR_YN': 'N',
            'OFL_YN': 'N',
            'INQR_DVSN': '01',
            'UNPR_DVSN': '01',
            'FUND_STTL_ICLD_YN': 'N',
            'FNCG_AMT_AUTO_RDPT_YN': 'N',
            'PRCS_DVSN': '01',
            'CTX_AREA_FK100': ctx_area_fk100,
            'CTX_AREA_NK100': ctx_area_nk100
        }

        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        data['tr_cont'] = res.headers['tr_cont']
        return data

    def fetch_balance_oversea(self) -> dict:
        """해외주식 잔고조회
        Args:
        Returns:
            dict: _description_
        """
        path = "/uapi/overseas-stock/v1/trading/inquire-present-balance"
        url = f"{self.base_url}/{path}"

        headers = {
           "content-type": "application/json",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "CTRP6504R"
        }

        params = {
            'CANO': self.acc_no_prefix,
            'ACNT_PRDT_CD': self.acc_no_postfix,
            "WCRC_FRCR_DVSN_CD": "02",
            "NATN_CD": "840",
            "TR_MKET_CD": "01",
            "INQR_DVSN_CD": "00"
        }
        res = requests.get(url, headers=headers, params=params)
        return res.json()

    def fetch_balance_oversea2(self) -> dict:
        """해외주식 잔고조회
        Args:
        Returns:
            dict: _description_
        """
        path = "/uapi/overseas-stock/v1/trading/inquire-balance"
        url = f"{self.base_url}/{path}"

        if self.exchange in ['나스닥', '뉴욕', '아멕스']:
            tr_id = "JTTT3012R"
        else:
            tr_id = "TTTS3012R"

        headers = {
           "content-type": "application/json",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": tr_id
        }

        exchange_cd = EXCHANGE_CODE2[self.exchange]
        currency_cd = CURRENCY_CODE[self.exchange]
        params = {
            'CANO': self.acc_no_prefix,
            'ACNT_PRDT_CD': self.acc_no_postfix,
            'OVRS_EXCG_CD': exchange_cd,
            'TR_CRCY_CD': currency_cd,
            'CTX_AREA_FK200': "",
            'CTX_AREA_NK200': ""
        }
        res = requests.get(url, headers=headers, params=params)
        return res.json()

    def create_order(self, side: str, symbol: str, price: int,
                     quantity: int, order_type: str) -> dict:
        """국내주식주문/주식주문(현금)

        Args:
            side (str): _description_
            symbol (str): symbol
            price (int): _description_
            quantity (int): _description_
            order_type (str): _description_

        Returns:
            dict: _description_
        """
        path = "uapi/domestic-stock/v1/trading/order-cash"
        url = f"{self.base_url}/{path}"

        if self.mock:
            tr_id = "VTTC0802U" if side == "buy" else "VTTC0801U"
        else:
            tr_id = "TTTC0802U" if side == "buy" else "TTTC0801U"

        unpr = "0" if order_type == "01" else str(price)

        data = {
            "CANO": self.acc_no_prefix,
            "ACNT_PRDT_CD": self.acc_no_postfix,
            "PDNO": symbol,
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
           "hashkey": hashkey
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        return resp.json()

    def create_market_buy_order(self, symbol: str, quantity: int) -> dict:
        """시장가 매수

        Args:
            symbol (str): _description_
            quantity (int): _description_

        Returns:
            dict: _description_
        """
        return self.create_order("buy", symbol, 0, quantity, "01")

    def create_market_sell_order(self, symbol: str, quantity: int) -> dict:
        """시장가 매도

        Args:
            symbol (str): _description_
            quantity (int): _description_

        Returns:
            dict: _description_
        """
        return self.create_order("sell", symbol, 0, quantity, "01")

    def create_limit_buy_order(self, symbol: str, price: int, quantity: int) -> dict:
        """지정가 매수

        Args:
            symbol (str): 종목코드
            price (int): 가격
            quantity (int): 수량

        Returns:
            dict: _description_
        """
        if self.exchange == "서울":
            resp = self.create_order("buy", symbol, price, quantity, "00")
        else:
            resp = self.create_oversea_order("buy", symbol, price, quantity, "00")

        return resp

    def create_limit_sell_order(self, symbol: str, price: int, quantity: int) -> dict:
        """지정가 매도

        Args:
            symbol (str): _description_
            price (int): _description_
            quantity (int): _description_

        Returns:
            dict: _description_
        """
        if self.exchange == "서울":
            resp = self.create_order("sell", symbol, price, quantity, "00")
        else:
            resp = self.create_oversea_order("sell", symbol, price, quantity, "00")
        return resp

    def cancel_order(self, order_code: str, order_id: str, order_type: str,
                     price: int, quantity: int):
        """주문 취소

        Args:
            order_code (str): _description_
            order_id (str): _description_
            order_type (str): _description_
            price (int): _description_
            quantity (int): _description_

        Returns:
            _type_: _description_
        """
        return self.update_order(
            order_code, order_id, order_type, price, quantity, is_change=False
        )

    def modify_order(self, order_code: str, order_id: str, order_type: str,
                     price: int, quantity: int):
        """_summary_

        Args:
            order_code (str): _description_
            order_id (str): _description_
            order_type (str): _description_
            price (int): _description_
            quantity (int): _description_

        Returns:
            _type_: _description_
        """
        return self.update_order(order_code, order_id, order_type, price, quantity)

    def update_order(self, order_code: str, order_id: str, order_type: str, price: int,
                     quantity: int, is_change: bool = True):
        """_summary_

        Args:
            order_code (str): _description_
            order_id (str): _description_
            order_type (str): _description_
            price (int): _description_
            quantity (int): _description_
            is_change (bool, optional): _description_. Defaults to True.

        Returns:
            _type_: _description_
        """
        path = "uapi/domestic-stock/v1/trading/order-rvsecncl"
        url = f"{self.base_url}/{path}"
        param = "01" if is_change else "02"
        data = {
            "CANO": self.acc_no_prefix,
            "ACNT_PRDT_CD": self.acc_no_postfix,
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
           "hashkey": hashkey
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        return resp.json()

    def fetch_open_order(self, param: dict):
        """주식 정정/취소가능 주문 조회
        Args:
            param (dict): 세부 파라미터
        Returns:
            _type_: _description_
        """
        path = "uapi/domestic-stock/v1/trading/inquire-psbl-rvsecncl"
        url = f"{self.base_url}/{path}"

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
            "CANO": self.acc_no_prefix,
            "ACNT_PRDT_CD": self.acc_no_postfix,
            "CTX_AREA_FK100": fk100,
            "CTX_AREA_NK100": nk100,
            "INQR_DVSN_1": type1,
            "INQR_DVSN_2": type2
        }

        resp = requests.get(url, headers=headers, params=params)
        return resp.json()

    def create_oversea_order(self, side: str, symbol: str, price: int,
                             quantity: int, order_type: str) -> dict:
        """_summary_

        Args:
            side (str): _description_
            symbol (str): _description_
            price (int): _description_
            quantity (int): _description_
            order_type (str): _description_

        Returns:
            dict: _description_
        """
        path = "uapi/overseas-stock/v1/trading/order"
        url = f"{self.base_url}/{path}"

        if side == "buy":
            tr_id = "JTTT1002U"
        else:
            tr_id = "JTTT1006U"

        exchange_cd = EXCHANGE_CODE2[self.exchange]
        data = {
            "CANO": self.acc_no_prefix,
            "ACNT_PRDT_CD": self.acc_no_postfix,
            "OVRS_EXCG_CD": exchange_cd,
            "PDNO": symbol,
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
           "hashkey": hashkey
        }
        resp = requests.post(url, headers=headers, data=json.dumps(data))
        return resp.json()

    def fetch_ohlcv2(self, symbol: str, timeframe:str='1d', to:str="",
                    adjusted:bool=True):
        """해외주식현재가-해외주식기간별시세
           해외주식의 기반별 시세를 확인하는 API

        Args:
            symbol (str): 종목코드
            timeframe (str, optional): '1d', '1w', '1m'
            since (str, optional): YYYYMMDD
            adjusted (bool, optional): False: 수정주가 미반영, True: 수정주가 반영
        """
        path = "/uapi/overseas-price/v1/quotations/dailyprice"
        url = f"{self.base_url}/{path}"

        headers = {
           "content-type": "application/json",
           "authorization": self.access_token,
           "appKey": self.api_key,
           "appSecret": self.api_secret,
           "tr_id": "HHDFS76240000"
        }

        timeframe_lookup = {
            '1d': "0",
            '1w': "1",
            '1m': "2"
        }

        params = {
            "AUTH": "",
            "EXCD": EXCHANGE_CODE.get(self.exchange, "NAS"),
            "SYMB": symbol,
            "GUBN": timeframe_lookup.get(timeframe, "1d"),
            "BYMD": to,
            "MODP": 1 if adjusted else 0
        }
        resp = requests.get(url, headers=headers, params=params)
        return resp.json()

if __name__ == "__main__":
    import pprint

    with open("../koreainvestment.key", encoding='utf-8') as key_file:
        lines = key_file.readlines()

    key = lines[0].strip()
    secret = lines[1].strip()
    ACC_NO = "63398082-01"

    broker = KoreaInvestment(
        api_key=key,
        api_secret=secret,
        acc_no=ACC_NO
    )

    minute1_ohlcv = broker.fetch_today_1m_ohlcv("005930")
    pprint.pprint(minute1_ohlcv)

    #broker = KoreaInvestment(key, secret, exchange="나스닥")
    #import pprint
    #resp = broker.fetch_price("005930")
    #pprint.pprint(resp)
    #
    # resp = broker.fetch_daily_price("005930")
    # pprint.pprint(resp)
    #
    #b = broker.fetch_balance("63398082")
    #pprint.pprint(b)
    #
    # resp = broker.create_market_buy_order("63398082", "005930", 10)
    # pprint.pprint(resp)
    #
    # resp = broker.cancel_order("63398082", "91252", "0000117057", "00", 60000, 5, "Y")
    # print(resp)
    #
    # resp = broker.create_limit_buy_order("63398082", "TQQQ", 35, 1)
    # print(resp)

    # 실시간주식 체결가
    #broker_ws = KoreaInvestmentWS(
    #   key, secret, ["H0STCNT0", "H0STASP0"], ["005930", "000660"], user_id="idjhh82")
    #broker_ws.start()
    #while True:
    #    data_ = broker_ws.get()
    #    if data_[0] == '체결':
    #        print(data_[1])
    #    elif data_[0] == '호가':
    #        print(data_[1])
    #    elif data_[0] == '체잔':
    #        print(data_[1])

    # 실시간주식호가
    # broker_ws = KoreaInvestmentWS(key, secret, "H0STASP0", "005930")
    # broker_ws.start()
    # for i in range(3):
    #    data = broker_ws.get()
    #    print(data)
    #
    # 실시간주식체결통보
    # broker_ws = KoreaInvestmentWS(key, secret, "H0STCNI0", "user_id")
    # broker_ws.start()
    # for i in range(3):
    #    data = broker_ws.get()
    #    print(data)

    #import pprint
    #broker = KoreaInvestment(key, secret, exchange="나스닥")
    #resp_ohlcv = broker.fetch_ohlcv("TSLA", '1d', to="")
    #print(len(resp_ohlcv['output2']))
    #pprint.pprint(resp_ohlcv['output2'][0])
    #pprint.pprint(resp_ohlcv['output2'][-1])