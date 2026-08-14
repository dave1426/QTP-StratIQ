from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        data = json.loads(self.rfile.read(content_length).decode('utf-8'))
        
        platform = data.get('platform')
        logic = data.get('logic')
        
        if platform == 'pine':
            code = f"//@version=6\nstrategy('{logic.upper()}_Bot', overlay=true)\nfast = ta.ema(close, {data.get('fast', 9)})\nslow = ta.ema(close, {data.get('slow', 21)})\nplot(fast, color=color.blue)\nplot(slow, color=color.yellow)"
        else:
            code = f"// QTP {logic.upper()} MQL5 Expert Advisor\ninput double RiskPercent = {data.get('risk', 1.0)};\n// Logic for {logic} goes here..."

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"generated_code": code}).encode('utf-8'))
