# Intentionally Vulnerable Web Security Training Lab v2.0 (CTF Edition)

A modular, hands-on, intentionally vulnerable web security training lab designed for Capture The Flag (CTF) practice and secure coding training. Built using **FastAPI**, **SQLite**, **Jinja2 templates**, **Tailwind CSS (Monochrome)**, **Playwright**, and **Docker (Multi-Container Bridge)**.

> [!WARNING]
> **STRICTLY FOR AUTHORIZED EDUCATIONAL & CTF TRAINING PURPOSES.**
> This application contains intentionally insecure code vulnerable to critical attacks (RCE, SQLi, IDOR, XSS, LFI, SSRF, SSTI, Race Conditions, JWT forgery). Never deploy this application onto public networks or untrusted production environments. The Docker setup binds exclusively to the local loopback interface (`127.0.0.1:8080:8000`).

---

## 📁 Project Architecture

```
.
├── docker-compose.yml              # Multi-container setup with isolated bridge network (lab-net)
├── Dockerfile                      # Python 3.11-slim with Chromium, Playwright, ping & flags
├── requirements.txt                # FastAPI, Uvicorn, Jinja2, PyJWT, HTTPX, Playwright
├── flag.txt                        # Root filesystem flags (CMDi & LFI)
├── labs.db                         # SQLite database (auto-seeded on startup)
├── test_v2.py                      # Automated end-to-end verification test suite
├── internal_admin/                 # Isolated internal microservice (SSRF pivot target)
│   ├── Dockerfile
│   └── main.py                     # Listens on port 9000, returns internal secret flag
└── app/
    ├── __init__.py
    ├── main.py                     # App entry point, dashboard, flag submission engine
    ├── database.py                 # SQLite initialization, wallet schema & environment reset
    ├── flags.py                    # Central CTF challenge metadata & flag registry
    ├── docs/                       # Target documents for LFI exploration
    ├── labs/                       # Modular vulnerability routers
    │   ├── __init__.py
    │   ├── sqli.py                 # Auth bypass & UNION exfiltration
    │   ├── xss.py                  # Reflected XSS, Stored Guestbook & Playwright Admin Bot
    │   ├── idor.py                 # Broken Object Level Authorization (Invoices)
    │   ├── cmdi.py                 # Network diagnostic OS command injection
    │   ├── lfi.py                  # Directory traversal & file inclusion
    │   ├── jwt_lab.py              # JWT signature bypass & 'none' algorithm
    │   ├── ssrf.py                 # URL preview checker & internal pivoting
    │   ├── ssti.py                 # Jinja2 template injection & Python RCE
    │   └── race.py                 # Concurrency TOCTOU coupon redemption glitch
    ├── static/
    │   ├── css/style.css           # Minimalist Monochrome theme (IBM Plex Mono)
    │   └── js/lab.js               # 3-tab switcher (Hint / Vulnerable Source / How to Fix)
    └── templates/                  # Dark-mode CTF web interface
        ├── base.html               # Shared layout, navbar, live flag submit modal
        ├── index.html              # Central CTF dashboard & score tracker
        ├── sqli.html               # SQLi workspace with 3-tab secure code comparison
        ├── xss.html                # XSS workspace with Playwright Bot trigger
        ├── idor.html               # IDOR workspace with 3-tab secure code comparison
        ├── cmdi.html               # CMDi terminal with 3-tab secure code comparison
        ├── lfi.html                # LFI reader with 3-tab secure code comparison
        ├── jwt.html                # JWT attack workbench
        ├── ssrf.html               # SSRF preview workbench & pivot target
        ├── ssti.html               # SSTI custom badge generator
        └── race.html               # Race condition wallet balance & exploit helper
```

---

## 🚀 Quick Start Guide

### Option 1: Multi-Container Docker Compose (Recommended)

1. **Build and launch the lab in detached mode:**
   ```bash
   docker compose up --build -d
   ```
2. **Access the web interface:**
   Navigate to [http://127.0.0.1:8080](http://127.0.0.1:8080) in your web browser.

3. **Stop the lab:**
   ```bash
   docker compose down
   ```

---

### Option 2: Local Python Execution

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Start the FastAPI server:**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access the dashboard:**
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) (or `http://<your-lan-ip>:8000` for lab peers).

---

### Option 3: Automated Verification Suite

Run automated checks across all 12 vulnerability paths and flag verification:
```bash
python test_v2.py
```

---

## 🎯 Challenge Matrix & Flag Registry

