# Security Policy for HVT6

**Version**: 6.2.0
**Last Updated**: 2025-11-05
**Status**: Active

---

## Table of Contents

1. [Overview](#overview)
2. [Credential Security](#credential-security)
3. [Git History Exposure](#git-history-exposure)
4. [Password Rotation Guide](#password-rotation-guide)
5. [Git History Cleanup](#git-history-cleanup)
6. [Best Practices](#best-practices)
7. [Reporting Security Issues](#reporting-security-issues)
8. [Security Roadmap](#security-roadmap)

---

## Overview

HVT6 (Hardening Verification Tool v6) is a security auditing tool that requires device credentials to collect configurations from Cisco IOS/IOS-XE devices. This document outlines security best practices, credential management, and remediation steps for exposed credentials.

### Key Security Principles

- **Principle of Least Privilege**: Use read-only accounts when possible
- **Defense in Depth**: Multiple layers of credential protection
- **Secure by Default**: .env file never committed to version control
- **Transparency**: Clear logging of credential sources
- **Forward Compatibility**: Architecture prepared for HashiCorp Vault integration (v7.0+)

---

## Credential Security

### Current Implementation (v6.2+)

**Credential Storage Priority:**

1. **Environment Variables (.env)** ← PRIMARY (RECOMMENDED)
2. **YAML Inventory Files** ← LEGACY (DEPRECATED, removed in v7.0)
3. **Interactive Prompts** ← FALLBACK (manual use only)

**Security Measures:**

✅ **Environment Variables**: Credentials stored in `.env` file (excluded from Git)
✅ **File Permissions**: `.env` should be `chmod 600` (read/write owner only)
✅ **No Plaintext in Code**: All credential handling through abstraction layer
✅ **Validation Warnings**: Alerts if credentials missing or loaded from deprecated source
✅ **Read-Only Operations**: Collector only executes `show` commands

### Migrating from YAML to .env

**If you used HVT6 v6.0-6.1**, credentials were stored in `inventory/defaults.yaml` in plaintext. **These credentials are exposed in Git history**.

**Immediate Actions Required:**

1. ✅ **Migrate to .env** (see README.md - Configuración de Seguridad)
2. ⚠️ **Rotate passwords** (see Password Rotation Guide below)
3. 🧹 **Clean Git history** (optional, see Git History Cleanup below)

---

## Git History Exposure

### Problem Description

**Versions Affected**: HVT6 v6.0.0 - v6.1.0 (October 2025)

Prior to v6.2, `inventory/defaults.yaml` contained plaintext credentials:

```yaml
username: admin
password: BvsTv3965!  # ⚠️ EXPOSED IN GIT HISTORY
secret: BvsTv3965!    # ⚠️ EXPOSED IN GIT HISTORY
```

**Impact:**

- ⚠️ **HIGH**: Credentials committed to Git repository
- ⚠️ **MEDIUM**: Exposed in all historical commits
- ⚠️ **LOW**: If repository is private and access controlled

**Affected Commits:**

You can search your Git history for exposed credentials:

```bash
# Search for password keyword
git log --all --full-history --source --pickaxe-all -S 'password'

# Search specific file history
git log --all --full-history -- inventory/defaults.yaml

# View specific commit
git show <commit-hash>:inventory/defaults.yaml
```

### Risk Assessment Matrix

| Repository Status | Access Level | Risk Level | Action Required |
|-------------------|-------------|------------|-----------------|
| Public GitHub | Anyone | 🔴 **CRITICAL** | Rotate passwords IMMEDIATELY + Clean history |
| Private GitHub | Team only | 🟡 **HIGH** | Rotate passwords within 24h + Consider cleanup |
| Local only | You only | 🟢 **MEDIUM** | Rotate passwords + Update .env |
| Air-gapped | Isolated | 🟢 **LOW** | Update to .env for future security |

---

## Password Rotation Guide

### Prerequisites

- Access to all devices configured in HVT6
- Administrative privileges to change passwords
- List of affected devices: `grep 'hostname' inventory/hosts.yaml`

### Step-by-Step Rotation

#### Step 1: Prepare New Credentials

```bash
# Generate strong passwords (example using pwgen)
sudo apt install pwgen
pwgen -s -y -n 16 1  # Secure, symbols, numbers, 16 chars

# Or use Python
python3 -c "import secrets, string; chars = string.ascii_letters + string.digits + string.punctuation; print(''.join(secrets.choice(chars) for _ in range(16)))"
```

**Requirements:**
- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- Not based on dictionary words
- Different from previous passwords

#### Step 2: Update Device Passwords

**For each device:**

```cisco
! Connect to device
ssh admin@device-hostname

! Enter enable mode
enable

! Enter configuration mode
configure terminal

! Change local username password
username admin privilege 15 secret YourNewSecurePassword123!

! If using enable secret
enable secret YourNewSecurePassword123!

! Save configuration
write memory
! or
copy running-config startup-config

! Exit
exit
```

**Important Notes:**
- Test new credentials on one device first
- Keep console access available during changes
- Document the change in your change management system
- Verify AAA configuration if using TACACS+/RADIUS

#### Step 3: Update .env File

```bash
# Edit .env with new credentials
nano .env

# Update these lines:
DEVICE_USERNAME=admin
DEVICE_PASSWORD=YourNewSecurePassword123!
DEVICE_SECRET=YourNewSecurePassword123!
```

#### Step 4: Test New Credentials

```bash
# Test collection with new credentials
python collect.py --host device-name --verbose

# Verify in logs:
tail -f config_analyzer.log | grep -i "credential"

# Expected output:
# ✓ username: loaded from Environment Variables (.env)
# ✓ password: loaded from Environment Variables (.env)
```

#### Step 5: Verify Access to All Devices

```bash
# Test SSH access
for device in device1 device2 device3; do
  echo "Testing $device..."
  ssh -o ConnectTimeout=5 $DEVICE_USERNAME@$device "show clock"
  if [ $? -eq 0 ]; then
    echo "✓ $device: OK"
  else
    echo "✗ $device: FAILED"
  fi
done
```

#### Step 6: Update Documentation

- [ ] Update password vault/manager (LastPass, 1Password, etc.)
- [ ] Notify team members of credential change
- [ ] Update any automation scripts using old credentials
- [ ] Update CI/CD secrets (GitHub Actions, GitLab CI, etc.)
- [ ] Document rotation date in password management system

### Bulk Rotation Script (Advanced)

For large deployments, consider automating rotation:

```python
# rotate_passwords.py
from netmiko import ConnectHandler
import csv

devices_csv = 'devices.csv'  # hostname, ip, old_password
new_password = 'YourNewSecurePassword123!'

with open(devices_csv) as f:
    reader = csv.DictReader(f)
    for row in reader:
        device = {
            'device_type': 'cisco_ios',
            'host': row['ip'],
            'username': 'admin',
            'password': row['old_password'],
            'secret': row['old_password']
        }

        try:
            connection = ConnectHandler(**device)
            connection.enable()

            commands = [
                'configure terminal',
                f'username admin privilege 15 secret {new_password}',
                f'enable secret {new_password}',
                'end',
                'write memory'
            ]

            output = connection.send_config_set(commands)
            print(f"✓ {row['hostname']}: Password updated")
            connection.disconnect()

        except Exception as e:
            print(f"✗ {row['hostname']}: FAILED - {e}")
```

**⚠️ WARNING**: Test thoroughly before running in production. Always maintain out-of-band access (console) during bulk changes.

---

## Git History Cleanup

### Option 1: BFG Repo-Cleaner (Recommended)

**BFG** is faster and simpler than `git filter-branch` for removing sensitive data.

#### Installation

```bash
# macOS
brew install bfg

# Debian/Ubuntu
sudo apt install bfg

# Or download manually
wget https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar
alias bfg='java -jar bfg-1.14.0.jar'
```

#### Cleanup Steps

```bash
# 1. Clone a fresh copy (don't use your working repository)
git clone --mirror git@github.com:yourorg/ios-xe_hardening.git
cd ios-xe_hardening.git

# 2. Create a file with passwords to remove
cat > passwords.txt <<EOF
BvsTv3965!
admin
secret
EOF

# 3. Run BFG to remove passwords from history
bfg --replace-text passwords.txt

# 4. Clean up repository
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Force push to remote (⚠️ DESTRUCTIVE - COORDINATE WITH TEAM)
git push --force

# 6. Clean up local clone
cd ..
rm -rf ios-xe_hardening.git
```

#### Team Coordination

**Before force-pushing:**

1. ✅ Notify entire team of upcoming history rewrite
2. ✅ Ask team to commit and push all pending changes
3. ✅ Schedule maintenance window
4. ✅ Create backup: `git clone --mirror` to external location

**After force-push:**

```bash
# Each team member must re-clone:
cd ~/projects
rm -rf ios-xe_hardening  # Delete old repository
git clone git@github.com:yourorg/ios-xe_hardening.git
cd ios-xe_hardening
```

**Alternative: Rebase existing clone (advanced)**

```bash
git fetch origin
git reset --hard origin/main  # Replace main with your branch
git clean -fdx
```

### Option 2: git filter-branch (Legacy Method)

**⚠️ Not recommended**: Use BFG instead. Included for completeness.

```bash
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch inventory/defaults.yaml" \
  --prune-empty --tag-name-filter cat -- --all

git push origin --force --all
git push origin --force --tags
```

### Option 3: Selective File History Rewrite

If you only want to clean specific commits:

```bash
# 1. Identify commits with sensitive data
git log --all --full-history -- inventory/defaults.yaml

# 2. Interactive rebase to specific commit
git rebase -i <commit-before-exposure>^

# 3. Mark commits to edit, then amend each:
git commit --amend  # Remove sensitive data
git rebase --continue

# 4. Force push
git push --force-with-lease  # Safer than --force
```

### Verification After Cleanup

```bash
# Search for exposed passwords (should return nothing)
git log --all --source --pickaxe-all -S 'BvsTv3965'
git log --all --source --pickaxe-all -S 'password:'

# Check current file doesn't contain secrets
git show HEAD:inventory/defaults.yaml | grep -i password

# Verify .env is never tracked
git log --all -- .env  # Should be empty
```

### GitHub Additional Steps

If using GitHub, also invalidate cached data:

1. Go to: `https://github.com/yourorg/ios-xe_hardening/settings`
2. Scroll to "Danger Zone"
3. Click "Temporarily disable repository"
4. Wait 5 minutes
5. Re-enable repository

This clears GitHub's cache of repository data.

---

## Best Practices

### Credential Management

#### ✅ DO:

- **Use .env for all credentials** (primary method as of v6.2)
- **Set file permissions**: `chmod 600 .env`
- **Use strong passwords**: 12+ chars, mixed case, numbers, symbols
- **Rotate regularly**: Quarterly or after team member changes
- **Use read-only accounts** when possible (level 1-7 privilege)
- **Separate credentials per environment** (dev/staging/prod)
- **Use service accounts**, not personal accounts
- **Enable MFA on devices** where supported
- **Document credential changes** in change management system

#### ❌ DON'T:

- **Commit .env to Git** (.gitignore protects this)
- **Share .env via email/chat**
- **Use default passwords** (admin/admin, cisco/cisco)
- **Reuse passwords** across devices or environments
- **Store credentials in code** or scripts
- **Use weak passwords** (< 12 chars, dictionary words)
- **Share privileged accounts** (use individual accounts + sudo/AAA)

### Access Control

#### Device Configuration

```cisco
! Use AAA for centralized authentication
aaa new-model
aaa authentication login default group tacacs+ local
aaa authorization exec default group tacacs+ local

! Create local read-only user for HVT6
username hvt6_readonly privilege 7 secret SecurePassword123!

! Privilege level 7 allows: show, ping, traceroute (read-only)
privilege exec level 7 show running-config
privilege exec level 7 show startup-config
```

#### SSH Hardening

```cisco
! SSH version 2 only
ip ssh version 2
ip ssh time-out 60
ip ssh authentication-retries 3

! Disable Telnet
no transport input telnet
transport input ssh

! Use ACL to restrict access
ip access-list standard SSH_ACCESS
 permit 10.1.1.0 0.0.0.255
 permit host 192.168.1.10
 deny any log

line vty 0 4
 transport input ssh
 access-class SSH_ACCESS in
```

### File Security

```bash
# Restrict .env file permissions
chmod 600 .env

# Verify no secrets in Git
git secrets --scan  # Install: brew install git-secrets

# Pre-commit hook to prevent .env commits
cat > .git/hooks/pre-commit <<'EOF'
#!/bin/bash
if git diff --cached --name-only | grep -q '.env$'; then
  echo "❌ ERROR: Attempting to commit .env file"
  echo "   Remove from staging: git reset HEAD .env"
  exit 1
fi
EOF
chmod +x .git/hooks/pre-commit
```

### CI/CD Integration

#### GitHub Actions

```yaml
# .github/workflows/audit.yml
name: Security Audit

on:
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Mondays at 2 AM

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run collection
        env:
          DEVICE_USERNAME: ${{ secrets.DEVICE_USERNAME }}
          DEVICE_PASSWORD: ${{ secrets.DEVICE_PASSWORD }}
          DEVICE_SECRET: ${{ secrets.DEVICE_SECRET }}
        run: python collect.py --all

      - name: Run audit
        run: python hvt6.py --customer "Automated Audit"

      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            reports/
            results/
```

**Secret Management in GitHub:**

1. Go to: `https://github.com/yourorg/repo/settings/secrets/actions`
2. Click "New repository secret"
3. Add: `DEVICE_USERNAME`, `DEVICE_PASSWORD`, `DEVICE_SECRET`
4. Secrets are encrypted and never exposed in logs

---

## Reporting Security Issues

### Vulnerability Disclosure

If you discover a security vulnerability in HVT6:

1. **DO NOT** open a public GitHub issue
2. Email: security@yourorg.com (replace with your contact)
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### Response Timeline

- **< 24 hours**: Acknowledgment of report
- **< 7 days**: Initial assessment and triage
- **< 30 days**: Fix or mitigation plan
- **< 90 days**: Public disclosure (coordinated)

### Hall of Fame

Contributors who responsibly disclose vulnerabilities:

- *No entries yet - be the first!*

---

## Security Roadmap

### Current (v6.2.0) - November 2025

- ✅ Environment variable credential storage
- ✅ Deprecation of YAML plaintext credentials
- ✅ Credential abstraction layer
- ✅ Priority-based credential loading
- ✅ Validation warnings

### Near-Term (v6.3.0) - Q1 2026

- 🎯 Per-device credential override (DEVICE_ROUTER1_PASSWORD)
- 🎯 Credential encryption at rest (encrypted .env)
- 🎯 Certificate-based SSH authentication
- 🎯 Audit logging of credential access

### Medium-Term (v7.0.0) - Q2 2026

- 🎯 HashiCorp Vault integration (primary credential source)
- 🎯 AWS Secrets Manager support
- 🎯 Azure Key Vault support
- 🎯 Complete removal of YAML credential support

### Long-Term (v8.0.0+) - 2027

- 🎯 OAuth/OIDC device authentication
- 🎯 Zero-trust architecture
- 🎯 Credential rotation automation
- 🎯 Session recording and audit trails

---

## References

- **HVT6 Documentation**: [README.md](README.md)
- **Credential Setup**: [README.md - Configuración de Seguridad](README.md#-configuración-de-seguridad-importante)
- **Collector Guide**: [collector/README.md](collector/README.md)
- **Architecture**: [CLAUDE.md](CLAUDE.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)

### External Resources

- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/sp800-63b.html)
- [OWASP Credential Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Credential_Storage_Cheat_Sheet.html)
- [Cisco IOS Security Best Practices](https://www.cisco.com/c/en/us/support/docs/ios-nx-os-software/ios-software-releases-122-mainline/13608-21.html)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [Git Secrets Tool](https://github.com/awslabs/git-secrets)

---

**Last Updated**: 2025-11-05
**Document Version**: 1.0.0
**Review Cycle**: Quarterly
**Next Review**: 2026-02-05
