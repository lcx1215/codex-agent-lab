# Scenario Workspace Contract

Scenario workspaces are bounded places for future agent families. They let the lab support UCP agents, commercial customer-service agents, research agents, code-maintenance agents, workflow agents, evaluation agents, and other large agent systems without turning the root lab into any single product template.

## Purpose

Use a scenario workspace when work has a domain, product, customer, integration family, or long-running objective that should stay local until its patterns prove reusable.

The workspace should help Codex and Claude work better by giving them durable state, focused context, runnable checks, local skills, and handoff artifacts. It should not replace their reasoning, coding, review, or recovery responsibilities with rigid automation.

## Required Declarations

Every serious scenario workspace should declare:

- scenario type and objective;
- what is inside the scenario boundary;
- what is outside the scenario boundary;
- how the workspace amplifies Codex and Claude;
- which artifacts are durable state;
- which checks prove progress;
- when a pattern is eligible to move back into the shared lab.

## Scenario Boundary

The boundary keeps a scenario from taking over the lab:

- scenario code, docs, tests, and experiments stay inside the workspace;
- shared scripts or skills move to the root lab only after repeated cross-scenario value;
- scenario-specific assumptions must not be copied into root rules;
- live data, secrets, credentials, and external production effects stay out unless a separate approved boundary exists.

## Codex Claude Amplification

Each workspace should describe how it helps Codex and Claude:

- focused task context instead of broad conversation recall;
- deterministic harnesses for risky behavior;
- validation commands for completion claims;
- handoff notes for App, CLI, OMX, Codex, or Claude continuation;
- route indexes or dashboards when the workspace grows large.

The stop condition is not "the automation says OK." The stop condition is verified progress that Codex or Claude can explain, inspect, and repair.

## Promotion Rule

Promote a scenario pattern into the shared lab only when:

- it has been useful outside one scenario;
- it has a documented purpose and boundary;
- it has a check or test;
- it improves Codex/Claude speed, safety, or reliability without hiding responsibility;
- it does not weaken sandbox, secret, auth, lane, or plugin boundaries.
