from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

class Convert(BaseModel):
    ccy_from: str
    ccy_to: str
    quantity: float

class FXRates():
    def get_rate(self, pair):
        #GET request with parameter “?ccy_pair=GBPUSD”
        pairs = {"EURUSD": 1.16, "GBPUSD": 1.34, "USDCAD": 1.39, "USDJPY": 148.71, "EURGBP": 0.86}
        if pair in pairs:
            rate = pairs[pair]
        else:
            rate = 0.0
        return rate

app = FastAPI()

@app.get("/")
def read_root():
    return {"FX": "Converter"}

#@app.get("/converter/{item_id}")
#def read_item(item_id: int, q: Union[str, None] = None):
#    return {"quantity": 779.77, "ccy":"GBP"}

def get_rate(ccy_from, ccy_to):
    fx = FXRates()
    pair = ccy_from + ccy_to
    rate = fx.get_rate(pair)
    if rate == 0:
        rate1 = fx.get_rate(ccy_from + "USD")
        rate2 = fx.get_rate("USD" + ccy_to)
        if (rate1 != 0) and (rate2 != 0):
            rate = rate1 * rate2
    return rate


@app.post("/converter/")
def read_item(convert: Convert):
    rate = get_rate(convert.ccy_from, convert.ccy_to)
    if rate == 0:
        rate = get_rate(convert.ccy_to, convert.ccy_from)
        if rate != 0:
            rate = 1/rate
        else:
            raise HTTPException(status_code=404, detail="Currency Pair Not Found")

    final = convert.quantity*rate
    return {"quantity": final, "ccy":convert.ccy_to}

