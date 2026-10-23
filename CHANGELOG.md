# Changelog

Changes to the mnemEcho Pronunciation API, newest first. Within v1, fields and
flags may be added; existing ones keep working.

## 2026-10-24

- Self-serve keys: make, list and revoke them at https://account.mnemecho.com/keys.
  An account holds up to five keys sharing one quota.
- Tiers: no key (3 scores an hour per address), free (10 an hour, 100 a day). Paid
  plans follow.
- `POST /score/text`: the new name of `POST /score`, which keeps working.
- `GET /usage`: each plan and what is left in each window.
- `POST /feedback`: needs, bugs and payment methods wanted; no key needed.
- 402 `quota_exhausted` and `no_plan`, with `resets_at` and where to get more.
- Every error carries a stable `error` code beside `detail`.
- Responses carry `model` and `tier`; scored responses carry `X-RateLimit-*` headers.
- Failed requests no longer cost quota (they count toward the minute rate only).

## 2026-10-23

- `GET /status`: no key, any origin, `{"ok": true}` when the service answers.
- Public documentation, OpenAPI description, examples and this repository.

## 2026-10-23 (scoring)

- `words[].wrong_word`: a word heard as a different word (maart for februari) is
  marked, the word's `ok` is false, and the attempt cannot pass. New flag
  `wrong_word=N`.

## 2026-10-17

- v1 opens for early access: `POST /score`, `GET /health`.
