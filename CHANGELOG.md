# Changelog

Changes to the mnemEcho Pronunciation API, newest first. Within v1, fields and
flags may be added; existing ones keep working.

## 2026-10-23

- `GET /status`: no key, any origin, `{"ok": true}` when the service answers.
- Public documentation, OpenAPI description, examples and this repository.

## 2026-10-23 (scoring)

- `words[].wrong_word`: a word heard as a different word (maart for februari) is
  marked, the word's `ok` is false, and the attempt cannot pass. New flag
  `wrong_word=N`.

## 2026-10-17

- v1 opens for early access: `POST /score`, `GET /health`.
