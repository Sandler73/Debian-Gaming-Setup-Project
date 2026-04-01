# Security Policy

## Supported Versions

| Version | Supported          | Security Updates |
| ------- | ------------------ | ---------------- |
| 2.5.x   | :white_check_mark: | Yes (Current)    |
| 2.2.x-2.4.x | :white_check_mark: | Yes         |
| 2.0.x-2.1.x | :white_check_mark: | Yes         |
| 1.x.x   | :x:                | No (Legacy)      |

**Current Stable Version:** 3.5.0

---

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly.

### 🔍 What to Include

Please provide:
1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Potential impact** assessment
4. **Suggested fix** (if known)
5. **Your contact information** (for follow-up)

### 🔒 Responsible Disclosure

- **Do not** publicly disclose the vulnerability until we've addressed it
- We'll work with you to understand and resolve the issue
- We'll credit you in the security advisory (unless you prefer anonymity)
- We aim to provide a fix within 30 days

---

## Security Considerations

### ⚠️ Script Requires Root Access

This script requires `sudo` privileges to:
- Install system packages
- Modify system configurations
- Install GPU drivers
- Configure kernel parameters
- Add and manage APT repositories
- Write sysctl configuration files

**We recommend:**
- Review the script before running
- Use `--dry-run` mode first
- Use `--check-requirements` to validate your system ✨
- Check logs for suspicious activity
- Use `--rollback` if anything goes wrong ✨

### 📂 What the Script Accesses

**File System:**
- `/etc/apt/` - Repository configuration
- `/etc/sysctl.d/` - Kernel parameters
- `/etc/sudoers.d/` - CPU governor permissions
- `/tmp/` - Temporary download files (cleaned up after use)
- `~/.config/` - User configurations (MangoHud, vkBasalt)
- `~/.steam/` - Steam installation and GE-Proton
- `~/gaming_setup_logs/` - Operation logs, state files, rollback manifest
- `~/gaming_setup_backups/` - Pre-modification file backups

**Network Access:**
- Package repositories (APT)
- Flathub (for Flatpak apps)
- GitHub API (for GE-Proton downloads and self-update)
- WineHQ repository
- Waydroid repository (waydro.id)
- Official distribution repositories

**No External Data Collection:**
- Script does not phone home
- No analytics or tracking
- No personal data transmitted
- All operations are local
- User-Agent header identifies as `debian-gaming-setup` only

### 🛡️ Security Features

**v3.4.2 Security Hardening:** ✨

- ✅ **No `shell=True` subprocess calls** — All commands use list-form arguments, preventing shell injection. The debconf EULA pipe uses `subprocess.run(input=)` instead of shell echo-pipe
- ✅ **No bare `except` clauses** — Every try/except block catches specific exception types (`OSError`, `IOError`, `subprocess.SubprocessError`, `json.JSONDecodeError`, etc.). One documented outermost catch-all retained in `run()` as last-resort handler
- ✅ **Categorized timeout constants** — 6 named timeouts (QUICK 5s, NETWORK 10s, API 15s, DOWNLOAD 120s, INSTALL 300s, UPDATE 600s) prevent hanging operations
- ✅ **Secure external script execution** — Waydroid repository script downloaded to temp file, validated (shebang check to catch HTML error pages), then executed and cleaned up. No `curl | bash`
- ✅ **Atomic file writes** — Rollback manifest written to temp file then `os.replace()` to prevent corruption on crash
- ✅ **Signal handling** — SIGTERM/SIGINT handlers save installation state and rollback manifest before clean exit
- ✅ **Post-install health check** — Verifies installed packages, binaries, Flatpak apps, and GPU drivers after installation

**Core Protections (All Versions):**

- ✅ No arbitrary code execution from user input
- ✅ No `eval()` or `exec()` usage
- ✅ Validates package sources before installation
- ✅ Creates backups before modifications
- ✅ Comprehensive logging of all operations
- ✅ Sudo timeout for sensitive operations
- ✅ Validates sudoers file syntax before applying
- ✅ Input validation and sanitization
- ✅ GE-Proton SHA512 checksum verification ✨
- ✅ Wine repository URL validation via HTTP HEAD ✨
- ✅ Network connectivity pre-check before remote operations ✨
- ✅ System requirements pre-flight validation ✨

**Verification:**
- Package signatures verified by APT
- Flatpak apps verified by Flathub
- GitHub releases verified via HTTPS
- GE-Proton tarballs verified via SHA512 checksums ✨
- Self-update validates syntax via `py_compile` before replacing ✨
- Downloaded scripts validated (shebang check) before execution ✨

---

## Known Security Limitations

### 1. Third-Party Repositories

The script adds the following repositories:
- **WineHQ** - wine.org official repository (URL validated before adding) ✨
- **Waydroid** - waydro.id official repository (script validated before executing) ✨
- **Flathub** - Flatpak application repository