| ID | Category | Title | Difficulty | Target Route | Flag |
|---|---|---|---|---|---|
| `sqli-auth` | SQLi | Login Bypass | Introductory | `POST /labs/sqli/login` | `FLAG{sqli_auth_bypass_login_pwned_8192}` |
| `sqli-union` | SQLi | UNION Exfiltration | Intermediate | `GET /labs/sqli?q=` | `FLAG{sqli_union_db_extraction_7719}` |
| `xss-reflected` | XSS | Reflected Injection | Introductory | `GET /labs/xss?q=` | `FLAG{r3fl3ct3d_xss_c00k13_st0l3n_4421}` |
| `xss-stored` | XSS | Stored Guestbook | Intermediate | `POST /labs/xss/guestbook` | `FLAG{st0r3d_xss_p3rs1st3nt_p4yl04d_5532}` |
| `xss-bot` | XSS | Playwright Admin Bot | Advanced | `POST /labs/xss/report` | `FLAG{xss_stole_admin_cookie}` |
| `idor` | Access Control | Invoice Enumeration | Introductory | `GET /labs/idor?receipt_id=` | `FLAG{1d0r_privilege_escalation_view_secret_3301}` |
| `cmdi` | OS Execution | Diagnostic Ping | Advanced | `POST /labs/cmdi/ping` | `FLAG{c0mm4nd_1nj3ct10n_r00t_sh3ll_9824}` |
| `lfi` | Path Traversal | Arbitrary File Reader | Intermediate | `GET /labs/lfi?file=` | `FLAG{p4th_tr4v3rs4l_lfi_r34d_syst3m_f1l3s_1048}` |
| `jwt` | Authentication | Signature Verification Bypass | Intermediate | `POST /labs/jwt/admin-vault` | `FLAG{jwt_broken_verification_admin_3389}` |
| `ssrf` | SSRF | Internal Network Pivoting | Advanced | `POST /labs/ssrf/check-url` | `FLAG{ssrf_internal_pivot_pwned_9941}` |
| `ssti` | SSTI | Jinja2 Template Injection RCE | Advanced | `POST /labs/ssti/render` | `FLAG{ssti_jinja2_template_rce_8812}` |
| `race` | Concurrency | TOCTOU Coupon Redemption | Advanced | `POST /labs/race/redeem` | `FLAG{race_condition_toctou_balance_glitch_4011}` |

---

## 🛠️ Exploit Walkthroughs & Remediation Guide

### 1. JWT Attacks (`/labs/jwt`)
- **Vulnerability:** Server calls `jwt.decode(token, options={"verify_signature": False})`.
- **Exploitation:**
  1. Base64url-decode payload `{"sub": "guest", "role": "user"}`.
  2. Change `"role": "admin"`, re-encode to Base64url.
  3. Submit forged token to `/labs/jwt/admin-vault` to capture flag.
- **Remediation:** Enforce cryptographic signature verification: `jwt.decode(token, key=SECRET, algorithms=["HS256"], options={"verify_signature": True})`.

### 2. SSRF & Internal Pivoting (`/labs/ssrf`)
- **Vulnerability:** Unconstrained server-side HTTP GET requests without IP/hostname allowlisting.
- **Exploitation:** Target the isolated microservice on the Docker bridge: `http://internal-admin:9000/secret-flag`.
- **Remediation:** Validate URLs using `socket.gethostbyname()`, block private/loopback RFC1918 ranges with `ipaddress.is_private`, and disable redirects.

### 3. Server-Side Template Injection (`/labs/ssti`)
- **Vulnerability:** `jinja2.Environment().from_string(f"...{user_input}...").render()`.
- **Exploitation:**
  - Expression test: `{{ 7 * 7 }}` -> evaluates to `49`.
  - Context leak: `{{ SYSTEM_FLAG }}` -> leaks flag.
  - Python RCE: `{{ self.__init__.__globals__.__builtins__.__import__('os').popen('cat flag.txt').read() }}`.
- **Remediation:** Never format user input into template strings. Pass input as context variables (`env.from_string("...{{ name }}...").render(name=name)`) with `autoescape=True`.

### 4. Race Condition / TOCTOU (`/labs/race`)
- **Vulnerability:** 200ms `asyncio.sleep(0.2)` window between checking `coupon_used == 0` and updating balance without database row locks.
- **Exploitation:** Blast 6-8 concurrent asynchronous POST requests with coupon code `FREE10` to push balance over $50.00, then purchase the elite flag.
- **Remediation:** Use atomic conditional SQL updates: `UPDATE wallets SET balance = balance + 10.0, coupon_used = 1 WHERE user_id = 1 AND coupon_used = 0;` and check `cursor.rowcount`.

### 5. Playwright Active Admin Bot (`/labs/xss`)
- **Workflow:** When "Report Page to Admin" is clicked, headless Chromium visits the guestbook carrying a secret non-HttpOnly cookie (`admin_session=FLAG{xss_stole_admin_cookie}`).
- **Remediation:** Remove `| safe` filters to allow Jinja2 contextual HTML entity escaping, sanitize rich inputs with `nh3`, and mark cookies `HttpOnly=True; Secure; SameSite=Strict`.
