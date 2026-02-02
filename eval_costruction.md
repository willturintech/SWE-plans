# SWE-bench Planning Agent Evaluation Framework

This document outlines the evaluation schema for assessing the multi-step reasoning and execution capabilities of AI Planning Agents using the SWE-bench dataset. By selectively masking columns, we create distinct difficulty tiers to measure agent autonomy.

---

## 1. Dataset Column Roles

| Column | Role | Technical Utility |
| :--- | :--- | :--- |
| **`instance_id`** | Identifier | Unique task key for logging and reproducibility. |
| **`problem_statement`** | **The Goal** | The core "Question." Contains the GitHub issue description, bug reports, or feature requests. |
| **`patch`** | **The Answer** | The "Gold Solution." The human-authored code changes that successfully resolved the issue. |
| **`test_patch`** | **Validation Logic** | A set of unit tests designed to fail on the buggy code and pass on the patched code. |
| **`FAIL_TO_PASS`** | Success Criteria | The specific list of tests within the `test_patch` that verify the bug fix. |
| **`PASS_TO_PASS`** | Safety Criteria | Existing tests that must remain passing to ensure no regressions were introduced. |

---

## 2. Evaluation Difficulty Levels

In both levels, **`hints_text`** is strictly removed to ensure the agent relies on repository navigation and logic rather than developer commentary.

### **Level 1: Directed Test-Driven Development (TDD)**
**Focus:** *Constraint Satisfaction & Execution Logic*

* **Masking Configuration:**
    * `patch`: **REMOVED**
    * `test_patch`: **PROVIDED**
    * `hints_text`: **REMOVED**
* **The Planning Challenge:** The agent is given a specific validation script (`test_patch`). It must plan a trajectory to explore the codebase, locate the relevant files, and modify the code until the provided verification script passes.
* **Success Metric:** The agent satisfies the provided test constraints with minimal iterations.

### **Level 2: Autonomous Issue Resolution (Zero-Context)**
**Focus:** *Root Cause Analysis & Strategy Generation*

* **Masking Configuration:**
    * `patch`: **REMOVED**
    * `test_patch`: **REMOVED**
    * `hints_text`: **REMOVED**
* **The Planning Challenge:** The agent is given only the `problem_statement`. It must independently plan the following phases:
    1.  **Discovery:** Locate the bug within the repository structure.
    2.  **Reproduction:** Autonomously write its own `test_patch` to prove the bug exists.
    3.  **Remediation:** Plan and execute a code fix (`patch`).
    4.  **Verification:** Validate the fix against its own self-generated tests.
* **Success Metric:** The agent's final generated patch matches the functional intent of the "Gold Patch" and passes the (hidden) verification suite.

---

## 3. Data Schema for Evaluation Harness

When preparing your evaluation JSON/CSV, use the following logic to strip the data:

| Level | Input provided to Agent | Hidden (Target) |
| :--- | :--- | :--- |
| **Tier 1** | `problem_statement`, `test_patch` | `patch` |
| **Tier 2** | `problem_statement` | `patch`, `test_patch` |

```python
# Pseudo-code for Tier 2 evaluation
def run_autonomous_eval(instance):
    # Strip all context except the issue
    goal = instance['problem_statement']
    
    # Agent must now plan: 
    # 1. repo_search() -> 2. create_repro_test() -> 3. apply_fix()
    result_patch = planning_agent.resolve(goal)
    
    return verify_with_gold_standard(result_patch, instance['test_patch'])
