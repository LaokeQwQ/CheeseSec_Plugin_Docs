# CheeseSec Plugin handbook constraints

- Keep Chinese and English instructions aligned with the CheeseWAF source and
  acceptance tests.
- Mark contract-only examples clearly; do not describe unimplemented install,
  OTA, or runtime behavior as available.
- Do not publish signing keys, tokens, customer data, generated output, or
  `@agent-eyes`/`code-inspector`/`codex-acp` tooling.
- Every security-sensitive example must state the confirmation, audit,
  rollback, and offline behavior that applies.
