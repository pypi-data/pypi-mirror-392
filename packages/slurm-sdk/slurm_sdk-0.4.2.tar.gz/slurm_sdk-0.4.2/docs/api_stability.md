# API Stability Guide

This document defines the stability guarantees for different parts of the slurm-sdk API.

## Overview

The slurm-sdk follows semantic versioning (SemVer). This means:
- **Patch releases** (0.3.X): Bug fixes only, no API changes
- **Minor releases** (0.X.0): New features, backward compatible
- **Major releases** (X.0.0): Breaking changes allowed

Since we're in version 0.x, the API is still evolving. We provide stability tiers to help you understand which parts are safe to depend on.

---

## Stability Tiers

### ⭐ Stable APIs (Safe to Use)

These APIs are considered stable within the 0.x series and won't change without deprecation warnings:

#### Core Decorators
```python
from slurm import task, workflow

@task(time="00:10:00", cpus_per_task=4)
def my_task(x: int) -> int:
    return x * 2

@workflow(time="00:30:00")
def my_workflow(value: int, ctx: WorkflowContext):
    job = my_task(value)
    return job.get_result()
```

#### Cluster Management
```python
from slurm import Cluster

# Creating a cluster
cluster = Cluster(
    backend_type="ssh",
    hostname="slurm.example.com",
    username="user"
)

# Loading from Slurmfile
cluster = Cluster.from_env("Slurmfile.toml", env="production")

# Submitting jobs
job = cluster.submit(my_task)(42)
```

#### Job Operations
```python
# All Job methods are stable
job.wait(timeout=300)
job.is_successful()
job.is_running()
job.is_pending()
job.get_status()
job.get_result()
job.cancel()
```

#### Workflow Context
```python
from slurm.workflow import WorkflowContext

# All WorkflowContext methods are stable
@workflow(time="00:30:00")
def my_workflow(ctx: WorkflowContext):
    job = ctx.submit(my_task)(42)  # Submit child task
    result = job.get_result()
    return result
```

#### Array Jobs
```python
# Array job API is stable
from slurm import task

@task(time="00:05:00")
def process_item(x: int) -> int:
    return x * 2

# Map over items
array_job = cluster.submit(process_item).map([1, 2, 3, 4, 5])
results = array_job.get_results()
```

#### Job Context (Runtime)
```python
from slurm import JobContext

@task(time="00:10:00")
def my_task(x: int, ctx: JobContext) -> dict:
    return {
        "result": x * 2,
        "job_id": ctx.job_id,
        "cpus": ctx.cpus_per_task
    }
```

#### Error Types
All error types in `slurm.errors` are stable:
```python
from slurm import (
    SubmissionError,
    DownloadError,
    BackendError,
    BackendTimeout,
    BackendCommandError,
    PackagingError,
    SlurmfileError,
)
```

---

### 🧪 Experimental APIs (May Change)

These APIs are functional but may change in minor releases (0.X.0):

#### Callback System
The callback system is experimental and the API may evolve:

```python
from slurm.callbacks import BaseCallback, LoggerCallback, BenchmarkCallback

# Basic usage is stable, but callback signatures may change
cluster = Cluster(
    backend_type="ssh",
    hostname="example.com",
    callbacks=[LoggerCallback(), BenchmarkCallback()]
)
```

**Why experimental?**
- Callback method signatures may gain new parameters
- New callback types may be added
- Event timing and guarantees may change

**Migration path:** We'll provide adapters if breaking changes are needed.

#### Container Packaging
Container packaging support is experimental:

```python
# API may change
@task(
    time="00:10:00",
    packaging={
        "type": "container",
        "image": "my-image:latest",
        "python_executable": "python3"
    }
)
def my_task():
    pass
```

**Why experimental?**
- Integration with different container runtimes (Singularity, Enroot, Podman) may require API changes
- Multi-word executables support is new

#### Environment Inheritance
The `InheritPackagingStrategy` is experimental:

```python
# API may change
@task(time="00:05:00", packaging={"type": "inherit"})
def child_task():
    pass
```

**Why experimental?**
- Metadata format may evolve
- Cross-backend inheritance behavior being refined

---

### 🔒 Internal APIs (Do Not Use)

These APIs are for internal use only and may change without notice:

#### Private Modules
- `slurm.runner` - Internal job execution script
- `slurm.rendering` - Job script generation
- `slurm.config` - Slurmfile parsing
- `slurm.api.*` - Backend implementations

#### Private Functions/Classes
Any symbol starting with `_` is private:
```python
from slurm.cluster import _JobStatusPoller  # ❌ Internal, do not use
from slurm.runtime import _bind_job_context  # ❌ Internal, do not use
```

