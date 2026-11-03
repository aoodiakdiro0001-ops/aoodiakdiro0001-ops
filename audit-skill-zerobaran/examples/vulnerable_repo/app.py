# INTENTIONALLY VULNERABLE sample file — used only as a test fixture for
# Audit-Skill-ZeroBaran (Project #35, Baran Avisat). DO NOT copy into real code.
import os, pickle, hashlib, subprocess, requests
from flask import Flask, request, render_template_string

API_KEY = "sk-proj-aBcDeF1234567890abcdefGHIJKLmnop"
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
db_password = "Sup3rS3cretP@ss2026!"

app = Flask(__name__)
app.run(debug=True)

def get_user(cursor, user_id):
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")   # SQLi
    return cursor.fetchone()

def run_backup(name):
    os.system("tar czf /backups/" + name + ".tgz /data")          # OS command injection

def load_model(blob):
    return pickle.loads(blob)                                     # unsafe deserialization

def hash_pwd(p):
    return hashlib.md5(p.encode()).hexdigest()                    # weak crypto

def fetch(url):
    return requests.get(url, verify=False).text                   # TLS validation off

@app.route("/greet")
def greet():
    tpl = "<h1>Hello %s</h1>" % request.args.get("name", "")
    return render_template_string(tpl)                            # SSTI

def calc(expr):
    return eval(expr)                                             # dynamic eval
