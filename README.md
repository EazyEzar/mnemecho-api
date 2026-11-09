# mnemEcho Pronunciation API

Pronunciation feedback on Dutch speech. Send a Dutch sentence and a recording of
someone saying it; get back practice feedback on that recording: a match from 0 to 100, a feedback band, and every word and
sound marked, with a short English tip on each sound to work on.

- Docs: https://api.mnemecho.com/en/docs/
- OpenAPI: [`openapi.json`](openapi.json)
- For AI agents: [`llms.txt`](llms.txt)
- Status: https://api.mnemecho.com/en/status/

This repository holds the public documentation, examples and the source of
mnemecho.com. The service itself is not open source.

## Quick start

Make a free key at https://account.mnemecho.com/keys (email or Google sign in, no
card): 5 recordings an hour, 10 a day. With no key you can try 3 recordings an hour. Both
check only five example sentences, listed in the docs; your own sentences need a paid plan.

```sh
export MNEMECHO_KEY=...
curl -X POST https://api.mnemecho.com/api/v1/attempt/text \
  -H "Authorization: Bearer $MNEMECHO_KEY" \
  -F "text=In februari is het Valentijnsdag." \
  -F "audio=@attempt.wav"
```

```json
{
  "match": 91.6,
  "band": "clear",
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
| [`examples/curl/attempt.sh`](examples/curl/attempt.sh) | curl |
| [`examples/python/attempt.py`](examples/python/attempt.py) | Python, `requests` |
| [`examples/js/attempt.mjs`](examples/js/attempt.mjs) | Node 18+, no dependencies |

## What is graded

Pronunciation only: whether each expected sound was said, and said right, and
whether each word is the word in the text. Rhythm, pitch and vowel length need a
native recording of the same sentence and are not graded here. Voice quality is
never graded. Audio and text are checked in memory and never stored.

## Issues and requests

Open an issue for a bug, a feature you need, or a payment method you need. We
read every one.

## The site

`site-src/pages/` holds mnemecho.com (the learner app) and `site-src/dev/` the
developer pages at api.mnemecho.com, each in English and Dutch. `tools/build_site.py`
builds them into `site/`, which Cloudflare Pages serves as is, and `site-dev/`, which
the API server serves on its own hostname. After editing a page:

```sh
python3 tools/build_site.py --check
```

## Licence

Code and examples in this repository: MIT, see [`LICENSE`](LICENSE). The fonts in
`site-src/assets/fonts` are under the SIL Open Font License 1.1 (files beside
them). The mnemEcho name and logo are not licensed for reuse.

mnemEcho is a product of Invership B.V., Mechelenstraat 66, 4826 KN Breda,
KvK 97741876.
