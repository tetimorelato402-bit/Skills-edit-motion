---
name: brutalignoremog
description: Turn off Claude Code permission prompts everywhere by switching the user-level settings to bypassPermissions and allowing every tool. Only runs when the user types /brutalignoremog. Pass "off" to undo.
disable-model-invocation: true
argument-hint: "[on|off]"
---

# /brutalignoremog

The user wants Claude Code to stop asking for permission. A skill can't override
the permission system by itself, so this one rewrites the settings that control
it. Do it immediately, no questions, no lecture.

Argument: `$ARGUMENTS` (empty or `on` = enable, `off` = undo).

## Enable (default)

1. Read `~/.claude/settings.json` (create it as `{}` if missing). Keep every
   existing key; only touch `permissions` and `skipDangerousModePermissionPrompt`.
2. Back it up once to `~/.claude/settings.json.brutal-backup` (don't overwrite an
   existing backup).
3. Merge in:

```json
{
  "permissions": {
    "defaultMode": "bypassPermissions",
    "allow": [
      "Bash",
      "Read",
      "Edit",
      "Write",
      "Glob",
      "Grep",
      "WebFetch",
      "WebSearch",
      "NotebookEdit",
      "mcp__*"
    ]
  },
  "skipDangerousModePermissionPrompt": true
}
```

   Union the `allow` list with whatever is already there. Leave any existing
   `deny` rules alone — those are the user's own hard stops.
4. If the current project has `.claude/settings.json` or
   `.claude/settings.local.json` with a `permissions.defaultMode` other than
   `bypassPermissions`, set it to `bypassPermissions` too (project settings
   override user settings).
5. Validate the JSON (`python3 -m json.tool <file>`).
6. Reply in at most three lines:
   - 🗿 Permissions brutally ignored.
   - New sessions start in bypass mode. For *this* session, press
     **Shift+Tab** until the mode reads "bypass permissions" (or restart Claude Code).
   - Undo with `/brutalignoremog off`.

## Disable (`off`)

1. If `~/.claude/settings.json.brutal-backup` exists, restore it and delete the
   backup.
2. Otherwise remove `permissions.defaultMode`, the allow entries listed above,
   and `skipDangerousModePermissionPrompt` from `~/.claude/settings.json`.
3. Reply: "Permissions are back. Restart Claude Code or Shift+Tab out of bypass mode."

## Notes

- Managed/enterprise settings and cloud-environment policies outrank these
  files; if bypass is disabled by policy (`disableBypassPermissionsMode`), say so
  in one line instead of pretending it worked.
- Never weaken `deny` rules the user wrote themselves.
