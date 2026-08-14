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
        logic = data.get('logic', 'smc')
        risk = data.get('risk', '1.0')
        swing = data.get('swing', '10')
        fast = data.get('fast', '9')
        slow = data.get('slow', '21')
        session = data.get('session', 'yes')

        if platform == 'webhook':
            # TradingView / Automation Webhook JSON Payload
            code = f"""{{
  "bot_name": "QTP StratIQ Execution Engine",
  "methodology": "{logic.upper()}",
  "risk_percentage": {risk},
  "parameters": {{
    "swing_lookback_or_fast": {swing if logic == 'smc' else fast},
    "slow_ema": {("'N/A'" if logic == 'smc' else slow)}
  }},
  "session_filter_active": {str(session == 'yes').lower()},
  "action": "{{{{strategy.order.action}}}}",
  "contract_size": "{{{{strategy.order.contracts}}}}",
  "price": "{{{{price}}}}",
  "timestamp": "{{{{timenow}}}}"
}}"""

        elif logic == 'ema':
            if platform == 'pine':
                code = f"""//@version=6
strategy("QTP StratIQ EMA Crossover", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value={risk})

fastEMA = ta.ema(close, {fast})
slowEMA = ta.ema(close, {slow})

if (ta.crossover(fastEMA, slowEMA))
    strategy.entry("EMA Buy", strategy.long)

if (ta.crossunder(fastEMA, slowEMA))
    strategy.entry("EMA Sell", strategy.short)

plot(fastEMA, color=color.cyan, title="Fast EMA")
plot(slowEMA, color=color.yellow, title="Slow EMA")"""
            else:
                code = f"""//+------------------------------------------------------------------+
//|                                     QTP_EMA_Strategy.mq5         |
//|                                  Copyright 2026, QTP StratIQ     |
//+------------------------------------------------------------------+
#property copyright "QTP StratIQ"
#property link      "https://www.qtpstratiq.com"
#property version   "1.00"
#include <Trade\\Trade.mqh>

input double InpRiskPercent = {risk};
input int InpFastEMA = {fast};
input int InpSlowEMA = {slow};

CTrade trade;
int fastMaHandle, slowMaHandle;

int OnInit()
{{
    fastMaHandle = iMA(_Symbol, _Period, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
    slowMaHandle = iMA(_Symbol, _Period, InpSlowEMA, 0, MODE_EMA, PRICE_CLOSE);
    return(INIT_SUCCEEDED);
}}

void OnTick()
{{
    if(PositionsTotal() > 0) return;
    double fastVal[], slowVal[];
    ArraySetAsSeries(fastVal, true);
    ArraySetAsSeries(slowVal, true);
    if(CopyBuffer(fastMaHandle, 0, 0, 2, fastVal) < 2) return;
    if(CopyBuffer(slowMaHandle, 0, 0, 2, slowVal) < 2) return;

    if(fastVal[1] < slowVal[1] && fastVal[0] > slowVal[0])
        trade.Buy(0.1, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_ASK), 0, 0, "EMA Buy");
    if(fastVal[1] > slowVal[1] && fastVal[0] < slowVal[0])
        trade.Sell(0.1, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_BID), 0, 0, "EMA Sell");
}}"""
        else:
            if platform == 'pine':
                code = f"""//@version=6
strategy("QTP StratIQ SMC Suite", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value={risk})

swing_len = input.int({swing}, title="Swing Lookback Period")
use_session = input.bool({str(session == 'yes').lower()}, title="Filter London/NY Session")

highest_high = ta.highest(high, swing_len)
lowest_low = ta.lowest(low, swing_len)

bos_bullish = ta.crossover(close, highest_high[1])
bos_bearish = ta.crossunder(close, lowest_low[1])

in_session = not use_session or (time(timeframe.period, "0800-1600:1234567") != 0)

if (bos_bullish and in_session)
    strategy.entry("SMC Buy", strategy.long)

if (bos_bearish and in_session)
    strategy.entry("SMC Sell", strategy.short)
"""
            else:
                session_check = """
    MqlDateTime dt;
    TimeToStruct(TimeCurrent(), dt);
    if(dt.hour < 8 || dt.hour > 16) return;""" if session == 'yes' else ""

                code = f"""//+------------------------------------------------------------------+
//|                                    QTP_SMC_Institutional.mq5     |
//|                                  Copyright 2026, QTP StratIQ     |
//+------------------------------------------------------------------+
#property copyright "QTP StratIQ"
#property link      "https://www.qtpstratiq.com"
#property version   "2.10"
#include <Trade\\Trade.mqh>

input double InpRiskPercent = {risk};
input int InpSwingPeriod = {swing};
input bool InpSessionFilter = {str(session == 'yes').lower()};

CTrade trade;

int OnInit()
{{
    return(INIT_SUCCEEDED);
}}

void OnTick()
{{
    {session_check}
    if(PositionsTotal() > 0) return;

    double highBuffer[], lowBuffer[];
    ArraySetAsSeries(highBuffer, true);
    ArraySetAsSeries(lowBuffer, true);
    
    CopyHigh(_Symbol, _Period, 0, InpSwingPeriod + 1, highBuffer);
    CopyLow(_Symbol, _Period, 0, InpSwingPeriod + 1, lowBuffer);
    
    double currentClose[];
    ArraySetAsSeries(currentClose, true);
    CopyClose(_Symbol, _Period, 0, 2, currentClose);

    if(ArraySize(highBuffer) < InpSwingPeriod + 1 || ArraySize(currentClose) < 2) return;

    if(currentClose[0] > highBuffer[1])
        trade.Buy(0.1, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_ASK), 0, 0, "SMC Buy");
    else if(currentClose[0] < lowBuffer[1])
        trade.Sell(0.1, _Symbol, SymbolInfoDouble(_Symbol, SYMBOL_BID), 0, 0, "SMC Sell");
}}"""

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"generated_code": code}).encode('utf-8'))
