# Version 0.3.0 Release Countdown

This document tracks all issues that must be resolved before releasing version 0.3.0. Each item is actionable and can be assigned to team members.

**Current Status:** Version bumped to 0.3.0 in pyproject.toml, multiple critical issues identified

---

## 🔴 CRITICAL - Must Fix Before Release

### C1. Version String Mismatch
**File:** `src/slurm/__init__.py` line 7
**Issue:** `__version__ = "0.1.0"` but pyproject.toml has `version = "0.3.0"`
**Impact:** Package reports wrong version at runtime

**Fix:**
```python
# Change line 7 from:
__version__ = "0.1.0"
# To:
__version__ = "0.3.0"
```

**Assignee:** _________
**Estimate:** 5 minutes

---

### C2. Broken Public API Exports in runtime.py
**File:** `src/slurm/runtime.py` lines 372-378
**Issue:** `__all__` exports `"function_wants_job_context"` and `"bind_job_context"` but actual functions are named `_function_wants_job_context` and `_bind_job_context` (private)
**Impact:** ImportError when users try to import these "public" functions

**Fix Option 1 (Recommended):** Remove from public API
```python
# Line 372-378, change to:
__all__ = [
    "JobContext",
    "build_job_context",
    "current_job_context",
    # Removed - these are internal:
    # "function_wants_job_context",
    # "bind_job_context",
]
```

**Fix Option 2:** Make truly public by renaming functions
```python
# Lines 240 and 251, remove underscore prefix:
def function_wants_job_context(func: Callable[..., Any]) -> bool:
    ...

def bind_job_context(...):
    ...
```

**Decision Required:** Should these be public or private?
**Assignee:** _________
**Estimate:** 30 minutes (including decision + tests)

---

### C3. Missing Public API Exports
**File:** `src/slurm/__init__.py` lines 22-34
**Issue:** Callbacks and error types are not exposed in main `__all__`, users cannot import them
**Impact:** Users must use internal import paths like `from slurm.callbacks import BaseCallback`

**Fix:**
```python
# Add to imports (after line 20):
from .callbacks import BaseCallback, LoggerCallback, BenchmarkCallback
from .errors import (
    SubmissionError,
    DownloadError,
    BackendError,
    BackendTimeout,
    BackendCommandError,
    PackagingError,
    SlurmfileError,
)

# Add to __all__ (after line 33):
__all__ = [
    # ... existing exports ...
    # Callbacks
    "BaseCallback",
    "LoggerCallback",
    "BenchmarkCallback",
    # Errors
    "SubmissionError",
    "DownloadError",
    "BackendError",
    "BackendTimeout",
    "BackendCommandError",
    "PackagingError",
    "SlurmfileError",
]
```

**Assignee:** _________
**Estimate:** 20 minutes

---

## 🟠 HIGH - Fix Before Release

### H1. Bare Exception Handlers in SSH Backend
**File:** `src/slurm/api/ssh.py` lines 593, 600, 605 (and possibly more)
**Issue:** Uses bare `except:` which catches ALL exceptions including SystemExit and KeyboardInterrupt
**Impact:** Makes debugging impossible, can hide critical errors

**Fix:** Replace all bare `except:` with specific exception types
```python
# BEFORE:
try:
    sftp.close()
except:
    pass

# AFTER:
try:
    sftp.close()
except (IOError, OSError, paramiko.SSHException) as e:
    logger.debug(f"Error closing SFTP connection: {e}")
```

**Action Items:**
1. Find all bare `except:` in ssh.py: `grep -n "except:" src/slurm/api/ssh.py`
2. Replace each with specific exception types
3. Add logging instead of silent `pass`

**Assignee:** _________
**Estimate:** 2 hours

---

### H2. Silent Callback Failures
**File:** `src/slurm/runner.py` lines 396, 721, 787, 829
**Issue:** Callback exceptions are caught and silently ignored with `except Exception: pass`
**Impact:** Users don't know their callbacks are failing

