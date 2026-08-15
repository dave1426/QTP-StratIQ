from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for active bot telemetry
active_bots_state = [
    {"id": "1", "name": "QTP SPECTATOR v4.2 (XAUUSD)", "platform": "MQL5", "status": "Active", "pnl": "+$840.00 (2.1R)", "lastPing": "Just now"},
    {"id": "2", "name": "QTP BREAKBIAS v3.3 (GER30)", "platform": "Pine v6", "status": "Active", "pnl": "+$580.50 (1.6R)", "lastPing": "45s ago"}
]

# 1. Strategy Translation Endpoint
@app.route('/api/translate', methods=['POST'])
def translate_strategy():
    data = request.json
    platform = data.get('platform', 'pine')
    logic = data.get('logic', 'smc')
    risk = data.get('risk', '1.0')
    
    if platform == 'mql5':
        code = f"""//+------------------------------------------------------------------+
//|                                              QTP_Auto_System.mq5 |
//|                                  Copyright 2026, QTP StratIQ     |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026"
#property link      "https://www.qtpsig.com"
#property version   "1.00"

input double RiskPercent = {risk};
input string LogicType   = "{logic}";

int OnInit()
{{
   Print("QTP System Initialized: Risk ", RiskPercent, "%");
   return(INIT_SUCCEEDED);
}}
"""
    elif platform == 'webhook':
        code = f"""{{
  "event": "QTP_SIGNAL",
  "logic": "{logic}",
  "risk_percent": {risk},
  "timestamp": "2026-08-15T00:00:00Z"
}}"""
    else:
        code = f"""// @version=6
strategy("QTP StratIQ System", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value={risk})

logicType = input.string("{logic}", title="Methodology")
swingLen  = input.int(10, title="Swing Period")

isBOS = ta.crossover(close, ta.highest(high, swingLen))
isCHoCH = ta.crossunder(close, ta.lowest(low, swingLen))

if (isBOS)
    strategy.entry("QTP Long", strategy.long)

if (isCHoCH)
    strategy.close("QTP Long")
"""

    return jsonify({"generated_code": code})

# 2. Webhook Endpoint for TradingView / MT5 Alerts
@app.route('/api/webhook', methods=['POST'])
def handle_webhook():
    incoming_data = request.json
    print("Incoming Webhook Payload:", incoming_data)
    
    bot_name = incoming_data.get('name', 'QTP System')
    pnl = incoming_data.get('pnl', '+$0.00')
    
    for bot in active_bots_state:
        if bot['name'] in bot_name or bot_name in bot['name']:
            bot['pnl'] = pnl
            bot['lastPing'] = 'Just now'
            
    return jsonify({"status": "success", "message": "Telemetry updated successfully"}), 200

# 3. Telemetry Endpoint for Dashboard Monitoring
@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    return jsonify({"bots": active_bots_state})

if __name__ == '__main__':
    app.run(debug=True)
