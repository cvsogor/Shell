from typing import Union
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json

class Convert(BaseModel):
    ccy_from: str
    ccy_to: str
    quantity: float

# FAKE Class
class FXRates():
    def get_rate(self, pair):
        """
        url = "http://fx.com/fxrates?ccy_pair=GBPUSD"
        try:
            response = requests.get(url)
            response.raise_for_status()  
            resp = response.json()
            rate = json.loads(resp)
            return rate["rate"]
        except requests.exceptions.RequestException as e:
            return 0.0
        """
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
        #triangulation rule via USD
        usd = "USD"
        rate1 = fx.get_rate(ccy_from + usd)
        rate2 = fx.get_rate(usd + ccy_to)
        if (rate1 != 0) and (rate2 != 0):
            rate = rate1 * rate2
    return rate


@app.post("/converter/")
def read_item(convert: Convert):
    if convert.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity should be more than 0")
    
    rate = get_rate(convert.ccy_from, convert.ccy_to)
    if rate == 0:
        rate = get_rate(convert.ccy_to, convert.ccy_from)
        if rate != 0:
            rate = 1/rate
        else:
            raise HTTPException(status_code=404, detail="Currency Pair Not Found")

    final = convert.quantity*rate
    return {"quantity": final, "ccy":convert.ccy_to}

