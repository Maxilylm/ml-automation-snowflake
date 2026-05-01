<!--
PR template — required fields are enforced by CI.
Reject reason if missing: "PR must reference a Jira ticket (PM3-N) in the title or body".
-->

## Linked Jira ticket

<!-- REQUIRED. Format: PM3-<number>. Multiple tickets OK. -->
<!-- Examples: PM3-12, Closes PM3-45 -->

## Summary

<!-- What changed and why. 1–3 sentences. -->

## Test plan

<!-- How you verified. Include CI logs, local commands run, screenshots if UI. -->
- [ ] Unit tests pass locally for affected plugins
- [ ] Matrix CI green on this PR
- [ ] Reviewed Claude's automated findings (do NOT auto-merge if SECURITY or BREAKING flagged)

## Plugins touched

<!-- Tick all that apply. Helps reviewers and matrix CI scope. -->
- [ ] ab-testing
- [ ] aws
- [ ] azure
- [ ] cv
- [ ] databricks
- [ ] drift
- [ ] explainability
- [ ] gcp
- [ ] llm
- [ ] mmm
- [ ] nlp
- [ ] plugin (meta)
- [ ] snowflake
- [ ] timeseries
- [ ] benchmark
- [ ] tooling / CI / docs only

## Breaking change?

<!-- If yes, describe the migration path. Removing/renaming agents, skills, or manifest fields is breaking. -->
- [ ] No
- [ ] Yes — migration plan:

---

<!--
Smart commit transitions (optional but encouraged in commit messages):
  PM3-12 #in-progress  → moves PM3-12 to In Progress
  PM3-12 #done         → moves PM3-12 to Done on merge
  PM3-12 #time 2h      → logs 2h against PM3-12
See CONTRIBUTING.md.
-->
