from flask import Flask, request, jsonify

app = Flask(__name__)

# Enhanced bot state with kill-switch status and trade logs
active_bots_state = [
    {
        "id": "1", 
        "name": "QTP SPECTATOR v4.2 (XAUUSD)", 
        "platform": "MQL5", 
        "status": "Active", 
        "pnl": "+$840.00 (2.1R)", 
        "lastPing": "12s ago",
        "trades": [
            {"type": "LONG", "entry": "2384.50", "exit": "2405.60", "r": "+2.1R", "time": "14:22"}
        ]
    },
    {
        "id": "2", 
        "name": "QTP BREAKBIAS v3.3 (GER30)", 
        "platform": "Pine v6", 
        "status": "Active", 
        "pnl": "+$580.50 (1.6R)", 
        "lastPing": "45s ago",
        "trades": [
            {"type": "SHORT", "entry": "18450.2", "exit": "18384.0", "r": "+1.6R", "time": "13:05"}
        ]
    }
]

@app.route('/api/translate', methods=['POST'])
def translate_strategy():
    data = request.json
    platform = data.get('platform', 'pine')
    logic = data.get('logic', 'smc')
    risk = data.get('risk', '1.0')
    
    if logic == 'ob':
        logic_title = "Order Block Mitigation"
        pine_logic = "isOB = ta.crossover(close, ta.valuewhen(high == ta.highest(high, 10), high, 0))"
    elif logic == 'sweep':
        logic_title = "Liquidity Sweep"
        pine_logic = "isSweep = (low < ta.lowest(low, 20)[1]) and (close > ta.lowest(low, 20)[1])"
    elif logic == 'ema':
        logic_title = "EMA Trend Crossover"
        pine_logic = "isEMA = ta.crossover(ta.ema(close, 9), ta.ema(close, 21))"
    else:
        logic_title = "Smart Money Concepts (SMC)"
        pine_logic = "isBOS = ta.crossover(close, ta.highest(high, 10))"

    if platform == 'mql5':
        code = f"""//+------------------------------------------------------------------+
//|                                              QTP_Auto_System.mq5 |
//|                                  Methodology: {logic_title}        |
//+------------------------------------------------------------------+
#property copyright "Copyright 2026"
input double RiskPercent = {risk};
input string LogicModel  = "{logic_title}";

int OnInit() {{
   Print("QTP System Initialized: ", LogicModel);
   return(INIT_SUCCEEDED);
}}
"""
    elif platform == 'webhook':
        code = f"""{{
  "event": "QTP_SIGNAL",
  "methodology": "{logic_title}",
  "risk_percent": {risk}
}}"""
    else:
        code = f"""// @version=6
strategy("QTP StratIQ - {logic_title}", overlay=true, default_qty_value={risk})
{pine_logic}
if (true)
    strategy.entry("QTP Exec", strategy.long)
"""
    return jsonify({"generated_code": code})

@app.route('/api/webhook', methods=['POST'])
def handle_webhook():
    incoming_data = request.json
    bot_name = incoming_data.get('name', 'QTP System')
    pnl = incoming_data.get('pnl', '+$0.00')
    trade = incoming_data.get('trade', None)
    
    for bot in active_bots_state:
        if bot['name'] in bot_name or bot_name in bot['name']:
            if bot['status'] == 'Paused':
                return jsonify({"status": "ignored", "message": "Bot is currently paused via kill switch"}), 200
            bot['pnl'] = pnl
            bot['lastPing'] = 'Just now'
            if trade:
                bot['trades'].insert(0, trade)
                if len(bot['trades']) > 5:
                    bot['trades'].pop()
            
    return jsonify({"status": "success", "message": "Telemetry updated successfully"}), 200

@app.route('/api/telemetry', methods=['GET'])
def get_telemetry():
    return jsonify({"bots": active_bots_state})

@app.route('/api/bot/toggle', methods=['POST'])
def toggle_bot():
    data = request.json
    bot_id = data.get('id')
    for bot in active_bots_state:
        if bot['id'] == bot_id:
            bot['status'] = 'Paused' if bot['status'] == 'Active' else 'Active'
            return jsonify({"status": "success", "bot": bot})
    return jsonify({"error": "Bot not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
