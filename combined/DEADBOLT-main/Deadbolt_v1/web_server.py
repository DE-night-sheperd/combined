from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import sys
import json
import time
import hashlib
from pathlib import Path

# Add src directory to path
src_dir = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_dir)

app = Flask(__name__)
app.secret_key = os.environ.get('DEADBOLT_SECRET_KEY', 'deadbolt-dev-only-2025-change-this')

# Initialize Deadbolt modules
config_dir = Path.home() / '.deadlock'
config_dir.mkdir(parents=True, exist_ok=True)

# Initialize modules
try:
    # Add src to path first
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    from system_activity_monitor import SystemActivityMonitor
    activity_monitor = SystemActivityMonitor(config_dir)
    activity_monitor.start()
except Exception as e:
    print(f"⚠️  Warning: SystemActivityMonitor not found: {e}")
    import traceback
    traceback.print_exc()
    activity_monitor = None

try:
    from proxy_auth import ProxyAuthenticator
    proxy_auth = ProxyAuthenticator(config_dir)
except Exception as e:
    print(f"⚠️  Warning: ProxyAuthenticator not found: {e}")
    import traceback
    traceback.print_exc()
    proxy_auth = None

try:
    from security_monitor import DeadlockSecurityMonitor
    security_monitor = DeadlockSecurityMonitor()
except Exception as e:
    print(f"⚠️  Warning: DeadlockSecurityMonitor not found: {e}")
    import traceback
    traceback.print_exc()
    security_monitor = None

def get_admin_config():
    admin_config_file = config_dir / 'admin_config.json'
    if not admin_config_file.exists():
        default_config = {
            'admin_username': 'admin',
            'admin_password_hash': hashlib.sha256(b'DeadlockAdmin2024!').hexdigest(),
            'admin_enabled': True,
            'allowed_users': [
                {'username': 'admin', 'full_name': 'Deadlock Admin', 'role': 'Administrator', 'last_login': None, 'status': 'Active'}
            ]
        }
        with open(admin_config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        return default_config
    with open(admin_config_file, 'r') as f:
        return json.load(f)

def verify_password(username, password):
    config = get_admin_config()
    if config.get('admin_username') != username:
        return False
    input_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return input_hash == config.get('admin_password_hash')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/portal')
def portal():
    return render_template('sentinel_grid.html')

# --------------------------
# API Endpoints
# --------------------------
@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json or request.form
    username = data.get('username', '')
    password = data.get('password', '')
    if verify_password(username, password):
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/api/activity')
def api_activity():
    if activity_monitor:
        return jsonify({'activity': activity_monitor.get_activity_log(100)})
    else:
        return jsonify({'activity': []})

@app.route('/api/app_usage')
def api_app_usage():
    if activity_monitor:
        return jsonify(activity_monitor.get_app_usage_stats())
    else:
        return jsonify({})

@app.route('/api/proxy/status')
def api_proxy_status():
    if proxy_auth:
        return jsonify(proxy_auth.get_status())
    else:
        return jsonify({'enabled': False, 'proxy_server': None})

@app.route('/api/proxy/settings', methods=['POST'])
def api_proxy_settings():
    data = request.json or request.form
    if not proxy_auth:
        return jsonify({'success': False, 'message': 'Proxy auth not available'})
    
    if 'proxy_server' in data:
        proxy_auth.set_proxy_server(data['proxy_server'])
    if 'enable' in data:
        if data['enable']:
            proxy_auth.enable_proxy_auth()
        else:
            proxy_auth.disable_proxy_auth()
    
    return jsonify({'success': True, 'status': proxy_auth.get_status()})

@app.route('/api/users')
def api_users():
    config = get_admin_config()
    return jsonify({'users': config.get('allowed_users', [])})

@app.route('/api/security/alerts')
def api_security_alerts():
    # Generate sample alerts for demonstration
    sample_alerts = [
        {'id': 'ALRT-001', 'time': '14:32:15', 'type': 'Authentication', 'severity': 'INFO', 'description': 'Admin login successful', 'status': 'Active'},
        {'id': 'ALRT-002', 'time': '14:18:45', 'type': 'Threat', 'severity': 'LOW', 'description': 'Unusual network activity detected', 'status': 'Resolved'},
    ]
    return jsonify({'alerts': sample_alerts})

@app.route('/api/devices')
def api_devices():
    # Generate sample devices
    sample_devices = [
        {'device_id': 'DEV-001', 'name': 'Workstation A', 'os': 'Windows 11', 'last_seen': time.strftime('%Y-%m-%d %H:%M:%S'), 'status': 'Active'},
        {'device_id': 'DEV-002', 'name': 'Server B', 'os': 'Ubuntu 22.04', 'last_seen': time.strftime('%Y-%m-%d %H:%M:%S'), 'status': 'Active'},
    ]
    return jsonify({'devices': sample_devices})

@app.route('/api/threats')
def api_threats():
    # Generate sample threats
    sample_threats = [
        {'threat_id': 'THRT-001', 'type': 'Malware', 'severity': 'HIGH', 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'description': 'Unusual file modification detected', 'status': 'Open'},
        {'threat_id': 'THRT-002', 'type': 'Phishing', 'severity': 'MEDIUM', 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'description': 'Suspicious URL accessed', 'status': 'Closed'},
    ]
    return jsonify({'threats': sample_threats})

if __name__ == '__main__':
    print("🚀 Starting Deadbolt Unified Portal on http://127.0.0.1:5000")
    print("⚠️  This is a development server. For production, use a proper WSGI server.")
    app.run(debug=True, host='0.0.0.0', port=5000)
