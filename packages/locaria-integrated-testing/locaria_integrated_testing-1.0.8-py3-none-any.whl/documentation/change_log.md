### Integrated Tests Change Log

This change log records all notable updates to the `integrated_tests` package. Its purpose is to capture changes as we implement them so we can:
- Keep the team up to date in real time
- Consolidate updates into the main documentation in one pass
- Maintain a clear history for auditing and troubleshooting

### Scope
- Changes to test suites (new tests, refactors, removals)
- Test data updates and fixtures
- Test utilities/helpers and shared test infrastructure
- CI test configuration relevant to integrated tests

### How to record changes
Add an entry for every meaningful change as soon as it lands (or when opening the PR). Prefer small, frequent entries over large batched summaries.

- **Date**: YYYY-MM-DD
- **Author**: your name/handle
- **Area**: file(s) or module(s) touched
- **Type**: Add | Change | Fix | Remove | Docs | Infra
- **Description**: concise but specific
- **Rationale**: why this change was needed (if non-obvious)
- **Impact**: behavior, coverage, performance, or developer workflow implications
- **Links**: PR, or related docs

### Format
- Keep entries in reverse chronological order.
- Group under a version heading if applicable; otherwise use an "Unreleased" section at the top.
- Use short, scannable bullets; include links for traceability.

#### Entry template
```text
#### YYYY-MM-DD — Type — Short title
- Author: <name>
- Area: <path/to/test_or_helper.py>
- Description: <what changed>
- Rationale: <why> (optional)
- Impact: <behavior/coverage/infra effects>
- Links: PR #<id>
```

---

### Logs
#### 2025-11-18 - Feature - Per-Issue Firestore Docs & Ownership Metadata
- Author: Thorsten
- Area:
    - locaria_integrated_testing/main/acknowledge_manager.py
    - locaria_integrated_testing/main/testkit.py
    - locaria_integrated_testing/__init__.py
- Description:
    - Move from a single `{repo}%{pipeline}%{test_name}` document with an `issues` map to a per-issue subcollection structure: `pipeline_acknowledgments/{test_doc}/issues/{issue_key_simple}`.
    - Each issue document now stores `issue_first_occurrence`, `issue_last_occurrence`, `issue_owner`, and all additional metadata alongside `acknowledged` / `muted_until`, enabling long-term tracking and ownership.
    - Update `batch_update_issue_detections` to batch-read and batch-write individual issue docs, preserving existing acknowledgment state while updating occurrence timestamps and metadata.
    - Align `check_issue_acknowledged` and `acknowledge_issue` with the new structure so muted issues continue to be filtered correctly without relying on the legacy `issues` map.
- Impact:
    - Eliminates document-size limits for noisy tests by storing one Firestore document per issue instead of a giant map.
    - Enables accurate, per-issue history (first/last occurrence) and ownership for the FIN acknowledgment UI and future tooling.
    - Requires pipelines and apps consuming the data to use the new per-issue structure (no backward compatibility with the old map layout in v1.0.7).
- Version:
    - Bumped package version to `1.0.7`.

#### 2025-11-15 - Feature - Batched Acknowledgments & Per-Issue Identifiers
- Author: Thorsten
- Area:
    - locaria_integrated_testing/main/testkit.py
    - locaria_integrated_testing/main/acknowledge_manager.py
    - locaria_integrated_testing/__init__.py
- Description:
    - Introduce batched acknowledgment writes: all acknowledgeable WARN results are persisted to Firestore once per test at `finalize_run()`, via `batch_update_issue_detections`.
    - Ensure every warning and failure carries a stable `issue_identifier` and `metrics['issue_details']` so issues are uniquely trackable and render well in emails/UI.
    - Add support for rich per-issue metadata while keeping the Firestore document structure (`pipeline_acknowledgments/{repo}%{pipeline}%{test_name}`) fully backwards compatible.
    - Clean up the public API: `finalize_run()` no longer takes a run-level identifier, and `log_warn`/`log_fail` do not write to Firestore directly.
- Impact:
    - All pipelines using v1.0.5 get per-issue acknowledgment, muted issues filtered out of digests, and significantly fewer Firestore writes per run.
- Version:
    - Bumped package version to `1.0.5`.

#### 2025-10-29 - Fix - Test Core
- Author: Pablo
- Area: 
    - modules/integrated_tests/main/acknowledge_manager.py
    - modules/integrated_tests/main/testkit.py
- Description: 
    - Remove unused arguments from key functions (e.g., `issue_type`, `issue_key`).
    - Make sure additional metadata is logged via the metrics argument so it can be stored in Firestore.
    - Make `issue_identifier` a required argument everywhere possible.
    - Disable pass tests logging
    - Remove hacky workarounds from logging functions that were meant to retrieve the issue identifier from legacy fields.
    - Change hardcoded references to centralized variables.
- Impact: All the scripts where the Integrated Tests were already written, and the ones coming.
- Links: https://github.com/Locaria/locate_2_pulls/pull/7

#### 2025-10-29 - Fix - Generic Tests
- Author: Pablo
- Area: 
    - modules/integrated_tests/generic_tests/data_quality_tests.py
    - modules/integrated_tests/generic_tests/duplicate_tests.py
    - modules/integrated_tests/generic_tests/freshness_tests.py
    - modules/integrated_tests/generic_tests/row_count_tests.py
- Description: 
    - Improve the logs in the different functions by adding more & clearer arguments.
    - Added a `caller_script` argument on the generic tests `__init__` function, so we can have more context in the logs.
    - Streamline the `issue_identifier` definition in each function by dynamically pulling the caller script and the function names (instead of hardcoding them).
    - Created `check_column_completeness()` inside `duplicate_tests.py` to be able to see the completeness in certain columns individually, and not in the whole DataFrame at once.
- Impact: All the scripts where the Integrated Tests were already written, and the ones coming.
- Links: https://github.com/Locaria/locate_2_pulls/pull/7