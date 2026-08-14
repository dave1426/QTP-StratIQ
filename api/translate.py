from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        try:
            data = json.loads(self.rfile.read(content_length).decode('utf-8'))
        except Exception:
            data = {}
        
        platform = data.get('platform', 'mql5')
        logic = data.get('logic', 'ema')
        risk = data.get('risk', '1.0')
        fast = data.get('fast', '9')
        slow = data.get('slow', '21')

        if platform == 'pine':
            # Full TradingView Pine Script v6 Template
            code = f"""//@version=6
strategy("QTP StratIQ {logic.upper()} Pro", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value={risk})

fastEMA = ta.ema(close, {fast})
slowEMA = ta.ema(close, {slow})

longCondition = ta.crossover(fastEMA, slowEMA)
shortCondition = ta.crossunder(fastEMA, slowEMA)

if (longCondition)
    strategy.entry("QTP Buy", strategy.long)

if (shortCondition)
    strategy.entry("QTP Sell", strategy.short)

plot(fastEMA, color=color.cyan, title="Fast EMA")
plot(slowEMA, color=color.yellow, title="Slow EMA")"""

        else:
            # Full MetaTrader 5 MQL5 Expert Advisor Template
            code = f"""//+------------------------------------------------------------------+
//|                                     QTP_{logic.upper()}_Strategy.mq5 |
//|                                  Copyright 2026, QTP StratIQ     |
//|                                     https://www.qtpstratiq.com   |
//+------------------------------------------------------------------+
#property copyright "QTP StratIQ"
#property link      "https://www.qtpstratiq.com"
#property version   "1.00"
#include <Trade\\Trade.mqh>

input group "--- Risk Management ---"
input double InpRiskPercent = {risk}; // Risk Per Trade (%)

input group "--- Indicator Settings ---"
input int InpFastEMA = {fast};       // Fast EMA Period
input int InpSlowEMA = {slow};       // Slow EMA Period

CTrade trade;
int fastMaHandle, slowMaHandle;

int OnInit()
{{
    fastMaHandle = iMA(_Symbol, _Period, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
    slowMaHandle = iMA(_Symbol, _Period, InpSlowEMA, 0, MODE_EMA, PRICE_CLOSE);
    
    if(fastMaHandle == INVALID_HANDLE || slowMaHandle == INVALID_HANDLE)
        return(INIT_FAILED);
        
    Print("QTP StratIQ Engine Initialized Successfully.");
    return(INIT_SUCCEEDED);
}}

void OnDeinit(const int reason)
{{
    IndicatorRelease(fastMaHandle);
    IndicatorRelease(slowMaHandle);
}}

void OnTick()
{{
    double fastVal[], slowVal[];
    ArraySetAsSeries(fastVal, true);
    ArraySetAsSeries(slowVal, true);
    
    if(CopyBuffer(fastMaHandle, 0, 0, 2, fastVal) < 2) return;
    if(CopyBuffer(slowMaHandle, 0, 0, 2, slowVal) < 2) return;
    
    // Check open positions
    if(PositionsTotal() > 0) return;

    // Bullish Crossover Signal
    if(fastVal[1] < slowVal[1] && fastVal[0] > slowVal[0])
    {{
        double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
        trade.Buy(0.1, _Symbol, ask, 0, 0, "QTP StratIQ Buy Signal");
    }}
    
    // Bearish Crossover Signal
    if(fastVal[1] > slowVal[1] && fastVal[0] < slowVal[0])
    {{
        double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        trade.Sell(0.1, _Symbol, bid, 0, 0, "QTP StratIQ Sell Signal");
    }}
}}"""

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"generated_code": code}).encode('utf-8'))