**Risk:** Compromised repositories could serve malicious packages
**Mitigation:** Only uses official, well-known repositories; validates URLs before adding; secure download-then-execute for Waydroid

### 2. Flatpak Applications

Flatpak apps run in sandboxes but may request permissions:
- File system access
- Network access
- Device access (GPU, audio)

**Risk:** Malicious Flatpak app could abuse permissions
**Mitigation:** Only installs from Flathub (verified apps); Flatpak setup deduplicated through `ensure_flatpak_ready()` with session caching

### 3. GitHub Downloads

GE-Proton is downloaded from GitHub releases. Self-update downloads from GitHub.

**Risk:** Man-in-the-middle attack or compromised GitHub account
**Mitigation:**
- Downloaded via HTTPS, GitHub's security measures
- GE-Proton: SHA512 checksum verification against published `.sha512sum` file ✨
- Self-update: Syntax validation via `py_compile` before replacing running script ✨
- Self-update: Current version backed up as `.v{version}.backup` before replacement ✨

### 4. Sudo Configuration

Script can configure passwordless sudo for CPU frequency control.

**Risk:** Could be abused if user account is compromised
**Mitigation:**
- Only allows specific commands (`cpupower`, `cpufreq-set`)
- Validates sudoers syntax before applying
- User is prompted for confirmation

### 5. Root Execution Model

The entire script runs as root.

**Risk:** Any bug could affect system-wide
**Mitigation:**
- Files in user home directories are `chown`ed to the real user (resolved from `$SUDO_USER`)
- Signal handlers save state before exit ✨
- Rollback engine can undo all changes ✨
- Dry-run mode for safe testing

---

## Best Practices for Users

### Before Running

1. ✅ **Review the script** - Read the code to understand what it does
2. ✅ **Use dry-run mode** - Test with `--dry-run` flag first
3. ✅ **Validate system** - Run `--check-requirements` first ✨
4. ✅ **Backup your data** - Create system backup before major changes
5. ✅ **Check source** - Download from official repository only
6. ✅ **Verify integrity** - Check file hash if provided

### During Installation

1. ✅ **Monitor output** - Watch for unexpected behavior
2. ✅ **Check logs** - Review `~/gaming_setup_logs/` for issues
3. ✅ **Don't interrupt** - Let the script complete to avoid partial installs
4. ✅ **Signal safety** - If you must interrupt, use Ctrl+C (state will be saved) ✨

### After Installation

1. ✅ **Review health check** - Check the post-install verification output ✨
2. ✅ **Review logs** - Check for warnings or errors
3. ✅ **Verify packages** - Confirm installed packages are legitimate
4. ✅ **Test in isolation** - Try one feature at a time initially
5. ✅ **Report issues** - Notify us of any suspicious behavior
6. ✅ **Know your rollback** - `--rollback` can undo the entire installation ✨

---

## Security Update Policy

### Critical Security Issues
- **Response Time:** 24-48 hours
- **Fix Timeline:** Emergency patch within 7 days
- **Notification:** GitHub Security Advisory + email to users

### High Priority Issues
- **Response Time:** 48-72 hours
- **Fix Timeline:** Patch in next minor release (2-4 weeks)
- **Notification:** GitHub Security Advisory

### Medium/Low Priority Issues
- **Response Time:** 1 week
- **Fix Timeline:** Next regular release
- **Notification:** Mentioned in CHANGELOG.md

---

## Secure Usage Guidelines

### Recommended Practices

**✅ DO:**
- Download from official repository only
- Verify script before running
- Use `--dry-run` to test
- Use `--check-requirements` to validate ✨
- Keep your system updated
- Review logs regularly
- Use `--rollback` if something goes wrong ✨
- Report suspicious behavior

**❌ DON'T:**
- Run scripts from untrusted sources
- Skip system updates
- Ignore warning messages
- Run as root unnecessarily (use sudo)
- Disable security features
- Ignore the post-install health check output ✨

### Environment-Specific Considerations

**Production Systems:**
- Test on non-production system first
- Use `--dry-run` mode
- Schedule during maintenance windows
- Have rollback plan ready (`--rollback` available) ✨

**Development Systems:**
- Still use caution with root access
- Review logs for unexpected behavior
- Keep backups of important projects

**Virtual Machines:**
- Snapshot before running
- Test in isolated VM first
- Verify network restrictions work

---

## Dependency Security

### Package Sources

All packages come from trusted sources:
- **Ubuntu/Debian repositories** - Official, signed packages
- **WineHQ** - Official repository (URL validated before adding) ✨
- **Flathub** - Verified Flatpak applications
- **GitHub Releases** - HTTPS, GE-Proton with SHA512 verification ✨
- **Waydroid** - Official repository (script validated before executing) ✨

### Known Vulnerabilities

We monitor:
- Ubuntu Security Notices
- Debian Security Advisories
- CVE databases
- GitHub Security Advisories

