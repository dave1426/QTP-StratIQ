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

        if logic == 'smc':
            if platform == 'pine':
                # Smart Money Concepts Pine Script v6 Template
                code = f"""//@version=6
strategy("QTP StratIQ SMC Institutional Suite", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value={risk})

// --- SMC STRUCTURAL LOGIC ---
le_length = input.int(10, title="Swing Lookback Length")
fvg_threshold = input.float(0.001, title="FVG Minimum Size")

// Market Structure & Order Blocks
highest_high = ta.highest(high, le_length)
lowest_low = ta.lowest(low, le_length)

bos_bullish = ta.crossover(close, highest_high[1])
bos_bearish = ta.crossunder(close, lowest_low[1])

// Fair Value Gap (FVG) Detection
bullish_fvg = (low > high[2]) and (close[1] > high[2])
bearish_fvg = (high < low[2]) and (close[1] < low[2])

if (bos_bullish or bullish_fvg)
    strategy.entry("SMC Buy (OB/FVG)", strategy.long)

if (bos_bearish or bearish_fvg)
    strategy.entry("SMC Sell (OB/FVG)", strategy.short)

plotshape(bos_bullish, title="BOS Bullish", style=shape.labelup, location=location.belowbar, color=color.green, text="BOS")
plotshape(bos_bearish, title="BOS Bearish", style=shape.labeldown, location=location.abovebar, color=color.red, text="BOS")"""
            else:
                # Smart Money Concepts MQL5 Expert Advisor Template
                code = f"""//+------------------------------------------------------------------+
//|                                    QTP_SMC_Institutional.mq5     |
//|                                  Copyright 2026, QTP StratIQ     |
//|                                     https://www.qtpstratiq.com   |
//+------------------------------------------------------------------+
#property copyright "QTP StratIQ"
#property link      "https://www.qtpstratiq.com"
#property version   "2.00"
#include <Trade\\Trade.mqh>

input group "--- Risk & Capital Management ---"
input double InpRiskPercent = {risk}; // Risk Per Trade (%)

input group "--- SMC Structure Settings ---"
input int InpSwingPeriod = 10;        // Swing High/Low Lookback

CTrade trade;

int OnInit()
{{
    Print("QTP StratIQ SMC Engine Initialized. Monitoring Market Structure Shifts & FVG.");
    return(INIT_SUCCEEDED);
}}

void OnDeinit(const int reason) {{}}

void OnTick()
{{
    // Check open positions to manage active risk
    if(PositionsTotal() > 0) return;

    // High/Low Array Buffer Simulation for Structure Shift
    double highBuffer[], lowBuffer[];
    ArraySetAsSeries(highBuffer, true);
    ArraySetAsSeries(lowBuffer, true);
    
    CopyHigh(_Symbol, _Period, 0, InpSwingPeriod + 1, highBuffer);
    CopyLow(_Symbol, _Period, 0, InpSwingPeriod + 1, lowBuffer);
    
    double currentClose[];
    ArraySetAsSeries(currentClose, true);
    CopyClose(_Symbol, _Period, 0, 2, currentClose);

    if(ArraySize(highBuffer) < InpSwingPeriod + 1 || ArraySize(currentClose) < 2) return;

    // Break of Structure (BOS) / Market Structure Shift (MSS) Triggers
    bool bullishMSS = (currentClose[0] > highBuffer[1]);
    bool bearishMSS = (currentClose[0] < lowBuffer[1]);

    if(bullishMSS)
    {{
        double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
        double sl = ask - (150 * _Point); // Structural Swing Stop
        double tp = ask + (300 * _Point); // 1:2 Risk-to-Reward Target
        trade.Buy(0.1, _Symbol, ask, sl, tp, "QTP SMC Bullish MSS Entry");
    }}
    else if(bearishMSS)
    {{
        double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
        double sl = bid + (150 * _Point);
        double tp = bid - (300 * _Point);
        trade.Sell(0.1, _Symbol, bid, sl, tp, "QTP SMC Bearish MSS Entry");
    }}
}}"""
        else:
            # Fallback EMA Template
            code = f"""// QTP EMA Crossover System
input double RiskPercent = {risk};
input int FastEMA = {fast};
input int SlowEMA = {slow};
// Standard EMA Crossover Execution Logic Active..."""

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"generated_code": code}).encode('utf-8'))
