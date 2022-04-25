import mojito
import pprint

with open("../../koreainvestment.key") as f:
    lines = f.readlines()
key = lines[0].strip()
secret = lines[1].strip()


if __name__ == "__main__":
    broker_ws = mojito.KoreaInvestmentWS(
        api_key=key,
        api_secret=secret,
        tr_id_list=["H0STASP0"],
        tr_key_list=["005930", "000660"],
        user_id="idjhh82"
    )

    broker_ws.start()
    while True:
        data = broker_ws.get_orderbook()
        print(data)


