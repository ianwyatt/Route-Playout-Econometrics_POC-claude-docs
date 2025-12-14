# Troubleshooting Documentation

This folder contains critical troubleshooting guides for operational issues encountered during development and deployment.

## Contents

### [POSTGRESQL_PARALLEL_WORKER_DEADLOCK_FIX.md](./POSTGRESQL_PARALLEL_WORKER_DEADLOCK_FIX.md)
**Issue**: PostgreSQL parallel workers deadlocking during materialized view creation
**Impact**: Migration 003 hanging indefinitely (6+ minutes)
**Solution**: Disable parallel workers for migration session
**When to Reference**:
- Running migration 003 to create/refresh mv_campaign_browser
- Any complex materialized view creation that hangs
- PostgreSQL queries spawning multiple stuck workers

---

## How to Use This Folder

When encountering an issue:
1. Check if there's a matching troubleshooting guide here
2. Follow the documented solution steps
3. Reference the monitoring/debugging commands provided
4. If you encounter a new critical issue, document it here

## Documentation Standards

Each troubleshooting document should include:
- **Issue Summary**: Clear description of the problem
- **Symptoms**: Observable behavior and error messages
- **Root Cause**: Technical explanation of why it happens
- **Solution**: Step-by-step fix with commands/code
- **Verification**: How to confirm the issue is resolved
- **Prevention**: How to avoid the issue in the future
- **Related Issues**: Links to similar problems or related documentation

---

**Folder Created**: November 15, 2025
**Purpose**: Quick reference for critical operational issues