#### Backend Implementations
Direct use of backend classes is discouraged:
```python
from slurm.api.ssh import SSHCommandBackend  # ❌ Use Cluster instead
```

**Instead, use:**
```python
from slurm import Cluster

cluster = Cluster(backend_type="ssh", ...)  # ✅ Public API
```

---

## Packaging Configuration

### Stable Packaging Types
```python
# Wheel packaging (stable)
@task(packaging={"type": "wheel", "build_tool": "uv"})
def my_task():
    pass

# No packaging (stable)
@task(packaging={"type": "none"})
def my_task():
    pass
```

### Experimental Packaging Types
```python
# Container packaging (experimental)
@task(packaging={"type": "container", "image": "my-image:latest"})
def my_task():
    pass

# Inherit packaging (experimental)
@task(packaging={"type": "inherit"})
def child_task():
    pass
```

---

## Slurmfile Configuration

The Slurmfile format is **stable** for basic configuration:

```toml
[production.cluster]
backend = "ssh"
job_base_dir = "/scratch/jobs"

[production.cluster.backend_config]
hostname = "slurm.example.com"
username = "myuser"

[production.packaging]
type = "wheel"
python_executable = "/usr/bin/python3.11"

[production.submit]
partition = "compute"
```

**Experimental Slurmfile features:**
- Container-specific configuration
- Advanced packaging options

---

## Deprecation Policy

### How We Deprecate

1. **Deprecation Warning** (Minor Release)
   - Feature marked as deprecated in documentation
   - Runtime warnings added (where possible)
   - Alternative API provided

2. **Grace Period** (1-2 Minor Releases)
   - Deprecated feature continues to work
   - Migration guide provided

3. **Removal** (Next Major Release)
   - Deprecated feature removed
   - Clear error messages guide users to alternatives

### Example Deprecation Flow

```
v0.3.0: Feature X added
v0.4.0: Feature X deprecated, Feature Y recommended
        DeprecationWarning shown when using Feature X
v0.5.0: Feature X still works, warnings continue
v1.0.0: Feature X removed, only Feature Y works
```

---

## Version Compatibility

### Python Version Support
- **Minimum**: Python 3.9
- **Recommended**: Python 3.11+
- **Tested**: Python 3.9, 3.10, 3.11, 3.12

### Slurm Version Support
- **Minimum**: Slurm 20.x
- **Recommended**: Slurm 22.x or newer
- **Tested**: Slurm 22.05, 23.02

---

## Migration Guidelines

### When We Break Things

If a breaking change is necessary, we will:

1. **Announce** in CHANGELOG.md and GitHub Releases
2. **Provide** a migration guide with code examples
3. **Offer** deprecation period (when possible)
4. **Document** all changes clearly

### Staying Updated

To minimize migration pain:

1. **Pin versions** in production:
   ```toml
   dependencies = ["slurm-sdk==0.3.0"]  # Exact version
   ```

2. **Test before upgrading**:
   ```bash
   # Test in development first
   pip install slurm-sdk==0.4.0
   pytest tests/
   ```

3. **Read CHANGELOG.md** before each upgrade

4. **Watch for DeprecationWarnings** in your code

---

## Future Stable APIs (Planned)

These features are coming and will be stable when released:

### Planned for v0.4.0
- Advanced dependency DAGs
- Checkpoint/resume for workflows
- Workflow visualization tools

### Planned for v1.0.0
- Full callback system stability
- Container packaging stabilization
- GraphQL/REST API for cluster management

---

## Questions?

- **Found a bug?** [Report it on GitHub](https://github.com/your-org/slurm-sdk/issues)
- **Need a feature?** [Request it on GitHub](https://github.com/your-org/slurm-sdk/issues)
- **Have questions?** Check the [documentation](https://docs.slurm-sdk.example.com)

---

## Summary Table

| API Category | Stability | Safe to Use? | Change Policy |
|-------------|-----------|--------------|---------------|
| Core decorators (@task, @workflow) | ⭐ Stable | ✅ Yes | Deprecation required |
| Cluster management | ⭐ Stable | ✅ Yes | Deprecation required |
| Job operations | ⭐ Stable | ✅ Yes | Deprecation required |
| Error types | ⭐ Stable | ✅ Yes | Deprecation required |
| Callback system | 🧪 Experimental | ⚠️ Cautiously | May change in minor releases |
| Container packaging | 🧪 Experimental | ⚠️ Cautiously | May change in minor releases |
| Inherit packaging | 🧪 Experimental | ⚠️ Cautiously | May change in minor releases |
| Private APIs (_*) | 🔒 Internal | ❌ No | Can change anytime |
| Backend implementations | 🔒 Internal | ❌ No | Can change anytime |

---

Last updated: 2025-10-22
Version: 0.3.0
