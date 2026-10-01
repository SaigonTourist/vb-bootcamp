# Compliance and cost guardrails

This is a working checklist for the session, not legal advice. The bank's data protection and
compliance teams have the final word; bring this page to them.

## People

- **Fictional presenters only.** Presenters are generated from scratch with `vg.py image`. A photo
  of a colleague, client or public figure is never used to make "them" speak or move.
- **Real people only as real footage**, with documented consent for that use (an internal video
  where the speaker agreed to appear). The AI builds around them; it does not alter them.
- **No minors**, in inputs or as generated characters.
- **Voices** come from the models. No voice of a real person is cloned.

## Data (GDPR)

- Prompts and input images leave the bank's systems: they go from Anthropic's cloud to OpenRouter
  and on to the model provider (Google for Veo and Nano Banana Pro, ByteDance for Seedance, MiniMax
  for H3). Some of these providers process data outside the EU.
- So: **no personal data, no client data, no internal confidential information** in prompts,
  images or footage sent for generation. Describe situations generically.
- Before using this beyond the training day, check OpenRouter's and each provider's data retention
  and training policies for the account, and whether the account can be limited to providers that
  do not retain inputs.

## Transparency (EU AI Act)

- Article 50 of the AI Act requires that AI-generated or manipulated images, audio or video that
  could pass as real (deep fakes) are disclosed as such; these transparency duties apply from
  2 August 2026.
- In practice for internal learning videos: a visible note on the card or as a caption, for example
  **"Einige Szenen wurden mit KI erstellt."** whenever generated people or realistic scenes appear.
- Keep the prompt files and the ledger (`jobs/`): they document what was generated and how.

## Cost

- Each participant has a key with a hard credit cap set by the facilitators.
- `vg.py` adds two soft limits: a confirmation line per generation (`VG_CONFIRM_EUR`, default 3 €)
  and a session budget (`VG_BUDGET_EUR`, default 60 €).
- `vg.py estimate` before every expensive call, `vg.py spend` at any time.
- The cheapest saving is discipline: draft Veo shots on `veo-fast`, change one thing per retry,
  never relaunch blind.