**Found vulnerability in dependency?** Report it to us and the upstream project.

---

## Incident Response

### If You Suspect Compromise

1. **Stop the script** immediately (Ctrl+C — state will be saved) ✨
2. **Disconnect from network** (if actively compromised)
3. **Preserve evidence** - Don't delete logs
4. **Review logs** - Check `~/gaming_setup_logs/`
5. **Use rollback** - `sudo python3 debian_gaming_setup.py --rollback` ✨
6. **Report to us**
7. **System scan** - Run antivirus/malware scan
8. **Change passwords** - If credentials may be compromised

### What We'll Do

1. **Acknowledge** report within 48 hours
2. **Investigate** the issue thoroughly
3. **Develop fix** if vulnerability confirmed
4. **Release patch** as soon as possible
5. **Publish advisory** with details and mitigation
6. **Credit reporter** (unless anonymous preferred)

---

## Security Audit

### Self-Audit Checklist

You can verify security by checking:

- [ ] Script source code is readable
- [ ] No obfuscated code
- [ ] No `shell=True` in subprocess calls ✨
- [ ] No bare `except` clauses (except documented outermost handler) ✨
- [ ] No `eval()` or `exec()` usage
- [ ] No network calls except to known repositories
- [ ] No data exfiltration
- [ ] Proper error handling with specific exception types ✨
- [ ] Input validation present
- [ ] Sudo usage is minimal and specific
- [ ] Backups created before changes
- [ ] Comprehensive logging enabled
- [ ] Timeout constants used for all operations ✨
- [ ] Signal handlers save state on interruption ✨
- [ ] Checksum verification for downloaded files ✨

### Professional Audit

We welcome security researchers to:
- Review the code
- Perform penetration testing
- Suggest improvements
- Report findings responsibly

---

## Security Changelog ✨

| Version | Security Change |
|---------|----------------|
| 3.4.2 | GE-Proton checksum verification skipped in dry-run mode (prevents false FileNotFoundError), health check summary now details specific warnings/failures |
| 3.4.1 | Fixed runtime TypeError from mixed logging format, AMD GPU false detection via 'ati'/'compatible' substring collision, eliminated all f-string logging (20 calls → %-format), wrapped unprotected os.chown calls, atomic state file write, test suite expanded to 136 tests (100% critical method coverage) |
| 3.4.0 | Expanded CI/CD with Bandit integration, 7 lint checks (added encoding + import validation), issue templates with security vulnerability form, PR template with security gate, comprehensive .gitignore with secrets section |
| 3.3.0 | Full --uninstall mode, `_check_package_available` fixed to use `apt-cache policy` (prevents false-positive availability on ZorinOS), bounded Flatpak remote queries |
| 3.3.0 | 90-test automated suite with 24 security/host-safety tests, CI/CD pipeline with security gates, pre-commit hooks |
| 3.0.0 | Bounded network reads (MAX_RESPONSE_BYTES), secure tempfile usage, eval elimination in bash, TOCTOU fixes, Python 3.12+ with StrEnum and dataclass slots |
| 2.6.0 | Pre-install detection for 7 methods, Flatpak command resolver, vkBasalt URL correction |
| 2.5.0 | Eliminated all shell=True, fixed bare except clauses, signal handlers, secure Waydroid install, categorized timeouts, Flatpak deduplication |
| 2.4.0 | Self-update syntax validation via py_compile, atomic script replacement |
| 2.3.0 | Atomic manifest writes (os.replace), GE-Proton SHA512 checksum verification |
| 2.2.0 | Wine URL validation before repo addition, network connectivity pre-check, package availability validation |
| 2.1.0 | Version-aware MangoHud installation, repository cleanup improvements |
| 2.0.0 | Input validation, structured logging, state management |

---

## Legal

### Responsible Disclosure

We follow responsible disclosure practices:
- We won't take legal action against researchers acting in good faith
- We'll work with you to understand and fix issues
- We'll credit you appropriately in security advisories

### Scope

**In Scope:**
- Security vulnerabilities in script code
- Privilege escalation issues
- Code injection possibilities
- Authentication/authorization bypasses
- Data exposure issues
- Unsafe subprocess execution patterns

**Out of Scope:**
- Vulnerabilities in dependencies (report to upstream)
- Social engineering attacks
- Physical security issues
- Denial of service (local script)

---

## Contact

**General Issues:** [Issues](https://github.com/Sandler73/Debian-Gaming-Setup-Project/issues)

**GPG Key:** Available on request

**Response Times:**
- Critical: 24 hours
- High: 48 hours
- Medium: 1 week

---

## Updates

This security policy is reviewed quarterly and updated as needed.

**Last Updated:** February 2026
**Next Review:** May 2026
**Version:** 3.5.0

---

**Thank you for helping keep this project secure! 🔒**
