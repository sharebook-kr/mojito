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
