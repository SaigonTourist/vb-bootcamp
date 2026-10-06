# Dry run

Facilitators' checklist to take this repo from "built" to "rehearsed". Everything below happens in
Claude Code on the web, the way the participants will work, except the paid probes and reserves,
which we can also run from our own machines.

## 0. Open decisions

- [ ] **Bucket or no bucket** for watching clips in the browser. Without it, clips are committed and
      pushed to the session branch and opened from GitHub. With it (S3 or Cloudflare R2), `vg.py`
      prints signed links that play in the browser and `vg.py gallery` builds one page per person.
      Decide after testing what the bank's proxy lets through.
- [ ] **Where the repo lives** (our GitHub organisation with participants invited, or theirs).

## 1. Questions for the bank (Jonas)

- [ ] Plan for Claude Code on the web (Team / Enterprise), and whether participants can edit their
      cloud environment (allowed domains, environment variables) or an admin has to.
- [ ] GitHub connected to their Claude accounts, and whether they can open or clone a repository we
      share with them.
- [ ] From the office browser: do claude.ai and github.com open, and do videos play on github.com?
      If we use a bucket: does its link play? (`vg.py doctor` prints a test link.)
- [ ] Send participants `BRING_YOUR_MATERIAL.md` (module text, photos of places and people, a clip they own) and check they can upload to github.com from the bank network.

## 2. Setup (facilitators)

1. **Repository.** Push this repo to a private GitHub repository and give the participants access.
2. **One OpenRouter key for everyone**, named after the day, with a hard credit limit of 150 $
   (about 25 $ per participant plus margin). Revoke it the evening of 8 October. The per-session
   soft cap `VG_BUDGET_EUR=40` stops any single session from eating the shared credit.
3. **Cloud environment** in Claude Code on the web, one per participant (or shared, if variables
   can be per user):
   - Network access: the default trusted list plus **`openrouter.ai`** (and the bucket host if any).
   - The key as a **managed credential** (the key never enters the container): type Bearer,
     allowed website `openrouter.ai`, path prefix `/api/v1/`, header `Authorization`, prefix
     `Bearer`, value = the shared key. `vg.py doctor` confirms it is accepted.
   - Environment variables:
     ```
     VG_USER=<first name, no spaces>
     VG_CONFIRM_EUR=3
     VG_BUDGET_EUR=40
     ```
     Bucket, only if used: `VG_S3_ENDPOINT`, `VG_S3_BUCKET`, `VG_S3_REGION` (`auto` for R2),
     `VG_S3_ACCESS_KEY`, `VG_S3_SECRET_KEY`, `VG_S3_PREFIX`.
4. **Paid probes** (about 6.80 $). They prove the German lip sync with banking vocabulary and the
   Veo and Seedance payloads through OpenRouter:
   ```bash
   bash probes/run_probes.sh
   VG_USER=probes python3 .claude/skills/video-gen/scripts/vg.py wait
   ```
   On our machine, check the German with whisper, then listen to all three:
   ```bash
   /Users/alan.johnson/Desktop/GoStudent/.venv/bin/python probes/check_de.py
   ```
5. **Reserves** (about 11.50 $ for 11 generations; prints the plan, sends nothing without `--go`):
   ```bash
   python3 scripts/make_reserves.py
   python3 scripts/make_reserves.py --go
   VG_USER=reserves python3 .claude/skills/video-gen/scripts/vg.py wait
   ```
   Review every reserve, regenerate the bad ones, then commit `templates/*/reserves/` and the
   start frames in `input/refs/`.

## 2b. Seedance straight through ModelArk (live demo, and fallback if OpenRouter is down)

`scripts/ark_seedance_probe.py` makes one Seedance 2.5 call directly against BytePlus ModelArk,
standard library only. Needs `ARK_API_KEY` in the environment and, in the cloud,
`ark.ap-southeast.bytepluses.com` plus the download host it reports in the allowed domains.

```bash
python3 scripts/ark_seedance_probe.py --check     # free: key and network only
python3 scripts/ark_seedance_probe.py             # one 5 s clip, about 108k video tokens
```

## 3. The rehearsal (fresh cloud session, timed like the day)

Open a new session on the repo with the dry-run key and work only through the chat, as a designer.

| Step | What to ask Claude | Expect |
|---|---|---|
| Start | (nothing) | The session-start hook installs ffmpeg in the container |
| 1 | "Run the doctor" | All ✓; `openrouter.ai reachable`; key credit shown |
| 2 | "Show me the three templates" | Status of A, B, C with costs to fill |
| 3 | "Fill template A in mock mode" (`VG_MOCK=1`) | Whole flow without spending; preview of 20.4 s |
| 4 | "Make the presenter for A" | `input/refs/presenter_A.png` in under a minute |
| 5 | "Launch s3, s2 and a veo-fast draft of s1" | Three jobs queued, `wait` running in the background |
| 6 | While they render: "Rewrite s1 so the man is sitting already" | Lint, estimate, one change named |
| 7 | When they land: "Build the preview" | `out/A_teaser_preview.mp4`, watchable from the browser |
| 8 | "What have I spent?" | `vg.py spend` total, matches OpenRouter's key page |

Record: minutes to the first launched render (target under 20), real render times per model, cost
per participant, anything the browser could not open.

## 4. Before the day

- [ ] `jobs/` contains only `probes.jsonl` and `reserves.jsonl`; delete the dry-run ledger.
- [ ] The shared key created with its 150 $ limit, every participant's environment configured and tested with `doctor`.
- [ ] Reminder set to revoke the shared key after the day.
- [ ] Reserves reviewed and committed; previews of A, B and C build from reserves alone.
- [ ] The corrected PDF sent: the IT list is claude.ai, github.com (and the bucket host), not the
      video endpoints; the fallback is pre-generated clips, not guest wifi.
