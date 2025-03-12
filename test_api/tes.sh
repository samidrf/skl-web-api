#!/bin/bash
USERNAME="admin123"
PASSWORD="tes123"

LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:5000/login \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"${USERNAME}\", \"password\": \"${PASSWORD}\"}")

ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')

if [ "$ACCESS_TOKEN" == "null" ] || [ -z "$ACCESS_TOKEN" ]; then
  echo "Gagal mendapatkan token. Cek kredensial login."
  exit 1
fi

# echo "Token berhasil didapatkan: $ACCESS_TOKEN"

# curl -X GET "http://127.0.0.1:5000/api/skl/form_skl/DIMAS%20RIFQI" \
#   -H "Authorization: Bearer $ACCESS_TOKEN"

QUERY="ANAK SATU"
QUERY_ENCODED=$(echo "$QUERY" | sed 's/ /%20/g') 

echo "API QUERY: $QUERY"

curl -X GET "http://127.0.0.1:5000/api/skl/form_skl/${QUERY_ENCODED}" \
    -H "Authorization: Bearer $ACCESS_TOKEN"