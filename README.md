# Educational Web Security Training Laboratory (VulnLabs)

A modular, intentionally vulnerable web security training laboratory designed exclusively for authorized cybersecurity education and secure coding research. Built using **FastAPI**, **SQLite**, **Jinja2 templates**, **Tailwind CSS (Monochrome)**, **Playwright**, and **Docker**.

> [!IMPORTANT]
> **STRICTLY FOR EDUCATIONAL STUDY PURPOSES ONLY.**
> This software is intended solely for academic learning, vulnerability research, and defense mechanisms study. It contains intentionally flawed logic (SQLi, XSS, IDOR, CMDi, LFI, JWT, SSRF, SSTI, Race Conditions, XXE, Insecure Deserialization, Mass Assignment, CSRF, Open Redirect, CORS, Unrestricted Upload, Header Spoofing, Weak PRNG, API BOLA, DOM XSS, Reconnaissance) to demonstrate security impact and remediation patterns. Do not deploy to public untrusted networks or production environments.

---

## 📁 Project Architecture

```
.
├── docker-compose.yml              # Multi-container setup with isolated bridge network (lab-net)
├── Dockerfile                      # Python 3.11-slim with Chromium, Playwright, ping & flags
├── requirements.txt                # FastAPI, Uvicorn, Jinja2, PyJWT, HTTPX, Playwright
├── flag.txt                        # Root filesystem flags (CMDi & LFI)
├── labs.db                         # SQLite database (auto-seeded on startup)
├── test_lab.py                     # Automated 28-challenge verification test suite
├── internal_admin/                 # Isolated internal microservice (SSRF pivot target)
│   ├── Dockerfile
│   └── main.py                     # Listens on port 9000, returns internal secret flag
└── app/
    ├── __init__.py
    ├── main.py                     # App entry point, dashboard, flag submission engine, robots.txt
    ├── database.py                 # SQLite initialization, wallet schema & environment reset
    ├── flags.py                    # Central CTF challenge metadata & flag registry
    ├── docs/                       # Target documents for LFI exploration
    ├── labs/                       # 21 Modular vulnerability routers
    │   ├── sqli.py                 # Auth bypass, UNION exfiltration, Blind & Nested keyword bypass
    │   ├── xss.py                  # Reflected XSS, Stored Guestbook & Playwright Admin Bot
    │   ├── idor.py                 # Broken Object Level Authorization (Invoices)
    │   ├── cmdi.py                 # Network diagnostic OS command injection
    │   ├── lfi.py                  # Directory traversal & nested non-recursive strip bypass
    │   ├── jwt_lab.py              # JWT signature bypass & 'none' algorithm
    │   ├── ssrf.py                 # Internal microservice pivot & cloud metadata exfiltration
    │   ├── ssti.py                 # Jinja2 template injection & Python RCE
    │   ├── race.py                 # Concurrency TOCTOU coupon redemption glitch
    │   ├── xxe.py                  # XML External Entity injection
    │   ├── deserialization.py      # Python pickle insecure deserialization
    │   ├── mass_assignment.py      # Model binding & parameter tampering
    │   ├── csrf.py                 # Cross-Site Request Forgery state change
    │   ├── redirect.py             # Open URL redirection
    │   ├── cors.py                 # CORS arbitrary origin credential reflection
    │   ├── upload.py               # Unrestricted file upload & script storage
    │   ├── headers_lab.py          # Reverse proxy header spoofing & IP bypass
    │   ├── crypto_lab.py           # Weak time-seeded PRNG token prediction
    │   ├── api_lab.py              # API property exposure & BOLA
    │   ├── dom_lab.py              # DOM-based XSS execution sinks
    │   └── recon.py                # Crawler enumeration & concealed archive discovery
    ├── static/
    │   ├── css/style.css           # Minimalist Monochrome theme (IBM Plex Mono)
    │   └── js/lab.js               # 3-tab switcher (Hint / Vulnerable Source / How to Fix)
    └── templates/                  # Dark-mode educational web interface (rounded-md)
        ├── base.html               # Shared layout, navbar, live flag submit modal
        ├── index.html              # Central dashboard & curriculum tracker
        ├── sqli.html               # SQLi workspace (Auth, UNION, Blind, Nested Filter)
        ├── xss.html                # XSS workspace with Playwright Bot trigger
        ├── idor.html               # IDOR workspace with 3-tab secure code comparison
        ├── cmdi.html               # CMDi terminal with 3-tab secure code comparison
        ├── lfi.html                # LFI reader & nested traversal bypass
        ├── jwt.html                # JWT attack workbench
        ├── ssrf.html               # SSRF workbench (Internal Pivot & Cloud Metadata)
        ├── ssti.html               # SSTI custom badge generator
        ├── race.html               # Race condition wallet balance & exploit helper
        ├── xxe.html                # XXE order parser workbench
        ├── deserialization.html    # Pickle session loader workbench
        ├── mass_assignment.html    # Profile mass assignment editor
        ├── csrf.html               # CSRF account action simulator
        ├── redirect.html           # Open redirect gateway tester
        ├── cors.html               # CORS preflight & credential header inspector
        ├── upload.html             # Unrestricted file repository
        ├── headers.html            # Upstream proxy header evaluator
        ├── crypto.html             # Weak PRNG token prediction workbench
        ├── api.html                # REST API property exposure viewer
        ├── dom.html                # DOM XSS client execution sink
        └── recon.html              # Asset discovery & robots exclusion probe
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

Run automated checks across all 28 vulnerability paths and flag verification:
```bash
python test_lab.py
```

---

## 🎯 Challenge Matrix & Flag Registry (28 Exercises)

| ID | Category | Title | Difficulty | Target Route | Flag |
|---|---|---|---|---|---|
| `sqli-auth` | SQLi | Login Bypass | Introductory | `POST /labs/sqli/login` | `FLAG{sqli_auth_bypass_login_pwned_8192}` |
| `sqli-union` | SQLi | UNION Exfiltration | Intermediate | `GET /labs/sqli?q=` | `FLAG{sqli_union_db_extraction_7719}` |
| `sqli-blind` | SQLi | Boolean Blind Inference | Advanced | `GET /labs/sqli#blind-check` | `FLAG{blind_sqli_boolean_extraction_9102}` |
| `sqli-nested` | SQLi | Nested Keyword Filter Bypass | Advanced | `GET /labs/sqli#nested-filter` | `FLAG{nested_keyword_filter_bypass_3310}` |
| `xss-reflected` | XSS | Reflected Injection | Introductory | `GET /labs/xss?q=` | `FLAG{r3fl3ct3d_xss_c00k13_st0l3n_4421}` |
| `xss-stored` | XSS | Stored Guestbook | Intermediate | `POST /labs/xss/guestbook` | `FLAG{st0r3d_xss_p3rs1st3nt_p4yl04d_5532}` |
| `xss-bot` | XSS | Playwright Admin Bot | Advanced | `POST /labs/xss/report` | `FLAG{xss_stole_admin_cookie}` |
| `idor` | Access Control | Invoice Enumeration | Introductory | `GET /labs/idor?receipt_id=` | `FLAG{1d0r_privilege_escalation_view_secret_3301}` |
| `cmdi` | OS Execution | Diagnostic Ping | Advanced | `POST /labs/cmdi/ping` | `FLAG{c0mm4nd_1nj3ct10n_r00t_sh3ll_9824}` |
| `lfi` | Path Traversal | Arbitrary File Reader | Intermediate | `GET /labs/lfi?file=` | `FLAG{p4th_tr4v3rs4l_lfi_r34d_syst3m_f1l3s_1048}` |
| `lfi-nested` | Path Traversal | Nested Non-Recursive Strip Bypass | Advanced | `GET /labs/lfi#nested-traversal` | `FLAG{nested_traversal_non_recursive_bypass_5591}` |
| `jwt` | Authentication | Signature Verification Bypass | Intermediate | `POST /labs/jwt/admin-vault` | `FLAG{jwt_broken_verification_admin_3389}` |
| `ssrf` | SSRF | Internal Network Pivoting | Advanced | `POST /labs/ssrf/check-url` | `FLAG{ssrf_internal_pivot_pwned_9941}` |
| `ssrf-metadata` | SSRF | Cloud Metadata Exfiltration | Advanced | `POST /labs/ssrf/check-metadata` | `FLAG{ssrf_cloud_metadata_credential_leak_6631}` |
| `ssti` | SSTI | Jinja2 Template Injection RCE | Advanced | `POST /labs/ssti/render` | `FLAG{ssti_jinja2_template_rce_8812}` |
| `race` | Concurrency | TOCTOU Coupon Redemption | Advanced | `POST /labs/race/redeem` | `FLAG{race_condition_toctou_balance_glitch_4011}` |
| `xxe` | XML Injection | XML External Entity Injection | Advanced | `POST /labs/xxe/parse` | `FLAG{xxe_external_entity_disclosure_7261}` |
| `deserialization` | Deserialization | Insecure Object Unpickling | Advanced | `POST /labs/deserialization/load` | `FLAG{insecure_pickle_deserialization_rce_5541}` |
| `mass-assignment` | Parameter Binding | Privilege Escalation | Intermediate | `POST /labs/mass-assignment/profile` | `FLAG{mass_assignment_privilege_escalation_1289}` |
| `csrf` | Session Integrity | Cross-Site Request Forgery | Intermediate | `POST /labs/csrf/change-email` | `FLAG{csrf_state_changing_action_pwned_4431}` |
| `open-redirect` | Input Validation | Arbitrary Target Forwarding | Introductory | `GET /labs/redirect?url=` | `FLAG{open_redirect_phishing_vector_6021}` |
| `cors` | Origin Policy | Insecure Origin Trust | Intermediate | `GET /labs/cors/api/account-keys` | `FLAG{cors_arbitrary_origin_credential_leak_3391}` |
| `upload` | File Handling | Unrestricted Extension Verification | Intermediate | `POST /labs/upload` | `FLAG{unrestricted_file_upload_stored_xss_8820}` |
| `headers-spoof` | Network Boundaries | Trust Boundary Bypass | Introductory | `GET /labs/headers/admin-panel` | `FLAG{header_spoofing_client_ip_bypass_4102}` |
| `crypto-weak` | Cryptography | Predictable Token Generation | Intermediate | `POST /labs/crypto/verify-token` | `FLAG{weak_prng_predictable_token_7734}` |
| `bola-api` | API Security | Property-Level Exposure | Introductory | `GET /labs/api-security/api/v1/users/` | `FLAG{bola_api_sensitive_field_exposure_5519}` |
| `dom-xss` | Client-Side Injection | Client Execution Sink | Intermediate | `GET /labs/dom-xss?nickname=` | `FLAG{dom_xss_execution_sink_untrusted_source_9918}` |
| `recon-hidden` | Information Disclosure | Crawler Governance & Robots Disclosure | Introductory | `GET /labs/recon` | `FLAG{recon_hidden_robots_path_disclosure_1982}` |