**Fix:** Add logging to exception handlers
```python
# BEFORE:
try:
    callback.on_submit_begin(context)
except Exception:
    pass

# AFTER:
try:
    callback.on_submit_begin(context)
except Exception as e:
    logger.warning(f"Callback {callback.__class__.__name__}.on_submit_begin failed: {e}")
```

**Action Items:**
1. Find all silent callback handlers
2. Add warning-level logging for failures
3. Consider: Should callback failures be fatal or just logged?

**Assignee:** _________
**Estimate:** 1 hour

---

### H3. Missing Type Hints in Public Methods
**File:** `src/slurm/task.py` line 224
**Issue:** `items: list` is too generic, should be `items: List[Any]`
**Impact:** Type checkers can't provide proper hints

**Fix:**
```python
# Line 224, change from:
def map(self, items: list, max_concurrent: Optional[int] = None):

# To:
def map(self, items: List[Any], max_concurrent: Optional[int] = None):

# Also add import at top if not present:
from typing import Any, List, Optional
```

**Assignee:** _________
**Estimate:** 10 minutes

---

### H4. Overly Permissive Type Annotation
**File:** `src/slurm/rendering.py` line 101
**Issue:** `cluster: Any = None` should be `Optional["Cluster"]`
**Impact:** Type safety compromised

**Fix:**
```python
# Line 101, change from:
cluster: Any = None,

# To:
cluster: Optional["Cluster"] = None,

# Add to imports if needed:
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .cluster import Cluster
```

**Assignee:** _________
**Estimate:** 15 minutes

---

## 🟡 MEDIUM - Should Fix Before Release

### M1. Inconsistent Error Handling Strategy
**Files:** `src/slurm/job.py`, `src/slurm/api/ssh.py`, `src/slurm/api/local.py`
**Issue:** Some methods return error dicts, others raise exceptions
**Impact:** API is unpredictable

**Examples:**
- `job.py` line 217: Returns `{"JobState": "UNKNOWN", "Error": str(e)}`
- `ssh.py` raises `BackendCommandError`
- `local.py` raises `BackendCommandError`

**Decision Required:**
- Should error handling be exception-based or return-value-based?
- Document the decision in CONTRIBUTING.md

**Assignee:** _________
**Estimate:** 4 hours (including refactoring)

---

### M2. Missing Input Validation in Public Methods
**Issue:** Public methods don't validate inputs
**Impact:** Unhelpful error messages when invalid inputs are provided

**Specific Cases:**

#### M2a. Cluster.__init__() - No backend validation
**File:** `src/slurm/cluster.py` line 209-250
**Fix:** Validate backend_type before creating backend
```python
def __init__(self, ...):
    if backend_type not in ["ssh", "local"]:
        raise ValueError(f"Invalid backend_type: {backend_type}. Must be 'ssh' or 'local'")
    # ... rest of init
```

#### M2b. SlurmTask.__init__() - No callable check
**File:** `src/slurm/task.py` line 91-114
**Fix:** Validate func is callable
```python
def __init__(self, func, ...):
    if not callable(func):
        raise TypeError(f"func must be callable, got {type(func)}")
    # ... rest of init
```

#### M2c. Job.__init__() - No ID validation
**File:** `src/slurm/job.py` line 75-132
**Fix:** Validate job ID is non-empty
```python
def __init__(self, id: str, ...):
    if not id or not id.strip():
        raise ValueError("job id must be a non-empty string")
    # ... rest of init
```

**Assignee:** _________
**Estimate:** 2 hours total

---

### M3. Bare Exception Handlers in runner.py and cluster.py
**Files:** `src/slurm/runner.py`, `src/slurm/cluster.py`
**Issue:** Multiple `except Exception: pass` blocks swallow errors
**Impact:** Similar to H1 and H2

**Fix:** Replace with specific exception types and add logging

**Assignee:** _________
**Estimate:** 2 hours

---

### M4. API Stability Documentation
**File:** Create `docs/api_stability.md`
**Issue:** No documentation on which APIs are stable vs experimental
**Impact:** Users don't know what's safe to depend on

