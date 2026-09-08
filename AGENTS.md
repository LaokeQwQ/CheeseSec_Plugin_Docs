# CheeseSec Plugin handbook constraints

- Keep Chinese and English instructions aligned with the CheeseWAF source and
  acceptance tests.
- Mark contract-only examples clearly; do not describe unimplemented install,
  OTA, or runtime behavior as available.
- Do not publish signing keys, tokens, customer data, generated output, or
  `@agent-eyes`/`code-inspector`/`codex-acp` tooling.
- Every security-sensitive example must state the confirmation, audit,
  rollback, and offline behavior that applies.
- `schema/crp-v1/` mirrors the publication schema under its public store URL.
  Any change must remain byte-for-byte aligned with the store repository and
  must validate the manifest, signature set, artifact size, MD5, SHA-1,
  SHA-256, and the exact three-entry v1 archive layout.
- Handbook CI uses only `pull_request`, explicit least-privilege permissions,
  and actions pinned by commit SHA. It must never use `pull_request_target`,
  publish a package, or receive signing keys, Tokens, recovery credentials, or
  deployment secrets. The workflow policy script enforces this boundary.
- Keep generated `.crp` files, keys, signatures, local CI environments, and
  generated site output outside Git. The local secret/release-artifact scan is
  a pre-commit gate, not an excuse to place secret examples in prose.
