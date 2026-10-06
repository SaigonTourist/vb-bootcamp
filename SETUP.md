# Setup · 08:30, before we start

Ten minutes, all in your browser. Nothing is installed on your laptop. Raise your hand at any step
that does not look like this page.

## 1. Open Claude Code

Go to **claude.ai/code** and sign in with your Claude account. If it asks to connect GitHub, accept.
You should see the repository **vb-bootcamp** in the list (we invited your GitHub account).

## 2. Add the video key to your environment

Open your environment's settings (**Environment: Default**) and choose **Add credential**. Fill it
exactly like this:

| Field | Value |
|---|---|
| Add to | Environment: Default |
| Name | `OPENROUTER` |
| Credential type | Bearer |
| Allowed websites | `openrouter.ai` |
| Path prefixes | `/api/v1/` |
| Custom header · Name | `Authorization` |
| Custom header · Prefix | `Bearer` |
| Custom header · Value | the key on the slip we hand you (the key only, without "Bearer") |

Save. The key never appears in your session, and it is switched off after today.

## 3. Add three settings

In the same environment settings, under **environment variables**, add:

```
VG_USER=yourfirstname
VG_BUDGET_EUR=40
VG_CONFIRM_EUR=3
```

`VG_USER` keeps your work apart from everyone else's. The other two are your spending guard rails:
Claude asks before any single video above 3 €, and stops your session at 40 €.

## 4. Start a session and check

Start a **new session** on **vb-bootcamp** and type:

> Run the doctor.

You are ready when every line shows ✓:

- python
- ffmpeg
- openrouter.ai reachable
- OpenRouter accepts the key

Any ✗: leave the session open and raise your hand.
