OMC<->OMX interop proof task.

Context: This task travels through the OMC/OMX interop shared-state protocol
(.omc/state/interop). OMC (Claude lane) is the leader and posted this task;
OMX (Codex lane) is the worker and must answer it with the real Codex model.

Request: In 5-8 lines, summarize the concrete engineering value of routing a
task through the file-based interop shared-state protocol (tasks/messages +
artifact descriptors) instead of pasting context between two CLI agents.
Name at least three properties this gives that an ad-hoc copy-paste handoff
does not (e.g. durability, auditability, atomic writes, retention policy).
End with a single line: INTEROP-PROOF-OK <one-word confidence: high|medium|low>.
