#!/bin/bash
# Start all background services for Wolfgang's automation stack

echo "=== Wolfgang's Service Startup ==="

echo ""
echo "Starting Vapi webhook handler..."
pkill -f vapi-webhook.py 2>/dev/null
sleep 0.5
nohup python3 /root/.openclaw/workspace/scripts/vapi-webhook.py > /tmp/vapi-webhook.log 2>&1 &
WEBHOOK_PID=$!
echo "Vapi webhook PID: $WEBHOOK_PID"

# Wait and verify it started
sleep 2
if kill -0 $WEBHOOK_PID 2>/dev/null; then
  echo "✅ Vapi webhook running on port 8765"
else
  echo "❌ Vapi webhook failed to start — check /tmp/vapi-webhook.log"
fi

echo ""
echo "Starting n8n..."
if docker info >/dev/null 2>&1; then
  if docker ps -a --filter name=n8n --format '{{.Names}}' | grep -q '^n8n$'; then
    docker start n8n 2>/dev/null && echo "✅ n8n started at http://localhost:5678" || echo "❌ Failed to start n8n container"
  else
    echo "⚠️  n8n container not found. Run setup to create it."
    echo "   docker run -d --name n8n --restart unless-stopped -p 5678:5678 \\"
    echo "     -e N8N_BASIC_AUTH_ACTIVE=true -e N8N_BASIC_AUTH_USER=wolfgang \\"
    echo "     -e N8N_BASIC_AUTH_PASSWORD=Bummerland20 -v n8n_data:/home/node/.n8n n8nio/n8n"
  fi
else
  echo "⚠️  Docker not available — n8n not started"
fi

echo ""
echo "=== Service Status ==="
echo "Vapi webhook:  http://localhost:8765"
echo "n8n dashboard: http://localhost:5678 (user: wolfgang)"
echo ""
echo "Logs:"
echo "  Vapi webhook: /tmp/vapi-webhook.log"
echo "  n8n:          docker logs n8n"
echo ""
echo "All services started. ✅"
