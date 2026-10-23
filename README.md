# mnemEcho Pronunciation API

Score Dutch speech against its text. Send a Dutch sentence and a recording of
someone saying it; get back a score from 0 to 100, a verdict, and every word and
sound marked, with a short English tip on each sound to work on.

- Docs: https://mnemecho.com/en/docs/
- OpenAPI: [`openapi.json`](openapi.json)
- For AI agents: [`llms.txt`](llms.txt)
- Status: https://mnemecho.com/en/status/

This repository holds the public documentation, examples and the source of
mnemecho.com. The scoring service itself is not open source.

## Quick start

Make a free key at https://account.mnemecho.com/keys (email or Google sign in, no
card): 10 scores an hour, 100 a day. With no key you can try 3 scores an hour.

```sh
export MNEMECHO_KEY=...
curl -X POST https://api.mnemecho.com/api/v1/score/text \
  -H "Authorization: Bearer $MNEMECHO_KEY" \
  -F "text=In februari is het Valentijnsdag." \
  -F "audio=@attempt.wav"
```

```json
{
  "score": 91.6,
  "verdict": "pass",
  "worst_word": "februari",
  "words": [
    {"word": "februari", "ok": false, "wrong_word": false, "sounds": [
      {"target": "eː", "heard": "ɛ", "ok": false, "quality": 0.6629,
       "hint": "the long ee in zee"}
    ]}
  ],
  "flags": ["unobservable_phones=1", "no_reference"]
}
```

(Trimmed; the full response has every word and sound.)

## Examples

| | |
|---|---|
| [`examples/curl/score.sh`](examples/curl/score.sh) | curl |
| [`examples/python/score.py`](examples/python/score.py) | Python, `requests` |
| [`examples/js/score.mjs`](examples/js/score.mjs) | Node 18+, no dependencies |

## What is graded

Pronunciation only: whether each expected sound was said, and said right, and
whether each word is the word in the text. Rhythm, pitch and vowel length need a
native recording of the same sentence and are not graded here. Voice quality is
never graded. Audio and text are scored in memory and never stored.

## Issues and requests

Open an issue for a bug, a feature you need, or a payment method you need. We
read every one.

## The site

`site-src/` holds the pages of mnemecho.com in English and Dutch, and
`tools/build_site.py` builds them into `site/`, which Cloudflare Pages serves as
is. After editing a page:

```sh
python3 tools/build_site.py --check
```

## Licence

Code and examples in this repository: MIT, see [`LICENSE`](LICENSE). The fonts in
`site-src/assets/fonts` are under the SIL Open Font License 1.1 (files beside
them). The mnemEcho name and logo are not licensed for reuse.

mnemEcho is a product of Invership B.V., Mechelenstraat 66, 4826 KN Breda,
KvK 97741876.
