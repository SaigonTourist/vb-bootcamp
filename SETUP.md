# Setup · 08:30, before we start

Ten minutes, all in your browser. Nothing is installed on your laptop. Raise your hand at any step
that does not look like this page.

> **Do not start a session until step 4.** A session only sees the key and settings that existed when
> it started. If you already opened one, that is fine: finish steps 2 and 3, then start a **new**
> session and use that one.

## 1. Open Claude Code

1. On **github.com**, signed in with your GitHub account, accept our invitation to **vb-bootcamp**
   (it is in your email and at github.com/SaigonTourist/vb-bootcamp/invitations).
2. Go to **claude.ai/code** and sign in with your Claude account. When it asks to connect GitHub,
   accept with that same GitHub account. If it never asks, connect GitHub from Claude Code's
   settings.
3. You should see the repository **vb-bootcamp** in the list. Your clips reach the Bootcamp wall
   through it, so without this step they stay in your chat only.

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
VG_USER=Anna
VG_BUDGET_EUR=40
VG_CONFIRM_EUR=3
```

`VG_USER` is your first name as the room will see it on the Bootcamp wall: letters only, no spaces, no
accents or umlauts (`Juergen`, not `Jürgen`). It also keeps your work apart from everyone else's. The other two are your spending guard rails:
Claude asks before any single video above 3 €, and stops your session at 40 €.

## 4. Start a session and check

Now, and only now, start a **new session** on **vb-bootcamp** and type:

> Run the doctor.

You are ready when every line shows ✓ and the doctor shows `VG_USER=` with your name (not `designer`):

- python
- ffmpeg
- openrouter.ai reachable
- OpenRouter accepts the key

Any ✗ on the key: check step 2, then start another **new** session (an open session never picks
up a key added later). Anything else: raise your hand.
