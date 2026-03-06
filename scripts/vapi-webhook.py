#!/usr/bin/env python3
"""
Vapi End-of-Call Webhook Handler
Receives call reports from Vapi → logs outcomes → flags warm leads → updates call queue

Deploy this as a simple HTTP endpoint (or run locally and expose via ngrok)
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, datetime

CALL_QUEUE = "/root/.openclaw/workspace/assets/call-queue.json"
RESULTS_LOG = "/root/.openclaw/workspace/assets/call-results-live.json"
WARM_LEADS = "/root/.openclaw/workspace/assets/warm-leads.json"

class VapiWebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        
        try:
            data = json.loads(body)
            event_type = data.get('message', {}).get('type', '')
            
            if event_type == 'end-of-call-report':
                self.handle_call_end(data['message'])
            
        except Exception as e:
            print(f"Error: {e}")
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    
    def handle_call_end(self, msg):
        call = msg.get('call', {})
        analysis = msg.get('analysis', {})
        
        call_id = call.get('id', '')
        duration = msg.get('durationSeconds', 0)
        ended_reason = msg.get('endedReason', '')
        summary = analysis.get('summary', '')
        sentiment = analysis.get('successEvaluation', '')
        
        # Load results log
        try:
            with open(RESULTS_LOG) as f:
                results = json.load(f)
        except:
            results = []
        
        result = {
            'call_id': call_id,
            'timestamp': datetime.datetime.utcnow().isoformat(),
            'duration_seconds': duration,
            'ended_reason': ended_reason,
            'summary': summary,
            'sentiment': sentiment,
            'warm_lead': duration > 90  # >90s = warm conversation
        }
        
        results.append(result)
        with open(RESULTS_LOG, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Flag warm leads
        if duration > 90:
            try:
                with open(WARM_LEADS) as f:
                    warm = json.load(f)
            except:
                warm = []
            warm.append(result)
            with open(WARM_LEADS, 'w') as f:
                json.dump(warm, f, indent=2)
            print(f"🔥 WARM LEAD: {call_id} ({duration}s) — {summary[:100]}")
        elif duration < 15:
            print(f"❌ Quick hangup: {call_id} ({duration}s) — {ended_reason}")
        else:
            print(f"✅ Completed: {call_id} ({duration}s)")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8765))
    server = HTTPServer(('0.0.0.0', port), VapiWebhookHandler)
    print(f"Vapi webhook listening on port {port}")
    server.serve_forever()
