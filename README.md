# 🏥 AutoHeal AI

> **Autonomous Self-Healing Software Engine** — Install once, self-heal forever.

AutoHeal AI is a language-agnostic CLI tool that wraps any command, detects errors in real-time, and automatically diagnoses and fixes them using AI.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

- 🔍 **Real-time Error Detection** — Monitors stdout/stderr for errors across 8+ languages
- 🧠 **AI-Powered Diagnosis** — Uses LLM (GPT-4o, Claude, Gemini, Ollama) for root cause analysis
- 🔧 **Auto-Fix** — Restarts crashed processes, installs missing dependencies
- 💡 **Smart Suggestions** — Generates code patches with diff preview (user-approved)
- 📚 **Learning Memory** — Remembers past errors and solutions for instant future fixes
- 🔒 **Safety-First** — Never auto-applies code changes; secrets redacted before LLM calls
- 🌍 **Language Agnostic** — Works with Python, Node.js, Go, Rust, Java, Ruby, PHP, and more

---

## 🚀 Quick Start

### Install

```bash
pip install autoheal-ai
```

### Setup

```bash
# Initialize in your project
cd your-project/
autoheal init

# Set your LLM API key
autoheal config set llm.api_key sk-proj-your-key-here

# (Optional) Use a different provider
autoheal config set llm.provider anthropic  # or google, ollama
```

### Run

```bash
# Monitor any command
autoheal run "python app.py"
autoheal run "npm start"
autoheal run "go run main.go"
autoheal run "cargo run"
```

---

## 📖 How It Works

```
You run:  autoheal run "python app.py"

┌─────────────┐     ┌──────────┐     ┌─────────────┐
│  Sentinel    │────>│   CECE   │────>│ Diagnostics  │
│  (Detect)    │     │ (Context)│     │ (Root Cause) │
└─────────────┘     └──────────┘     └──────┬───────┘
                                            │
┌─────────────┐     ┌──────────┐     ┌──────▼───────┐
│   Memory     │<────│ Harness  │<────│  Resolution  │
│   (Learn)    │     │ (Safety) │     │    (Fix)     │
└─────────────┘     └──────────┘     └──────────────┘
```

1. **Sentinel** watches your process output for errors
2. **CECE** builds full context (source code, environment, dependencies)
3. **Diagnostics** determines root cause via pattern matching + AI
4. **Resolution** generates the appropriate fix
5. **Harness** checks safety gates before applying
6. **Memory** stores the resolution for future instant fixes

---

## 🛠 CLI Commands

| Command | Description |
|---------|-------------|
| `autoheal init [path]` | Initialize AutoHeal in a project |
| `autoheal run <command>` | Run and monitor a command |
| `autoheal status` | Show error statistics |
| `autoheal history [-n 20]` | Show fix history |
| `autoheal config list` | Show all configuration |
| `autoheal config set <key> <val>` | Set a config value |
| `autoheal config get <key>` | Get a config value |
| `autoheal diagnose <error>` | Manually diagnose an error |
| `autoheal version` | Show version |

---

## ⚙️ Configuration

AutoHeal stores configuration in `.autoheal/config.toml`:

```toml
[llm]
provider = "openai"           # openai, anthropic, google, ollama
model = ""                    # Auto-selects best model per provider
api_key = "sk-proj-..."       # Your API key
temperature = 0.2

[resolution]
confidence_threshold = 0.75   # Min confidence for auto-fix
code_patch_threshold = 0.90   # Min confidence to suggest code patch
create_backup = true          # Git backup before patches

[general]
mode = "auto"                 # auto, suggest, manual
verbose = false
```

---

## 🤖 Supported LLM Providers

| Provider | Model | Setup |
|----------|-------|-------|
| **OpenAI** (default) | GPT-4o | `autoheal config set llm.api_key sk-...` |
| **Anthropic** | Claude 3.5 Sonnet | `autoheal config set llm.provider anthropic` |
| **Google** | Gemini 2.0 Flash | `autoheal config set llm.provider google` |
| **Ollama** (local) | Llama 3.1 | `autoheal config set llm.provider ollama` |

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.
