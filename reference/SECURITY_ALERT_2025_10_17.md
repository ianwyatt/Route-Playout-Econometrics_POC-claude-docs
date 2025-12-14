# SECURITY ALERT - October 17, 2025

## ⚠️ CRITICAL: API Keys Exposed in Git History

**Severity**: HIGH
**Date Discovered**: 2025-10-17
**Status**: REQUIRES IMMEDIATE ACTION

---

## What Happened

The file `.env.production` was committed to git with **REAL API keys** on **August 6, 2025** (commit `de8d7f1`).

This file has been in the public git history for **over 2 months**.

---

## Exposed Credentials

The following MediaTel API keys were exposed:

1. **Production API Key**: `c0d492a0-8917-4cd1-ab13-a614ebc04e44`
   - URL: `https://route.mediatelapi.co.uk`

2. **UAT API Key**: `e634425e-a7c6-4812-a093-936d5ec77189`
   - URL: `https://uat-routeapi.mediatel.co.uk`

3. **Dev API Key**: `cd62fc2e-4d6b-4697-acd2-7172cf69cb12`
   - URL: `https://route-uat.mediatelapi.co.uk:8443`

---

## Risk Assessment

**Likelihood of Compromise**: HIGH

- Keys have been in git history for 2+ months
- Repository may have been cloned/forked
- GitHub history is public if repo is public
- Automated scrapers constantly scan for exposed credentials

**Potential Impact**:
- Unauthorized API access
- Data exfiltration
- API quota exhaustion
- Service disruption
- Financial impact if APIs are metered

---

## Immediate Actions Required

### 1. Rotate ALL Three API Keys (URGENT)

**Contact MediaTel immediately:**
- Request revocation of all three exposed keys
- Generate new production, UAT, and dev keys
- Update local `.env` file with new keys

**Do NOT delay** - assume keys are already compromised.

### 2. Check API Usage Logs

Review MediaTel API logs for:
- Unusual access patterns since August 6, 2025
- Unexpected geographic locations
- High volume requests
- Failed authentication attempts with these keys

### 3. Verify Repository Access

Check GitHub/GitLab repository:
- Is the repo public or private?
- Who has access?
- Check access logs for unauthorized clones
- Review fork history

### 4. Notify Stakeholders

If APIs have been abused:
- Notify your security team
- Inform MediaTel of potential breach
- Document incident timeline

---

## What We Fixed

### Git Cleanup
✅ Removed `.env.production` from git tracking (commit `4301e7e`)
✅ Updated `.gitignore` to block ALL `.env.*` files
✅ Preserved safe templates (`.env.example`, `.env.template`)

### Prevention Measures
✅ Enhanced pre-commit hook checks for API keys
✅ Added `.env.*` pattern to .gitignore
✅ Claude/ directory blocked from commits (internal docs stay local)

---

## Git History Note

⚠️ **The exposed keys are STILL in git history** (commit `de8d7f1`)

While we've removed the file from tracking, the keys remain in historical commits.

**Why we didn't rewrite history:**
- Destructive operation requiring force push
- May break clones/forks
- Keys already exposed for 2 months
- Better to rotate keys than rewrite history

**Key rotation is the ONLY safe solution.**

---

## How This Happened

**Root Cause**: `.env.production` in project root wasn't covered by `.gitignore`

**Previous .gitignore had**:
- `.env` (blocked root .env)
- `config/.env.production` (blocked config folder)
- But NOT `.env.production` in root

**Why the hook didn't catch it**:
- Pre-commit hook scans staged files
- May not have been in place on August 6, 2025
- Or pattern didn't match UUID format

---

## Prevention Checklist

✅ `.gitignore` now blocks `.env.*` (all env files)
✅ Pre-commit hook scans for API keys/secrets
✅ Templates allowed with explicit exceptions
✅ Claude/ directory blocked from commits
✅ Deployment configs blocked from commits

**Future**: Never commit files with pattern `.env.*` unless it's a template.

---

## Timeline

- **2025-08-06**: `.env.production` committed with real keys (commit `de8d7f1`)
- **2025-10-17**: Exposure discovered during project cleanup
- **2025-10-17**: File removed from git, .gitignore updated (commit `4301e7e`)
- **2025-10-17**: Security alert created (this document)

**Duration of Exposure**: 72 days

---

## Action Checklist

- [ ] Contact MediaTel to rotate ALL three API keys
- [ ] Review API access logs since August 6, 2025
- [ ] Update local `.env` with new keys
- [ ] Verify repository access/permissions
- [ ] Check for unusual API usage/charges
- [ ] Notify security team if required
- [ ] Document incident response
- [ ] Update team security training

---

## Contact Information

**MediaTel Support**:
- Email: [support contact needed]
- Phone: [support phone needed]
- Portal: [API management portal URL]

**Internal Security**:
- Escalate to: [your security team contact]
- Incident reporting: [incident process]

---

## Lessons Learned

1. **Never commit .env.* files** with real credentials
2. **Always use templates** for example configs
3. **Pre-commit hooks** are defense in depth, not foolproof
4. **Regular security audits** catch issues early
5. **Key rotation policies** limit exposure window

---

## References

- Commit with exposed keys: `de8d7f1`
- Security fix commit: `4301e7e`
- .gitignore update: commit `4301e7e`
- This alert: `Claude/SECURITY_ALERT_2025_10_17.md` (local only)

---

**Status**: AWAITING KEY ROTATION

**Next Review**: After new keys are generated and deployed

---

*This document is confidential and should not be committed to git.*
