import os
import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent
DB_PATH = DB_DIR / "labs.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        secret_flag TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receipts (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        title TEXT NOT NULL,
        amount TEXT NOT NULL,
        is_private INTEGER DEFAULT 0,
        details TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS guestbook (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT NOT NULL,
        comment TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wallets (
        user_id INTEGER PRIMARY KEY,
        balance REAL NOT NULL DEFAULT 10.0,
        coupon_used INTEGER NOT NULL DEFAULT 0,
        flag_purchased INTEGER NOT NULL DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS profile_users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        bio TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS csrf_accounts (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        balance REAL NOT NULL DEFAULT 500.0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        role TEXT NOT NULL,
        is_internal INTEGER DEFAULT 0,
        secret_key TEXT NOT NULL,
        secret_flag TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS uploads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        original_name TEXT NOT NULL,
        content_type TEXT NOT NULL,
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        users = [
            (
                1,
                "admin",
                "p@ssw0rd_sup3r_s3cr3t_9921",
                "administrator",
                "FLAG{sqli_union_db_extraction_7719}",
            ),
            (2, "alice", "alice123", "analyst", "alice_confidential_notes_882"),
            (3, "bob", "hunter2", "developer", "bob_personal_diary_911"),
            (4, "charlie", "welcome2026", "auditor", "charlie_audit_logs_003"),
            (
                5,
                "system_flag",
                "sec_token_9102",
                "service",
                "FLAG{blind_sqli_boolean_extraction_9102}",
            ),
        ]
        cursor.executemany(
            "INSERT INTO users (id, username, password, role, secret_flag) VALUES (?, ?, ?, ?, ?)",
            users,
        )

    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()[0] == 0:
        products = [
            (
                1,
                "CyberShield NextGen Firewall",
                "Hardware",
                1299.99,
                "Enterprise rackmount appliance with real-time deep packet inspection.",
            ),
            (
                2,
                "Red Team Penetration Toolkit",
                "Software",
                499.50,
                "Automated reconnaissance and payload delivery orchestration suite.",
            ),
            (
                3,
                "Encrypted IronKey 128GB",
                "Hardware",
                89.99,
                "Military-grade AES-256 hardware encrypted portable storage.",
            ),
            (
                4,
                "Zero-Trust Access Gateway",
                "Networking",
                849.00,
                "Secure enclave broker supporting WireGuard and mTLS authentication.",
            ),
            (
                5,
                "Security Operations Center License",
                "Cloud",
                2100.00,
                "Annual SIEM event ingestion license with heuristic anomaly alarms.",
            ),
        ]
        cursor.executemany(
            "INSERT INTO products (id, name, category, price, description) VALUES (?, ?, ?, ?, ?)",
            products,
        )

    cursor.execute("SELECT COUNT(*) FROM receipts")
    if cursor.fetchone()[0] == 0:
        receipts = [
            (
                101,
                2,
                "Alice Cooper",
                "Invoice #101: Hardware Security Appliance",
                "$1,299.99",
                0,
                "Purchased by Alice Cooper for SOC Lab Deployment. Shipping confirmed.",
            ),
            (
                102,
                2,
                "Alice Cooper",
                "Invoice #102: Encrypted Storage Keys",
                "$89.99",
                0,
                "Purchased by Alice Cooper. Hand delivered to secure archive.",
            ),
            (
                103,
                3,
                "Bob Miller",
                "Invoice #103: Network Gateway Setup",
                "$849.00",
                0,
                "Purchased by Bob Miller for engineering home lab infrastructure.",
            ),
            (
                1337,
                1,
                "Executive Defense Directorate",
                "Invoice #1337: Red Team Zero-Day Assessment (CONFIDENTIAL)",
                "$45,000.00",
                1,
                "CLASSIFIED EXECUTIVE BRIEFING: Zero-day vulnerability discovery retainer. Secret clearance verification: FLAG{1d0r_privilege_escalation_view_secret_3301}",
            ),
        ]
        cursor.executemany(
            "INSERT INTO receipts (id, user_id, customer_name, title, amount, is_private, details) VALUES (?, ?, ?, ?, ?, ?, ?)",
            receipts,
        )

    cursor.execute("SELECT COUNT(*) FROM guestbook")
    if cursor.fetchone()[0] == 0:
        guestbook_entries = [
            (
                "Security Officer",
                "Internal discussion board. Please post questions responsibly.",
                "2026-11-10 09:30:00",
            ),
            (
                "DevOps Engineer",
                "System maintenance scheduled for this Saturday at 02:00 UTC.",
                "2026-11-12 14:15:00",
            ),
        ]
        cursor.executemany(
            "INSERT INTO guestbook (author, comment, created_at) VALUES (?, ?, ?)",
            guestbook_entries,
        )

    cursor.execute("SELECT COUNT(*) FROM wallets")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO wallets (user_id, balance, coupon_used, flag_purchased) VALUES (1, 10.0, 0, 0)"
        )

    cursor.execute("SELECT COUNT(*) FROM profile_users")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO profile_users (id, username, email, role, bio) VALUES (1, 'student', 'student@academy.local', 'student', 'Cybersecurity trainee')"
        )

    cursor.execute("SELECT COUNT(*) FROM csrf_accounts")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO csrf_accounts (id, username, email, balance) VALUES (1, 'victim_user', 'victim@company.local', 500.0)"
        )

    cursor.execute("SELECT COUNT(*) FROM api_users")
    if cursor.fetchone()[0] == 0:
        api_users = [
            (
                1,
                "admin_service",
                "svc-admin@internal.local",
                "administrator",
                1,
                "k_sec_99182312",
                "FLAG{bola_api_sensitive_field_exposure_5519}",
            ),
            (
                2,
                "guest_user",
                "guest@internal.local",
                "viewer",
                0,
                "k_pub_10293847",
                "NONE",
            ),
        ]
        cursor.executemany(
            "INSERT INTO api_users (id, username, email, role, is_internal, secret_key, secret_flag) VALUES (?, ?, ?, ?, ?, ?, ?)",
            api_users,
        )

    conn.commit()
    conn.close()


def reset_lab_environment():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS products")
    cursor.execute("DROP TABLE IF EXISTS receipts")
    cursor.execute("DROP TABLE IF EXISTS guestbook")
    cursor.execute("DROP TABLE IF EXISTS wallets")
    cursor.execute("DROP TABLE IF EXISTS profile_users")
    cursor.execute("DROP TABLE IF EXISTS csrf_accounts")
    cursor.execute("DROP TABLE IF EXISTS api_users")
    cursor.execute("DROP TABLE IF EXISTS uploads")
    conn.commit()
    conn.close()
    init_db()
