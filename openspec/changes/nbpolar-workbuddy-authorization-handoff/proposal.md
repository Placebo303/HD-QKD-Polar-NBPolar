# Proposal: make authorization prompts mandatory WorkBuddy artifacts

Every prepared execution packet must include a directly copyable authorization
message. The main thread must present that text in chat whenever user
authorization is the next gate. This prevents a valid packet from becoming
unusable merely because its status remains all-false and the user has no exact
grant to send to another session.
