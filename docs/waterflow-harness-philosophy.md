# Waterflow Harness Philosophy

## Thesis

The harness is not a bigger green test suite. It is a controlled way to make the auditor's claims falsifiable.

Waterflow exists to find workflow coordination failures before a long-horizon agent stack amplifies them. A useful harness must therefore create known bad water paths, known clean high-volume paths, and known command failures. The expected result is mixed: injected defects should be found, clean scale should stay clean, and validation failures should be recorded as failures.

The complex incident harness adds one more claim: after Waterflow finds a realistic multi-route problem, it must explain that problem in a repair packet another agent can actually use.

## Pass Semantics

A stress run passes only when all three claims hold:

- The problem fixture detects every expected defect family.
- The scale fixture reaches the requested route count without unexpected findings.
- The needle fixture finds small injected defects inside a large otherwise-clean graph.
- The validation stress plan records one pass, one failing command, and one timeout.

This means a harness pass is not "everything is fine." It means the diagnostic system can distinguish expected good, expected bad, expected fail, and expected timeout.

The incident harness uses the same semantics. Its pass means detection, evidence capture, diff generation, and Codex/Claude handoff generation worked. It is not a claim that the incident fixture has been fixed.

## Why Inject Problems

Passive scans can only say what they currently see. They cannot prove the detector would notice a realistic break. Problem injection gives the auditor a known target:

- malformed route metadata;
- duplicate routing;
- missing entrypoints;
- unvalidated scripts;
- empty evidence files;
- cross-boundary references;
- progress claims without evidence;
- validation commands that fail or time out.

If any expected target is missed, the harness fails even when the real lab scan is clean.

## Why Keep Fixtures Isolated

The harness intentionally creates bad files. These files must remain generated artifacts under `outputs/shared/waterflow/stress/`. They are evidence about the auditor, not source waterways for the real lab.

This prevents negative fixtures from contaminating the real lab graph, changing agent discovery, or becoming accidental operating rules.

## Why Scale Is Separate

Scale pressure answers a different question from problem injection. The scale fixture should be structurally clean. Its job is to expose performance, graph-shape, and false-positive issues as route count grows.

Problem fixtures test sensitivity. Scale fixtures test stability.

## Why Needle Fixtures Exist

A large clean graph does not prove small problems remain visible. Needle fixtures create a mostly clean large graph and then inject a few targeted defects. They test whether the scanner can keep high recall when the signal is tiny relative to total path count.

Needle fixtures answer the practical question: if one byte-sized route breaks in a very large system, does the auditor still surface it with a repairable finding?

## Why Incident Handoffs Exist

Stress results prove detector coverage, but large agent systems also fail at the handoff layer: a report can be technically correct yet still leave Codex or Claude without a clear repair order.

The incident harness therefore creates a realistic bad workflow and writes `codex-claude-handoff.md`. That handoff must include exact findings, evidence paths, failing commands, exit codes, timeout state, route-family priority, artifact paths, and minimal verification commands.

This checks the practical question: once Waterflow finds a complex coordination problem, can the next agent repair it without guessing what failed first?

## Design Rule

When the Waterflow Auditor gains a new detector, the harness should gain a matching injected defect. When the auditor gains a new route family, the scale fixture should learn to generate that route family. When validation semantics change, the stress plan should include a controlled example of the new success and failure modes.

## Coverage Contract

The stress harness enforces detector coverage directly. It reads implemented finding codes from `waterflow/auditor.py`, compares them with the codes detected in the generated problem fixture, and fails if any implemented detector has no injected proof case.

This turns the design rule into a machine check:

- new detector without injected defect: fail;
- expected defect without implementation: fail;
- injected defect not detected: fail;
- clean scale with unexpected finding: fail;
- needle defect hidden by graph size: fail;
- stale diff or changed-only evidence presented as current: fail;
- expected command failure not recorded: fail.
- complex incident detected but not translated into an actionable Codex/Claude handoff: fail.

The practical result is that harness pressure can improve the auditor itself. A clean real-lab scan is no longer enough; the auditor must also prove that its detector vocabulary is covered by adversarial examples.
