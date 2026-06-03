from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import sys
import json
import time
from pathlib import Path
import hashlib

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from security_utils import SecurityUtils
from device_fingerprint import get_device_fingerprint
from system_activity_monitor import SystemActivityMonitor
from proxy_auth import ProxyAuthenticator

app = Flask(__name__)
app.secret_key = "deadlock_secret_key_change_this_in_production"

# Initialize Deadlock modules
config_dir = Path.home() / ".deadlock"
config_dir.mkdir(parents=True, exist_ok=True)
activity_monitor = SystemActivityMonitor(config_dir)
proxy_auth = ProxyAuthenticator(config_dir)

# Admin authentication helpers
def get_admin_config():
    admin_config_file = config_dir / "admin_config.json"
    if not admin_config_file.exists():
        default_config = {
            "admin_username": "admin",
            "admin_password_hash": hashlib.sha256(b"DeadlockAdmin2024!").hexdigest(),
            "admin_enabled": True,
            "allowed_users": []
        }
        with open(admin_config_file, "w") as f:
            json.dump(default_config, f, indent=2)
        return default_config
    with open(admin_config_file, "r") as f:
        return json.load(f)

def verify_password(username, password):
    config = get_admin_config()
    if config.get("admin_username") != username:
        return False
    input_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return input_hash == config.get("admin_password_hash")

# Routes
@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if verify_password(username, password):
            # Set a simple session (in production use a proper session manager)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password!", "danger")
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    system_info = {
        "os": os.name,
        "hostname": get_device_fingerprint().get("hostname", "Unknown"),
        "ip_address": get_device_fingerprint().get("ip_addresses", ["Unknown"])[0],
        "uptime": "Not implemented yet"
    }
    
    security_score = 720  # Default score, can be expanded
    
    return render_template("dashboard.html", system_info=system_info, security_score=security_score)

@app.route("/activity")
def activity():
    activity_log = activity_monitor.get_activity_log(200)
    return render_template("activity.html", activity_log=activity_log)

@app.route("/app-usage")
def app_usage():
    usage_stats = activity_monitor.get_app_usage_stats()
    sorted_apps = sorted(usage_stats.items(), key=lambda x: x[1]["duration"], reverse=True)
    return render_template("app_usage.html", usage_stats=sorted_apps)

@app.route("/proxy-settings", methods=["GET", "POST"])
def proxy_settings():
    if request.method == "POST":
        if "toggle" in request.form:
            if proxy_auth.get_status()["enabled"]:
                proxy_auth.disable_proxy_auth()
            else:
                proxy_auth.enable_proxy_auth()
            flash("Proxy authentication status updated!", "success")
        elif "server" in request.form:
            new_server = request.form["proxy_server"]
            proxy_auth.set_proxy_server(new_server)
            flash(f"Proxy server set to {new_server}!", "success")
        elif "test" in request.form:
            success, msg = proxy_auth.authenticate_with_proxy()
            if success:
                flash("Proxy authentication test successful!", "success")
            else:
                flash(f"Proxy authentication test failed: {msg}", "danger")
    
    return render_template("proxy_settings.html", proxy_status=proxy_auth.get_status())

@app.route("/api/activity")
def api_activity():
    return jsonify({"activity": activity_monitor.get_activity_log(50)})

@app.route("/api/app-usage")
def api_app_usage():
    return jsonify(activity_monitor.get_app_usage_stats())

if __name__ == "__main__":
    print("🚀 Starting Deadlock Web Dashboard on http://127.0.0.1:5000")
    activity_monitor.start()
    try:
        app.run(debug=True, use_reloader=False)
    finally:
        activity_monitor.stop()
