"""Score one recording against one Dutch text and print the feedback.

Usage: MNEMECHO_KEY=... python score.py attempt.wav "In februari is het Valentijnsdag."
Needs: pip install requests
"""
import os
import sys
import time

import requests

API = os.environ.get("MNEMECHO_API", "https://api.mnemecho.com/api/v1")


def score(audio_path: str, text: str) -> dict:
    """POST /score/text, waiting once if the limit answers 429."""
    for attempt in range(2):
        with open(audio_path, "rb") as audio:
            resp = requests.post(
                f"{API}/score/text",
                headers={"Authorization": f"Bearer {os.environ['MNEMECHO_KEY']}"},
                data={"text": text},
                files={"audio": audio},
                timeout=30,
            )
        if resp.status_code == 429 and attempt == 0:
            time.sleep(int(resp.headers.get("Retry-After", "5")))
            continue
        if not resp.ok:
            sys.exit(f"{resp.status_code}: {resp.json().get('detail')}")
        return resp.json()
    raise RuntimeError("unreachable")


def main() -> None:
    audio_path, text = sys.argv[1], sys.argv[2]
    result = score(audio_path, text)
    print(f"{result['score']} {result['verdict']}")
    for word in result["words"]:
        if word["wrong_word"]:
            print(f"  {word['word']}: another word was said here")
            continue
        for sound in word["sounds"]:
            if not sound["ok"]:
                print(f"  {word['word']}: /{sound['target']}/ heard as /{sound['heard']}/, {sound['hint']}")


if __name__ == "__main__":
    main()
