# WorkBuddy handoff specification

Every packet requiring later user authorization SHALL carry a directly
copyable `AUTHORIZATION_PROMPT.md`. The main thread SHALL reproduce the full
authorization text in its user response when that authorization becomes the
next gate. The main thread SHALL continue through review, acceptance, durable
state updates and next-packet preparation instead of referring those duties to
an unspecified future main thread.
