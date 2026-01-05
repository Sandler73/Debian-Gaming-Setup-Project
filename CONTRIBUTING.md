# Contributing to Debian-Based Gaming Setup Script

Thank you for your interest in contributing! This project aims to make Linux gaming accessible to everyone, and your contributions help achieve that goal.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

---

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of:
- Experience level
- Gender identity and expression
- Sexual orientation
- Disability
- Personal appearance
- Body size
- Race or ethnicity
- Age
- Religion
- Nationality

### Expected Behavior

- **Be respectful** - Different viewpoints and experiences are valuable
- **Be collaborative** - Work together towards common goals
- **Be patient** - Help newcomers learn
- **Be constructive** - Offer helpful feedback
- **Be inclusive** - Welcome diverse perspectives

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks or trolling
- Publishing others' private information
- Spam or off-topic content
- Any conduct that would be inappropriate in a professional setting

---

## 🎯 How Can I Contribute?

### Reporting Bugs 🐛

**Before Submitting:**
1. Check existing issues to avoid duplicates
2. Test with the latest version
3. Use `--dry-run` to reproduce safely

**Bug Report Should Include:**
- **System information** - Distribution, version, architecture
- **GPU/Hardware** - GPU vendor, VM if applicable
- **Steps to reproduce** - Exact commands used
- **Expected behavior** - What should happen
- **Actual behavior** - What actually happened
- **Logs** - Relevant excerpts from `~/gaming_setup_logs/`
- **Screenshots** - If applicable

**Example Bug Report:**
```markdown
## Bug Description
MangoHud fails to install on Ubuntu 24.04

## System Information
- **OS:** Ubuntu 24.04.3 LTS
- **GPU:** NVIDIA RTX 3060
- **Virtualization:** None

## Steps to Reproduce
1. sudo python3 debian_gaming_setup.py --mangohud
2. Installation fails with "Package not found"

## Expected
MangoHud should install from repos

## Actual
Error: E: Unable to locate package mangohud

## Logs
[Paste relevant log excerpt]
```

### Suggesting Features 💡

**Good Feature Requests Include:**
- **Clear description** - What feature you want
- **Use case** - Why you need it
- **Examples** - How it would work
- **Alternatives considered** - Other solutions you've thought of

**Example Feature Request:**
```markdown
## Feature Description
Add support for installing GameHub launcher

## Use Case
GameHub provides unified library management for Steam, GOG, and more

## Proposed Implementation
- Add --gamehub CLI flag
- Install via Flatpak (com.github.tkashkin.gamehub)
- Include in installation summary

## Alternatives
- User can install manually
- Could document instead of automating
```

### Testing on Different Distributions 🧪

We need testers for:
- Ubuntu variants (Kubuntu, Xubuntu, Ubuntu MATE)
- Linux Mint editions (Cinnamon, MATE, Xfce)
- Debian (Stable, Testing, Unstable)
- Pop!_OS
- Elementary OS
- Zorin OS
- Other Debian-based distributions

**How to Help:**
1. Test on your distribution
2. Report results (success or failure)
3. Provide logs for failures
4. Document any distribution-specific quirks

### Improving Documentation 📖

Documentation improvements are always welcome:
- Fix typos or unclear instructions
- Add examples
- Improve explanations
- Translate to other languages (future)
- Create video tutorials (external)

### Writing Code 💻

