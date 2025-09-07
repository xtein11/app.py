import os, json, requests
from flask import Flask, request, jsonify
app = Flask(__name__)

TOKEN  = os.getenv("TELEGRAM_TOKEN")
CHATID = os.getenv("TELEGRAM_CHAT_ID")
TG_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

def get_first(d,*kk,default=None):
    for k in kk:
        cur=d
        ok=True
        for part in k.split("."):
            if isinstance(cur,dict) and part in cur: cur=cur[part]
            else: ok=False; break
        if ok and cur not in (None,"","[]",[]): return cur
    return default

@app.post("/webhook")
def webhook():
    p = request.get_json(force=True, silent=False)
    if not isinstance(p,dict): return jsonify({"ok":False,"error":"payload_not_dict"}),400
    action = get_first(p,"action","order_action","strategy.order_action","STRATEGY.ORDER.ACTION",default="N/A")
    ticker = get_first(p,"ticker","symbol","instrument",default="N/A")
    tf     = get_first(p,"tf","interval","timeframe",default="-")
    price  = get_first(p,"price","entry","entry_price","close",default="-")
    rsi    = get_first(p,"rsi",default="-")
    text = f"⚡ TradingView Сигнал\n─────────────────────────\nДействие: {action}\nАктив: {ticker} ({tf})\nЦена входа: {price}\nRSI: {rsi}"
    r = requests.post(TG_URL, json={"chat_id":CHATID,"text":text,"disable_web_page_preview":True}, timeout=10)
    ok = r.ok and r.json().get("ok",False)
    return (jsonify({"ok":True}),200) if ok else (jsonify({"ok":False,"tg":r.text}),502)

@app.get("/")
def root(): return "OK"
