# jps-pre-commit-utils

![Build](https://github.com/jai-python3/jps-pre-commit-utils/actions/workflows/test.yml/badge.svg)
![Publish to PyPI](https://github.com/jai-python3/jps-pre-commit-utils/actions/workflows/publish-to-pypi.yml/badge.svg)
[![codecov](https://codecov.io/gh/jai-python3/jps-pre-commit-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/jai-python3/jps-pre-commit-utils)

Custom pre-commit utilities for detecting debug/test leftovers, hardcoded paths, and environment-specific code
fragments in Python, Perl, and YAML files before they are committed.  
These checks catch issues that are not easily detected by flake8, black, mypy, or bandit.

---

## 🧩 Features

✅ Scans *staged diffs* (`git diff --cached`) before commit  
✅ Detects newly added lines containing:

- Debugging and testing statements (e.g., `print`, `sys.exit`, `pdb.set_trace`, `logger.debug`)
- Hardcoded filesystem paths (e.g., `/mnt/synth-genomics3/...`)
- Hardcoded environment variables or hostnames
- Inline comments with “test” or “TODO”
✅ Supports **Python**, **Perl**, and **YAML** files  
✅ Configurable via `.my-pre-commit-checks.yaml` or `~/.config/my-pre-commit-checks.yaml`  
✅ Integrates easily with manual usage or `.pre-commit-config.yaml`

---

## 🧩 Installation

```bash
pip install jps-pre-commit-utils
```

For local development:

```bash
git clone git@github.com:jai-python3/jps-pre-commit-utils.git
cd jps-pre-commit-utils
pip install -e '.[dev]'
```

---

## 🧩 Usage

Run manually:

```bash
jps-pre-commit-util-checks
```

Or integrate with Git pre-commit:

```bash
# .git/hooks/pre-commit
#!/bin/bash
python3 -m jps_pre_commit_utils.check_inserted_lines
```

---

## 🧩 Example Configuration

Configuration file:  
`.my-pre-commit-checks.yaml` *(in repo root)*  
or  
`~/.config/my-pre-commit-checks.yaml` *(global fallback)*

```yaml
# Example configuration for jps-pre-commit-utils
base_paths:
  - /mnt/synth-genomics3
  - /Users
ignore_patterns:
  - /mnt/synth-genomics3/bioinfo/shared/
extra_regexes:
  - "jira/[A-Z]+-[0-9]+"
```

---

## 🧩 Example Output

```bash
---------------------------------------------------------
🔧 Performing the following checks:
---------------------------------------------------------
• 🐍 Python debug/test statements
• 🐪 Perl debug/test statements
• 📁 Hardcoded absolute paths
• 🧪 Comments containing 'test' or 'testing'
---------------------------------------------------------
Scanning inserted lines ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% • 45/45
---------------------------------------------------------
🔍 Pre-commit inserted-line scan results
---------------------------------------------------------
⚠️  File: src/example.py, Line: 18
    Added line contains pattern: "#[  ]*.*test"
    → # test
---------------------------------------------------------
⚠️  Total findings: 1
---------------------------------------------------------
```

---

## 🧱 Development

Install dependencies for linting, formatting, and testing:

```bash
make install-build-tools
```

Run all development checks:

```bash
make fix && make format && make lint
make test
```

---

## 🧪 Testing

```bash
make test
```

---

## 🧾 License

MIT License  
© 2025 Jaideep Sundaram

---

## 🧠 Notes

- The utility is designed for use with Git repositories that follow a Gitflow workflow.  
- Configuration is fully customizable; extend `.my-pre-commit-checks.yaml` to add your own regexes.  
- Future versions will include additional checks for breakpoints, asserts, sleep statements, and other runtime risks.  

---

### 🧩 Example Workflow

```bash
# Edit a file
echo '# test' >> src/sample.py

# Stage and check
git add src/sample.py
jps-pre-commit-checks
```

If issues are found, they are listed as warnings.  
If none are found, you’ll see:

```bash
✅ No issues detected. (0 findings)
```
