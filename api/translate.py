from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            strategy_name = data.get('strategy_name', 'QTP_Bot')
            fast_ma = data.get('fast_ma', 9)
            slow_ma = data.get('slow_ma', 21)
        except Exception:
            strategy_name = 'QTP_Bot'
            fast_ma = 9
            slow_ma = 21

        # MQL5 Code Template Generation
        mql5_code = f"""//+------------------------------------------------------------------+
//|                                             {strategy_name}.mq5 |
//|                                  Copyright 2026, QTP StratIQ     |
//|                                     https://www.qtpstratiq.com   |
//+------------------------------------------------------------------+
#property copyright "QTP StratIQ"
#property link      "https://www.qtpstratiq.com"
#property version   "1.00"

input int FastPeriod = {fast_ma};
input int SlowPeriod = {slow_ma};
input double LotSize = 0.1;

int fastMaHandle, slowMaHandle;

int OnInit()
{{
    fastMaHandle = iMA(_Symbol, _Period, FastPeriod, 0, MODE_EMA, PRICE_CLOSE);
    slowMaHandle = iMA(_Symbol, _Period, SlowPeriod, 0, MODE_EMA, PRICE_CLOSE);
    return(INIT_SUCCEEDED);
}}

void OnTick()
{{
    double fastVal[], slowVal[];
    ArraySetAsSeries(fastVal, true);
    ArraySetAsSeries(slowVal, true);
    
    CopyBuffer(fastMaHandle, 0, 0, 2, fastVal);
    CopyBuffer(slowMaHandle, 0, 0, 2, slowVal);
    
    if(fastVal[1] < slowVal[1] && fastVal[0] > slowVal[0])
    {{
        Print("QTP StratIQ Signal: Bullish Crossover Detected.");
    }}
}}"""

        response_response = {
            "status": "success",
            "strategy_name": strategy_name,
            "mql5_code": mql5_code
        }

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response_response).encode('utf-8'))