**Fix:** Create stability tiers document:
```markdown
# API Stability Tiers

## Stable APIs (0.x compatible)
- `@task` decorator
- `@workflow` decorator
- `Cluster.submit()`
- `Job.wait()`, `Job.get_result()`, `Job.is_successful()`
- `WorkflowContext` methods

## Experimental APIs (may change)
- Callback system
- Container packaging
- `InheritPackagingStrategy`

## Internal APIs (not for public use)
- `runner.py` module
- `_*` prefixed functions/classes
```

**Assignee:** _________
**Estimate:** 1 hour

---

## 🟢 LOW - Nice to Have

### L1. Remove Confusing os Alias
**File:** `src/slurm/cluster.py` line 636
**Issue:** Uses `import os as _os` to avoid collision
**Impact:** Code readability

**Fix:** Refactor to avoid the need for aliasing
```python
# Instead of:
import os as _os
_os.path.exists(...)

# Use direct imports:
from os.path import exists
exists(...)
```

**Assignee:** _________
**Estimate:** 30 minutes

---

### L2. Add Docstrings to Undocumented Methods
**Issue:** Some public methods lack docstrings
**Impact:** Poor IDE autocomplete experience

**Action:** Audit all public methods and add Google-style docstrings

**Assignee:** _________
**Estimate:** 4 hours

---

### L3. Test Coverage for New Features
**Issue:** Need tests for InheritPackagingStrategy edge cases

**Test Cases Needed:**
1. Parent workflow using venv, child inherits
2. Parent workflow using container, child inherits
3. Invalid metadata file handling
4. Metadata file missing
5. Cross-backend inheritance (should fail gracefully)

**Assignee:** _________
**Estimate:** 3 hours

---

## 📋 Pre-Release Checklist

Before tagging v0.3.0, verify:

- [ ] **C1-C3**: All critical issues fixed
- [ ] **H1-H4**: All high-priority issues fixed
- [ ] Version string updated in `__init__.py`
- [ ] All integration tests pass
- [ ] Unit test coverage > 80%
- [ ] Documentation updated:
  - [ ] CHANGELOG.md updated with v0.3.0 changes
  - [ ] README.md examples still work
  - [ ] API reference docs generated
- [ ] Manual testing:
  - [ ] Workflow with callbacks works end-to-end
  - [ ] InheritPackagingStrategy works with venv
  - [ ] InheritPackagingStrategy works with containers
  - [ ] SSH backend works with real cluster
  - [ ] Local backend works for development
- [ ] No bare `except:` handlers remain in codebase
- [ ] All `__all__` exports are valid
- [ ] Breaking changes documented in CHANGELOG.md

---

## 🎯 Priority Summary

| Priority | Count | Total Estimate |
|----------|-------|----------------|
| CRITICAL | 3     | ~1 hour        |
| HIGH     | 4     | ~4 hours       |
| MEDIUM   | 4     | ~9 hours       |
| LOW      | 3     | ~7.5 hours     |
| **TOTAL**| **14**| **~21.5 hours**|

---

## 📝 Notes

### Version Numbering Strategy
Current: `0.3.0`
- Major version 0 = Pre-1.0, breaking changes allowed
- Minor version 3 = Feature releases (workflows, callbacks, inherit packaging)
- Patch version 0 = Bug fixes

### Breaking Changes in 0.3.0
1. Added workflow support (new feature, not breaking)
2. Added callback system (new feature, not breaking)
3. Added InheritPackagingStrategy (new feature, not breaking)
4. Fixed resource limits in tests (internal, not breaking)

### Future Considerations (0.4.0+)
- [ ] Add type stubs (.pyi files) for better IDE support
- [ ] GraphQL/REST API for cluster management
- [ ] Workflow visualization UI
- [ ] Advanced dependency graphs (DAG support)
- [ ] Checkpoint/resume for long workflows
- [ ] Workflow templates and reusable components

---

## 🔗 Related Documents
- `CHANGELOG.md` - Release notes
- `CONTRIBUTING.md` - Development guidelines (create if missing)
- `docs/api_stability.md` - API stability guarantees (create as M4)

---

**Last Updated:** 2025-10-22
**Release Target:** TBD (after all CRITICAL + HIGH issues resolved)
