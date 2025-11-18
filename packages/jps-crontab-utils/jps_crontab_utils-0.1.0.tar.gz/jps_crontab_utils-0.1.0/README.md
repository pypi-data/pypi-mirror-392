# jps-crontab-utils

![Build](https://github.com/jai-python3/jps-crontab-utils/actions/workflows/test.yml/badge.svg)
![Publish to PyPI](https://github.com/jai-python3/jps-crontab-utils/actions/workflows/publish-to-pypi.yml/badge.svg)
[![codecov](https://codecov.io/gh/jai-python3/jps-crontab-utils/branch/main/graph/badge.svg)](https://codecov.io/gh/jai-python3/jps-crontab-utils)

Collection of Python utilities for parsing, validating, and searching crontab files.

## 🚀 Overview

`jps-crontab-utils` provides three command-line tools:

### **1. Crontab Parser**
Parses raw crontab files into structured job objects:

- Supports per-job metadata via comment blocks  
- Handles multiline commands with POSIX `\` continuation  
- Resolves executables using `$PATH` or absolute paths  
- Normalizes metadata keys automatically (`owner-email` → `owner_email`)

### **2. Crontab Checker**
Validates each cron job for:

- Required metadata (owner, owner email, reference, repository, etc.)
- Recommended metadata (labels, run frequency, description, etc.)
- Executable existence, file type, +x bit, and non-empty status  
- Outputs human-readable tables **or JSON for automation**

### **3. Crontab Search Utility**
Queries crontab entries based on:

- Labels (`--label nightly`)
- Owner email (`--email john.smith`)
- Code repository (`--repo git@gitlab.com:org/pipeline.git`)
- Full JSON output for programmatic analysis

These utilities help improve crontab hygiene, enforce team standards, and identify broken or undocumented jobs across large environments.

---

## Features

- 🔍 **Search** cron jobs using metadata filters  
- 📝 **Parse** job schedule, command, metadata  
- 🛠 **Validate** executables and metadata completeness  
- 📈 **Rich terminal tables** (typer + rich)  
- 📦 **JSON output** for CI/CD and automation  
- 🧪 **100% test-covered parser and search modules**

---

## Example Usage

#### **Parse and inspect a crontab**

```bash
jps-crontab-parse --file /etc/crontab
```
Search for jobs labeled “nightly”

```bash
jps-crontab-search --file crontab.txt --label nightly
```

Audit a crontab

```bash
jps-crontab-check --file crontab.txt
```

JSON mode for pipelines

```bash
jps-crontab-check --file crontab.txt --json | jq .
```

## 📦 Installation

```bash
make install
```

```bash
pip install jps-crontab-utils
```


## 🧪 Development

```bash
make fix && make format && make lint
make test
```


## 📜 License
MIT License © Jaideep Sundaram

## Documentation

📘 Full documentation: see docs/USAGE.md