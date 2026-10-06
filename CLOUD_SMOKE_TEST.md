# Cloud smoke test

Instructions for Claude, running in a Claude Code on the web session on this repository.

**Goal:** find out whether this cloud environment can run the whole video workflow (generate
through OpenRouter, collect the clip, assemble a template, let the user watch the result) without
the user touching any local file or installing anything on their laptop. Where something does not
work, say exactly what the user has to change and where.

Reply to the user in the language they write in. Keep each step's report to one or two lines.

## Ground rules

- **Never print, echo, log or write the value of any secret** (`OPENROUTER_API_KEY`, `VG_S3_*`).
  Report only whether a variable is set.
- **Spending needs a yes.** Phases 1 to 3 cost nothing. Before phase 4, show the plan with its cost
  and wait for the user's explicit confirmation. Never pass `--over-budget`.
- Use `VG_USER=smoketest` for every `vg.py` command, so this run has its own ledger.
- Do not modify the skill, the templates or the tests. If something is broken, report it; do not
  patch it in this session.
- Run commands from the repository root.

## Phase 1 · Environment (free)

Run each check and note the result.

1. `python3 --version` (needs 3.8 or newer).
2. `echo "remote=${CLAUDE_CODE_REMOTE:-unset}"` and `uname -a`: confirm this is the cloud container.
3. ffmpeg: `command -v ffmpeg || ls ~/.local/bin/ffmpeg`. If missing, the session-start hook did not
   install it: run `bash scripts/setup_cloud.sh` once and check again. Then check for the text
   filter used by cards and captions: `ffmpeg -hide_banner -filters | grep -c drawtext`.
4. Secrets present, without values. Keys may come as managed credentials (the proxy adds the header and
   the variable does not exist in the container); `vg.py doctor` in step 6 is the real test:
   `for v in OPENROUTER_API_KEY VG_S3_ENDPOINT VG_S3_BUCKET; do [ -n "${!v}" ] && echo "$v set" || echo "$v missing"; done`
   (a missing bucket is fine; it is optional).
5. Network: `curl -s -o /dev/null -w "%{http_code}\n" https://openrouter.ai/api/v1/videos/models`
   (any HTTP code means the host is reachable; a connection error or a proxy 403 page means it is
   blocked by the environment's network settings).
6. `VG_USER=smoketest python3 .claude/skills/video-gen/scripts/vg.py doctor`

## Phase 2 · Code (free)

7. `python3 -m unittest discover -s tests`: every test should pass.
8. `VG_USER=smoketest python3 .claude/skills/video-gen/scripts/vg.py models --live`: the model
   templates should match what OpenRouter lists today. Report any ⚠ line verbatim.

## Phase 3 · Full flow in mock mode (free, no network)

9. With `VG_MOCK=1 VG_USER=smoketest`:
   - `vg.py image --prompt-file templates/A_teaser/prompts/frame_presenter_A.md --out input/refs/presenter_A.png`
   - `vg.py submit seedance --prompt-file templates/A_teaser/prompts/s2.md --dur 5 --slot templates/A_teaser/s2`
   - `vg.py wait`
   - `assemble.py templates/A_teaser`: expect `out/A_teaser_preview.mp4` at about 20.4 s.
10. Undo the mock artefacts so they do not look like real results: delete
    `templates/A_teaser/slots/s2.mp4`, `input/refs/presenter_A.png`, the mock clips in `out/`, and
    `jobs/smoketest.jsonl`.

## Phase 4 · One real generation (paid, about 1.20 $, ask first)

Show the user this plan with the estimates from `vg.py estimate`, and wait for a clear yes:

| Step | Command (prefix `VG_USER=smoketest`) | Estimate |
|---|---|---|
| Start frame | `vg.py image --prompt-file templates/A_teaser/prompts/frame_presenter_A.md --out input/refs/presenter_A.png` | 0.14 $ |
| H3, German line, 5 s | `vg.py submit h3 --prompt-file <a copy of templates/A_teaser/prompts/s3.md with a shorter line> --dur 5 --first-frame input/refs/presenter_A.png --label smoke_h3` | 0.65 $ |
| Veo Fast, 4 s, 720p | `vg.py submit veo-fast --prompt-file templates/A_teaser/prompts/s1.md --dur 4 --resolution 720p --seed 11 --label smoke_veo` | 0.40 $ |

For the H3 copy, keep everything and set the dialogue to `"Ein gutes Gespräch beginnt mit einer FRAGE. Also, ja."`
(fits 5 s). Save it as `out/smoke_h3.md`; do not edit the template.

Then:

11. Run `vg.py wait` in the background (it returns after 9 minutes at most; run it again while
    anything is still rendering). Note the real render time and the real cost of each job.
12. If a download fails, report the **host name only** of the download URL (never the full URL,
    which can carry a token): that host must be added to the environment's allowed domains.
13. Check each clip: extract one frame from the middle with ffmpeg and look at it; confirm the H3
    clip has an audio stream (`ffmpeg -i <file>` shows `Audio:`). Do not judge the lip sync, the
    user does that by watching.
14. `vg.py spend` and compare with the cost OpenRouter reported.

## Phase 5 · Can the user watch it?

The user only has a browser. Try, in this order, and report which works:

15. **Bucket**, if `VG_S3_*` is set: `vg.py publish out/<clip>.mp4` prints a signed link. Give the
    link to the user and ask whether it plays in their browser.
16. **Repository**: commit the two clips and the start frame on this session's branch, push, and
    give the user the link to the branch on GitHub. Ask whether the video plays there.

## The report

End with this table, filled in, and nothing after it except the questions for the user:

| Check | Result | What to change, and where |
|---|---|---|
| Python | | |
| ffmpeg (and drawtext) | | |
| `OPENROUTER_API_KEY` set | | |
| openrouter.ai reachable | | |
| Tests | | |
| Model templates match OpenRouter | | |
| Mock flow and assembly | | |
| Real start frame | | |
| Real H3 clip (time, cost) | | |
| Real Veo Fast clip (time, cost) | | |
| Download host allowed | | |
| User can watch (bucket / GitHub) | | |

Typical fixes to point to:

- **Key not accepted (doctor ✗ "OpenRouter accepts the key"):** claude.ai/code → this environment →
  add a credential: type Bearer, allowed website `openrouter.ai`, path prefix `/api/v1/`, header
  `Authorization` with prefix `Bearer` and the key as value. Or, simpler but less safe, an
  environment variable `OPENROUTER_API_KEY`. Then start a new session: a running session never picks up a credential or variable added after it started.
- **Host blocked:** same settings → network access: keep the trusted defaults and add the host
  (`openrouter.ai`, plus any download host from step 12 and the bucket host if used).
- **ffmpeg could not be installed:** say which route failed (apt or pip) and the error line; the
  package mirrors may be outside the allowed network list.
- **402 from OpenRouter:** the shared key has no credit or hit its limit, on openrouter.ai → Keys. It is shared: tell the facilitator, do not retry.
- **Push refused:** the Claude GitHub app has no write access to this repository.
