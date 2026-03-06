#!/bin/bash
# ============================================================
#  PantryMate Keystore Generator
#  Run this ONCE and store the output securely.
#  NEVER commit the .keystore file to version control.
# ============================================================

set -e

KEYSTORE_FILE="pantrymate.keystore"
KEY_ALIAS="pantrymate"
KEY_VALIDITY=10000   # ~27 years

echo "🔑 Generating PantryMate release keystore..."
echo ""
echo "You will be prompted for:"
echo "  - A keystore password (STORE_PASSWORD)"
echo "  - A key password (KEY_PASSWORD)  ← can be the same as store password"
echo "  - Your name / organization / location (for the cert)"
echo ""

keytool -genkey -v \
  -keystore "$KEYSTORE_FILE" \
  -alias "$KEY_ALIAS" \
  -keyalg RSA \
  -keysize 2048 \
  -validity $KEY_VALIDITY

echo ""
echo "✅ Keystore created: $KEYSTORE_FILE"
echo ""
echo "============================================================"
echo "  NEXT: Add these 4 secrets to GitHub"
echo "  Repo → Settings → Secrets and variables → Actions → New"
echo "============================================================"
echo ""
echo "1. KEYSTORE_FILE  (base64-encoded keystore)"
echo "   Run:"
echo "     base64 -w 0 $KEYSTORE_FILE | pbcopy   # macOS"
echo "     base64 -w 0 $KEYSTORE_FILE            # Linux (copy the output)"
echo ""
echo "2. KEY_ALIAS      = $KEY_ALIAS"
echo ""
echo "3. KEY_PASSWORD   = <the key password you just set>"
echo ""
echo "4. STORE_PASSWORD = <the keystore password you just set>"
echo ""
echo "⚠️  Back up $KEYSTORE_FILE somewhere safe (1Password, Bitwarden, etc.)"
echo "    You CANNOT re-upload to Play Store with a different keystore."
echo ""
