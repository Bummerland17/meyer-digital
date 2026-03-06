#!/bin/bash
# Collect leads via Brave Search API
API_KEY="BSA106jyrhl-5L1J4pkHQrw8H0BcesL"
OUTFILE="/root/.openclaw/workspace/smartbook-ai/raw-search-results.txt"
> "$OUTFILE"

search() {
  local query="$1"
  local label="$2"
  echo "=== SEARCH: $label ===" >> "$OUTFILE"
  sleep 2
  curl -s "https://api.search.brave.com/res/v1/web/search?q=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$query'))")&count=10" \
    -H "Accept: application/json" \
    -H "X-Subscription-Token: $API_KEY" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    results = data.get('web', {}).get('results', [])
    for r in results:
        print('TITLE:', r.get('title',''))
        print('URL:', r.get('url',''))
        print('SNIPPET:', r.get('description',''))
        print('---')
except Exception as e:
    print('ERROR:', e)
    sys.stdin = open('/dev/stdin')
    print(sys.stdin.read()[:500])
" >> "$OUTFILE"
  echo "" >> "$OUTFILE"
}

# Phoenix / Scottsdale dental
search "dentist Phoenix AZ independent phone number appointment" "Phoenix dental"
search "dentist Scottsdale AZ solo practice phone" "Scottsdale dental"
search "dentist Tempe Mesa AZ phone number" "Tempe/Mesa dental"

# Phoenix medspa
search "medical spa Phoenix AZ phone number booking" "Phoenix medspa"
search "medical spa Scottsdale AZ phone aesthetics" "Scottsdale medspa"

# Phoenix vet / physio
search "veterinary clinic Phoenix AZ independent phone" "Phoenix vet"
search "physical therapy Phoenix AZ phone number" "Phoenix physio"

# Salt Lake City
search "dentist Salt Lake City UT phone number" "SLC dental"
search "medical spa Salt Lake City UT phone" "SLC medspa"
search "veterinary clinic Salt Lake City UT phone" "SLC vet"
search "physical therapy Salt Lake City Provo UT phone" "SLC physio"

# Denver / Boulder
search "dentist Denver CO independent phone number" "Denver dental"
search "medical spa Denver CO phone" "Denver medspa"
search "veterinary clinic Denver CO phone" "Denver vet"
search "physical therapy Denver Boulder CO phone" "Denver physio"

# Boise
search "dentist Boise Meridian ID phone number" "Boise dental"
search "medical spa Boise ID phone" "Boise medspa"
search "veterinary clinic Boise ID phone" "Boise vet"

# Las Vegas
search "dentist Las Vegas NV independent phone" "LV dental"
search "medical spa Las Vegas NV phone" "LV medspa"
search "physical therapy Las Vegas NV phone" "LV physio"

# Albuquerque
search "dentist Albuquerque NM phone number" "ABQ dental"
search "medical spa Albuquerque NM phone" "ABQ medspa"

echo "DONE" >> "$OUTFILE"
echo "Search complete. Results in $OUTFILE"