See [Development Setup](#development-setup) below.

---

## 🛠️ Development Setup

### Prerequisites

```bash
# Install Python development tools
sudo apt-get install python3 python3-pip git

# Clone repository
git clone https://github.com/Sandler73/Debian-Gaming-Setup-Project.git
cd gaming-setup

# Create development branch
git checkout -b feature/your-feature-name
```

### Testing Your Changes

```bash
# Always test with dry-run first
sudo python3 debian_gaming_setup.py --dry-run [your-options]

# Test in a VM if making significant changes
# Recommended: Create VM snapshot first

# Test interactive mode
sudo python3 debian_gaming_setup.py

# Test automated mode
sudo python3 debian_gaming_setup.py -y --your-new-feature
```

### Code Structure

```
debian_gaming_setup_truly_enhanced.py
├── Imports and Constants (lines 1-200)
├── Helper Functions (lines 200-300)
├── Data Classes (lines 300-400)
├── Argument Parser (lines 400-520)
├── GamingSetup Class
│   ├── Initialization (lines 520-700)
│   ├── Detection Methods (lines 700-1200)
│   ├── Driver Installation (lines 1200-1700)
│   ├── Gaming Platforms (lines 1700-2100)
│   ├── Compatibility Layers (lines 2100-2300)
│   ├── Utilities (lines 2300-2700)
│   ├── Optimizations (lines 2700-2900)
│   ├── Installation Summary (lines 2900-3000)
│   └── Main Execution (lines 3000-3300)
└── Main Entry Point (lines 3300-3341)
```

---

## 🔄 Pull Request Process

### 1. Fork and Branch

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/Sandler73/Debian-Gaming-Setup-Project.git
cd gaming-setup

# Create feature branch
git checkout -b feature/descriptive-name
# or
git checkout -b fix/issue-description
```

### 2. Make Changes

- Follow [Coding Standards](#coding-standards)
- Add comments explaining your changes
- Update documentation if needed
- Test thoroughly

### 3. Commit

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "Add support for GameHub launcher

- Add install_gamehub() method
- Add --gamehub CLI flag
- Update installation summary
- Add documentation"
```

**Good Commit Messages:**
- Start with imperative verb (Add, Fix, Update, Remove)
- First line: Brief summary (50 chars or less)
- Blank line
- Detailed explanation if needed
- Reference issues: "Fixes #123" or "Relates to #456"

### 4. Push and Create PR

```bash
# Push to your fork
git push origin feature/descriptive-name

# Create pull request on GitHub
# Fill in the PR template
```

### 5. PR Review Process

**Checklist:**
- [ ] Code follows style guidelines
- [ ] Comments added where needed
- [ ] Documentation updated
- [ ] Tested with `--dry-run`
- [ ] Tested on at least one distribution
- [ ] No merge conflicts
- [ ] Passes any automated checks

**Review Timeline:**
- Initial review: 2-3 days
- Follow-up: 1-2 days after changes
- Merge: After approval from maintainer

---

## 📝 Coding Standards

### Python Style

**Follow PEP 8** with these specifics:

```python
# Indentation: 4 spaces (no tabs)
def my_function():
    if condition:
        do_something()

# Line length: 100 characters max (120 acceptable for long strings)

# Function names: snake_case
def install_gaming_platform():
    pass

# Class names: PascalCase
class GamingSetup:
    pass

# Constants: UPPER_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 300

# Private methods: leading underscore
def _internal_helper():
    pass
```

### Documentation

**Docstrings for all methods:**

```python
def install_new_tool(self):
    """
    Install NewTool via Flatpak
    
    NEW FEATURE: Brief description of what this tool does
    
    Performs:
        - Checks if Flatpak is installed
        - Adds Flathub repository
        - Installs com.example.NewTool
        - Creates default configuration
    
    Returns:
        bool: True if successful, False otherwise
    
    Example:
        >>> setup.install_new_tool()
        Installing NewTool via Flatpak...
        ✓ NewTool installed successfully
    """
    # Implementation
```

### Comments

**Good comments explain WHY, not WHAT:**

```python
# Good
# Use Flatpak because package not in Ubuntu 24.04 repos
self.run_command(["flatpak", "install", ...])

# Bad
# Install package
self.run_command(["flatpak", "install", ...])

# Good
# PRESERVED FROM ORIGINAL: Exact same version checking logic
if self.is_package_installed(package_name):
    ...

# Good
# ENHANCED: Added fallback for Ubuntu 24.04 compatibility
if not success:
    # Try alternative package name
```

### Error Handling

**Always handle errors gracefully:**

```python
# Good
success, stdout, stderr = self.run_command(
    cmd, 
    description,
    check=False  # Don't fail completely
)

if not success:
    print(f"{Color.YELLOW}⚠ Installation failed{Color.END}")
    print(f"{Color.CYAN}  Manual installation: https://example.com{Color.END}")
    return  # Continue with rest of script

# Bad
self.run_command(cmd, description)  # Will crash on error
```

### Configuration

**Add to InstallationConfig dataclass:**

```python
@dataclass
class InstallationConfig:
    # ... existing fields ...
    
    # NEW: Your feature
    install_your_feature: bool = False  # Brief comment
```

**Add to argument parser:**

```python
tools.add_argument('--your-feature', action='store_true',
                  help='Install YourFeature (brief description)')
```

**Add to config initialization:**

```python
config.install_your_feature = getattr(self.args, 'your_feature', False)
```

---

## 🧪 Testing Guidelines

### Manual Testing Checklist

**Before Submitting PR:**

- [ ] Tested with `--dry-run` flag
- [ ] Tested interactive mode (no CLI args)
- [ ] Tested automated mode (with CLI args)
- [ ] Tested on clean system (VM recommended)
- [ ] Verified logs contain no errors
- [ ] Checked installation summary shows component
- [ ] Tested actual functionality of installed component
- [ ] Reviewed all print statements for clarity

### Test Scenarios

**Minimum Test Matrix:**

| Scenario | Expected Result |
|----------|----------------|
| `--dry-run --your-feature` | Shows what would be done |
| `--your-feature` (interactive) | Prompts user, respects answer |
| `-y --your-feature` | Installs without prompts |
| Feature already installed | Detects, offers update/reinstall |
| Installation failure | Graceful error, continues script |
| Incompatible system | Warns, allows override or skips |

### VM Testing (Recommended)

**Set up test VM:**
1. Create Ubuntu 24.04 VM
2. Take snapshot
3. Test your changes
4. Revert snapshot
5. Test again to verify reproducibility

**Recommended VMs:**
- Ubuntu 24.04 (primary)
- Ubuntu 22.04 (LTS)
- Debian 12 (stable)
- Linux Mint 22 (Ubuntu-based)

---

## 📚 Documentation

### What to Update

**When adding new feature:**
1. **README.md** - Add to feature list and examples
2. **Usage_Guide.md** - Full documentation with examples
3. **Quick_Start.md** - If relevant for beginners
4. **CHANGELOG.md** - Add to "Unreleased" section
5. **Code comments** - Explain implementation

### Documentation Style

**Be clear and concise:**
- Use active voice
- Provide examples
- Explain prerequisites
- Show expected output
- Link to external docs when appropriate

**Example:**
```markdown
### Install YourFeature

YourFeature provides X functionality for Y purpose.

**CLI Flag:** `--your-feature`

**Prerequisites:**
- Python 3.6+
- Internet connection

**Usage:**
```bash
# Interactive
sudo python3 debian_gaming_setup.py

# Automated
sudo python3 debian_gaming_setup.py --your-feature
```

**Post-Installation:**
```bash
# Verify installation
your-feature --version

# Basic usage
your-feature command
```

**Configuration:**
Edit `~/.config/your-feature/config.conf`:
```ini
setting = value
```

**Troubleshooting:**
- Issue 1: Solution 1
- Issue 2: Solution 2
```

---

## 👥 Community

### Communication Channels

- **GitHub Issues** - Bug reports, feature requests
- **GitHub Discussions** - General questions, ideas
- **Pull Requests** - Code contributions

### Getting Help

**Need help contributing?**
- Read existing code for examples
- Check closed PRs for similar changes
- Ask in GitHub Discussions
- Reference this guide

### Recognition

Contributors are recognized in:
- GitHub contributors page
- CHANGELOG.md (for significant contributions)
- README.md acknowledgments section

---

## 📋 Checklist for Contributors

**Before submitting PR:**

- [ ] Forked repository and created feature branch
- [ ] Made changes following coding standards
- [ ] Added comments and docstrings
- [ ] Tested with `--dry-run`
- [ ] Tested on at least one distribution
- [ ] Updated relevant documentation
- [ ] Updated CHANGELOG.md
- [ ] Committed with descriptive messages
- [ ] Pushed to your fork
- [ ] Created pull request with filled template
- [ ] Responded to review feedback

---

## 🙏 Thank You!

Every contribution helps make Linux gaming more accessible. Whether you're fixing a typo, adding a feature, or testing on a new distribution, your effort is appreciated!

**Happy Contributing!** 🎮

---

**Questions?** Open a GitHub Discussion or comment on an issue!
- [Discussions](https://github.com/Sandler73/Debian-Gaming-Setup-Project/discussions)
- [Issues](https://github.com/Sandler73/Debian-Gaming-Setup-Project/issues)

**Version:** 2.1.0  
**Last Updated:** January 2026
