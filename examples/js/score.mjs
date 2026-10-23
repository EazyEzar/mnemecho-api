// Score one recording against one Dutch text and print the feedback.
// Usage: MNEMECHO_KEY=... node score.mjs attempt.wav "In februari is het Valentijnsdag."
// Node 18 or later, no dependencies.
import { readFile } from "node:fs/promises";
import { basename } from "node:path";

const API = process.env.MNEMECHO_API ?? "https://api.mnemecho.com/api/v1";
const [audioPath, text] = process.argv.slice(2);
if (!audioPath || !text) {
  console.error('usage: node score.mjs attempt.wav "Dutch text"');
  process.exit(2);
}

const form = new FormData();
form.append("text", text);
form.append("audio", new Blob([await readFile(audioPath)]), basename(audioPath));

const resp = await fetch(`${API}/score/text`, {
  method: "POST",
  headers: { Authorization: `Bearer ${process.env.MNEMECHO_KEY}` },
  body: form,
});
const body = await resp.json();
if (!resp.ok) {
  console.error(`${resp.status}: ${body.detail}`);
  process.exit(1);
}

console.log(`${body.score} ${body.verdict}`);
for (const word of body.words) {
  if (word.wrong_word) {
    console.log(`  ${word.word}: another word was said here`);
    continue;
  }
  for (const sound of word.sounds.filter((s) => !s.ok)) {
    console.log(`  ${word.word}: /${sound.target}/ heard as /${sound.heard}/, ${sound.hint}`);
  }
}
