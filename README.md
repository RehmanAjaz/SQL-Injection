<div align="center">

```
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║    ███████╗ ██████╗ ██╗     ██╗    ███████╗ ██████╗ █████╗ N   ║
║    ██╔════╝██╔═══██╗██║     ██║    ██╔════╝██╔════╝██╔══██╗    ║
║    ███████╗██║   ██║██║     ██║    ███████╗██║     ███████║    ║
║    ╚════██║██║▄▄ ██║██║     ██║    ╚════██║██║     ██╔══██║    ║
║    ███████║╚██████╔╝███████╗██║    ███████║╚██████╗██║  ██║    ║
║    ╚══════╝ ╚══▀▀═╝ ╚══════╝╚═╝    ╚══════╝ ╚═════╝╚═╝  ╚═╝   ║
║                                                                  ║
║              P R O  —  A D V A N C E D  E D I T I O N          ║
╚══════════════════════════════════════════════════════════════════╝
```

# SQLi Scanner Pro

**Advanced SQL Injection Testing Suite with Built-in Vulnerable Demo Server**

[![Python](https://img.shields.io/badge/Python-3.x-00CC77?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-00A8D6?style=for-the-badge&logo=python&logoColor=white)](https://docs.python.org/3/library/tkinter.html)
[![License](https://img.shields.io/badge/License-Educational_Only-E03333?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-9966DD?style=for-the-badge)](https://github.com)
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero_(stdlib_only)-E0A000?style=for-the-badge)](https://github.com)

> ⚠️ **FOR EDUCATIONAL AND AUTHORIZED PENETRATION TESTING ONLY** ⚠️
> Unauthorized use against systems you do not own or have explicit permission to test is illegal.

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Screenshots](#-screenshots)
- [Installation](#-installation)
- [Usage](#-usage)
- [Injection Categories](#-injection-categories)
- [Detection Engine](#-detection-engine)
- [Architecture](#-architecture)
- [Output & Export](#-output--export)
- [Remediation Guide](#-remediation-guide)
- [Legal Disclaimer](#-legal-disclaimer)

---

## 🔍 Overview

**SQLi Scanner Pro** is a fully self-contained, desktop SQL injection testing tool built with pure Python. No pip packages. No external dependencies. Just Python 3 and you're ready to scan.

The tool ships with a **built-in intentionally vulnerable HTTP demo server** so you can practice, learn, and test the detection engine locally — completely offline. A custom dark-themed GUI provides a professional workflow from target configuration to vulnerability reporting.

```
┌─────────────────────────────────────────────────────────────────┐
│  Target URL  →  Auto-Detect Params  →  Select Categories        │
│       ↓                                                          │
│  Multi-threaded Payload Engine  →  Real-time Detection          │
│       ↓                                                          │
│  Severity-Graded Findings  →  JSON Export                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Description |
|---|---|
| 🖥️ **Dark GUI** | Custom dark-themed Tkinter interface (1300×880px, resizable) |
| 🌐 **Built-in Demo Server** | Local vulnerable HTTP server auto-starts on port `18321` |
| 💉 **47 Payloads** | 6 injection categories, 47 carefully curated payloads |
| 🔍 **Smart Detection** | 30+ error signatures covering MySQL, MSSQL, PostgreSQL, Oracle, SQLite |
| ⚡ **Multi-threaded** | Non-blocking scan worker + responsive UI at all times |
| 📊 **Live Metrics** | Real-time progress bar, test counter, vulnerability counter |
| 🎯 **Confidence Scoring** | Each finding rated HIGH / MEDIUM / LOW with a percentage score |
| 📥 **JSON Export** | Timestamped export of all findings with full technical details |
| 🛑 **Stop Anytime** | Graceful scan cancellation with the STOP button |
| ✏️ **Manual Params** | Add parameters by hand or use auto-detection from the URL |

---

## 🖼️ Screenshots

### Application Banner & Live Metrics
```
╔══════════════════════════════════════════════════════════════════════════╗
║  [SQLi]  SQLi Scanner Pro                  TOTAL   DONE   VULNS  STATUS ║
║          Advanced SQL Injection Testing    [ 38 ] [ 38 ] [  4 ] [DONE]  ║
╠══════════════════════════════════════════════════════════════════════════╣
║  ████████████████████████████████████████████████████████  100%         ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### Main Interface
```
┌──────────────────────────┬───────────────────────────────────────────────┐
│ [*] TARGET CONFIG        │ [ SCAN LOG ] [ FINDINGS ] [ ANALYSIS ]        │
│ URL: http://target/      │ ════════════════════════════════════════════   │
│ [Auto-Detect] [Manual+]  │  SCAN STARTED: http://127.0.0.1:18321/user   │
│                          │ ════════════════════════════════════════════   │
│ [!] DEMO TARGETS         │  ok  id <- ' AND '1'='1... safe               │
│ [>] /user?id=1  ERROR    │  ok  id <- ' AND '1'='2... safe               │
│ [>] /search?q=  UNION    │                                                │
│ [>] /login?usr= BOOL     │  *** VULNERABLE! [HIGH] param=id              │
│                          │      Type   : Error-Based SQLi                 │
│ [+] PARAMETERS           │      Payload : '                               │
│  ☑ id                    │      Details : DB error: "SQL syntax..."       │
│                          │      Conf    : 92%  |  0.32s                   │
│ [~] CATEGORIES           │                                                │
│  ☑ Error-Based           │  *** VULNERABLE! [HIGH] param=id              │
│  ☑ Boolean-Based         │      Type   : Union-Based SQLi (Data Leak)    │
│  ☑ Time-Based            │      Payload : ' UNION SELECT username,pass-- │
│  ☑ Union-Based           │      Conf    : 88%  |  0.28s                   │
│  ☐ Stacked Queries       │                                                │
│  ☐ Out-of-Band           │  SCAN COMPLETE — Duration: 4.2s               │
│                          │  Tests: 38  |  Vulnerabilities: 4             │
│ [ ▶  START SCAN ]        │                                                │
│ [ ■  STOP       ]        │                                                │
│ [ ⬇  EXPORT JSON ]       │                                                │
└──────────────────────────┴───────────────────────────────────────────────┘
```

### Findings Tab
```
┌──────┬───────┬──────────────────────────────┬──────┬──────────────────────┐
│ SEV  │ PARAM │ TYPE                         │ CONF │ PAYLOAD              │
├──────┼───────┼──────────────────────────────┼──────┼──────────────────────┤
│ HIGH │ id    │ Error-Based SQLi             │  92% │ '                    │
│ HIGH │ id    │ Union-Based SQLi (Data Leak) │  88% │ ' UNION SELECT ...   │
│ MED  │ id    │ Boolean-Based Blind SQLi     │  65% │ ' AND '1'='1         │
│ MED  │ q     │ Time-Based Blind SQLi        │  78% │ ' AND SLEEP(2)--     │
└──────┴───────┴──────────────────────────────┴──────┴──────────────────────┘
```

---

## 🚀 Installation

**Zero dependencies.** Uses Python standard library only.

```bash
# Clone the repository
git clone https://github.com/yourusername/sqli-scanner-pro.git
cd sqli-scanner-pro

# Run directly — no pip install needed
python sql_injection_scanner.py
```

**Requirements:**
- Python 3.7+
- Tkinter (included with standard Python on Windows/macOS; on Linux: `sudo apt install python3-tk`)

---

## 🎯 Usage

### Quick Start with Demo Server

1. **Launch** the application — the built-in demo server starts automatically on `http://127.0.0.1:18321`
2. **Click a DEMO button** in the left panel to load a pre-configured vulnerable URL
3. **Click `[*] Auto-Detect Params`** to parse URL parameters
4. **Select injection categories** you want to test
5. **Click `[ ▶ START SCAN ]`** and watch results appear in real-time
6. **Switch to Findings tab** to review detected vulnerabilities
7. **Click `[ ⬇ EXPORT JSON ]`** to save findings

### Scanning a Custom Target

```
Target URL:  https://example.com/search?q=test&category=1
             ↓ Auto-Detect Params
Parameters:  ☑ q    ☑ category
             ↓ Select categories + click START
Results:     Real-time in Scan Log and Findings tabs
```

> **Always obtain written authorization before scanning any system you do not own.**

### Demo Endpoints (Built-in)

| Endpoint | Parameter | Vulnerability Type |
|---|---|---|
| `http://127.0.0.1:18321/user?id=1` | `id` | Error-Based SQLi |
| `http://127.0.0.1:18321/product?cat=1` | `cat` | Error-Based SQLi |
| `http://127.0.0.1:18321/search?q=test` | `q` | Union-Based SQLi |
| `http://127.0.0.1:18321/login?username=admin` | `username` | Boolean-Based SQLi |

---

## 💉 Injection Categories

| Category | Payloads | Detection Method |
|---|---|---|
| **Error-Based** | 15 | Triggers DB error messages exposing backend type/version |
| **Boolean-Based** | 10 | Compares TRUE vs FALSE response body length differences |
| **Time-Based** | 8 | Uses `SLEEP`/`WAITFOR` delays measured against baseline response time |
| **Union-Based** | 7 | Appends `UNION SELECT` to extract DB records directly into the response |
| **Stacked Queries** | 4 | Chains multiple SQL statements via semicolon injection |
| **Out-of-Band** | 3 | Leverages DNS/file-based channels for data exfiltration |

---

## 🧠 Detection Engine

The `ScannerEngine` class applies four independent detection strategies per payload:

```
┌─────────────────────────────────────────────────────────────┐
│                    DETECTION PIPELINE                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  HTTP Response Body                                          │
│       │                                                      │
│       ├── Error Signatures (30+ regex patterns)             │
│       │     MySQL · MSSQL · PostgreSQL · Oracle · SQLite    │
│       │     → Confidence: 92%  →  [HIGH]                    │
│       │                                                      │
│       ├── UNION Data Leak Detection                         │
│       │     Scans for leaked usernames/passwords/versions   │
│       │     → Confidence: 88%  →  [HIGH]                    │
│       │                                                      │
│       ├── Response Time Delta (Time-Based)                  │
│       │     Response > Baseline + 1.5s threshold            │
│       │     → Confidence: 78%  →  [MEDIUM]                  │
│       │                                                      │
│       └── Content Length Diff (Boolean-Based)               │
│             |TRUE_response| vs |FALSE_response| > 80 bytes  │
│             → Confidence: 65%  →  [MEDIUM/LOW]              │
└─────────────────────────────────────────────────────────────┘
```

### Severity Classification

| Badge | Confidence | Meaning |
|---|---|---|
| 🔴 **HIGH** | ≥ 85% | Direct data exposure or confirmed DB error. Remediate immediately. |
| 🟡 **MEDIUM** | 70–84% | Exploitable via blind technique. Requires further investigation. |
| 🔵 **LOW** | < 70% | Potential injection. Manual verification recommended. |

---

## 🏗️ Architecture

```
sql_injection_scanner.py
│
├── VulnerableHandler          # Built-in demo server (BaseHTTPRequestHandler)
│   ├── /user?id=              # Simulates MySQL error-based injection
│   ├── /product?cat=          # Simulates product category injection
│   ├── /search?q=             # Simulates UNION-exploitable search
│   └── /login?username=       # Simulates auth bypass injection
│
├── ScannerEngine              # Core detection logic
│   ├── fetch()                # HTTP requests via urllib (no requests lib)
│   ├── inject()               # URL parameter substitution
│   ├── check_errors()         # 30+ DB error regex signatures
│   └── scan_param()           # Per-parameter payload loop
│
└── App (Tkinter)              # Full GUI application
    ├── Banner                 # Live metrics: tests / vulns / status
    ├── Left Panel             # Target config, demo buttons, params, categories
    ├── Right Notebook         # Scan Log / Findings / Analysis tabs
    ├── Scan Worker Thread     # Daemon thread; pushes results to Queue
    ├── Demo Server Thread     # Daemon thread; serves localhost:18321
    └── drain_loop()           # Queue consumer; updates UI every 60ms
```

**Threading Model:**
```
Main Thread (Tkinter)  ←──── Queue ←──── Scan Worker Thread
                                               │
                       Demo Server Thread ─────┘
                       (socketserver, daemon)
```

---

## 📤 Output & Export

### JSON Export Format

```json
{
  "scan_date": "2025-01-15T14:32:07.441293",
  "target": "http://127.0.0.1:18321/user?id=1",
  "total_tests": 38,
  "vulnerabilities": [
    {
      "param": "id",
      "payload": "'",
      "category": "Error-Based",
      "status": 200,
      "elapsed": 0.321,
      "vulnerable": true,
      "vuln_type": "Error-Based SQLi",
      "confidence": 92,
      "details": "DB error: \"You have an error in your SQL syntax...\"",
      "url": "http://127.0.0.1:18321/user?id='",
      "body_len": 1247
    }
  ]
}
```

---

## 🛡️ Remediation Guide

If vulnerabilities are detected, apply the following fixes in order of priority:

```
1. ✅ USE PARAMETERIZED QUERIES (Prepared Statements)
      Never concatenate user input into SQL strings.
      -- Bad  → "SELECT * FROM users WHERE id = " + user_input
      -- Good → cursor.execute("SELECT * FROM users WHERE id = ?", (user_input,))

2. ✅ VALIDATE & SANITIZE ALL INPUTS
      Whitelist expected formats server-side (numeric IDs, alphanumeric fields).

3. ✅ LEAST-PRIVILEGE DATABASE ACCOUNTS
      App DB users must NOT have DROP, ALTER, FILE, or EXEC privileges.

4. ✅ DEPLOY A WEB APPLICATION FIREWALL (WAF)
      Use SQLi rulesets as a secondary defence layer.

5. ✅ SUPPRESS VERBOSE DB ERRORS
      Never expose raw database errors to end users. Log server-side only.

6. ✅ REGULAR SECURITY TESTING
      Run penetration tests and code reviews on all DB-facing components.
```

---

## 🏷️ Topics

`python` `sql-injection` `penetration-testing` `security-tools` `cybersecurity` `ethical-hacking` `tkinter` `gui` `vulnerability-scanner` `educational` `appsec` `infosec` `sqli` `web-security`

---

## ⚖️ Legal Disclaimer

```
╔══════════════════════════════════════════════════════════════════╗
║                    ⚠  LEGAL DISCLAIMER  ⚠                       ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  This tool is provided STRICTLY for educational purposes and     ║
║  authorized security testing ONLY.                               ║
║                                                                  ║
║  Using SQLi Scanner Pro against any system without EXPLICIT      ║
║  WRITTEN PERMISSION from the system owner is ILLEGAL and may     ║
║  result in criminal prosecution under computer fraud and         ║
║  abuse laws in your jurisdiction.                                ║
║                                                                  ║
║  The author accepts NO RESPONSIBILITY for misuse of this tool.   ║
║                                                                  ║
║  Always obtain proper written authorization before conducting    ║
║  any security assessment.                                        ║
╚══════════════════════════════════════════════════════════════════╝
```

---

<div align="center">

**Built for security education. Use responsibly.**

`[SQLi Scanner Pro]` · `Python 3` · `Zero Dependencies` · `Educational Use Only`

</div>
