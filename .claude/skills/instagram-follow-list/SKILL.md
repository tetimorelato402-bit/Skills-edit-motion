---
name: instagram-follow-list
description: Add the accounts Anvil followed on Instagram to the Anvil Following List artifact from an Instagram data export (.zip, folder, following.html or following.json). Use when the user sends their daily Instagram export, says "update the following list", or asks to add today's follows.
---

# Anvil Following List

The list lives in one artifact: **https://claude.ai/artifact/GNAkgX4JzjDJUcxficEwdP**
(page source: `anvil-following/index.html`). It has three columns: username, profile link,
and a follower count the user types in on the page. Never create a new artifact for this.
Update the existing one.

## Data model

Collection `days`, one document per day, doc id `YYYY-MM-DD`:

```json
{"date": "2026-10-12", "accounts": [{"u": "username", "at": "2026-10-12T18:12"}], "counts": {"username": 2134}}
```

`counts` holds what the user typed. **Never overwrite or drop it.**

## Daily run

1. Parse the export (it can be the whole zip):
   `python3 -I .claude/skills/instagram-follow-list/parse_following.py <export> > days.json`
   The export always contains the full following list, not just today.
2. Read every existing doc: `ArtifactData` `list` on `days` (limit 1000, follow `next_cursor`).
3. Compare and write in one `ArtifactData` `batch` (50 writes max per batch):
   - Day not in the db: `set` it with `counts: {}`.
   - Day already in the db with new usernames: `update` with only the `accounts` field
     (the full merged list for that day, newest first), pinned with `if_version`.
     Leave `counts` out so the typed numbers stay.
   - Unchanged days: skip.
   - Accounts that were in the db but are missing from the export were unfollowed.
     Don't delete them. Tell the user who they are and ask before removing anyone.
4. Reply with how many accounts were added and for which day, plus the artifact link.

Only use the Anvil anvil mark for branding. Don't add the Instagram logo.
