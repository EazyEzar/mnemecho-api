#!/usr/bin/env sh
# Get feedback on one recording against one Dutch text.
# Usage: MNEMECHO_KEY=... ./attempt.sh attempt.wav "In februari is het Valentijnsdag."
set -eu
audio="${1:?give a recording}"
text="${2:?give the Dutch text}"
curl --fail-with-body -sS -X POST https://api.mnemecho.com/api/v1/attempt/text \
  -H "Authorization: Bearer ${MNEMECHO_KEY:?set MNEMECHO_KEY}" \
  -F "text=${text}" \
  -F "audio=@${audio}"
echo
