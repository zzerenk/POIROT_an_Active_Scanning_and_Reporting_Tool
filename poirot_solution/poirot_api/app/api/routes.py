from flask import Blueprint, request, jsonify, render_template # <--- render_template EKLENDİ
from app.core.scanner import NmapScanner
import threading
import uuid
import time

# Blueprint tanımlıyoruz
api = Blueprint('api', __name__)

# Geçici Hafıza (Task Listesi)
SCAN_TASKS = {}

# --- 1. EKSİK OLAN PARÇA: ANA SAYFA ROTASI ---
@api.route('/')
def index():
    # Tarayıcı siteye girince home.html'i gösterir
    return render_template('pages/home.html')


# --- 2. ASENKRON İŞÇİ (Arka Plan Görevi) ---
def run_scan_in_background(task_id, target, options):
    scanner = NmapScanner()
    
    # Build detailed status message based on enabled options
    scan_features = []
    if options.get('serviceVersion'):
        scan_features.append('Service Detection')
    if options.get('detectOS'):
        scan_features.append('OS Fingerprinting')
    if options.get('vulnScan'):
        scan_features.append('Vulnerability Scanning')
    if options.get('subdomainScan'):
        scan_features.append('Subdomain Discovery')
    
    features_text = ', '.join(scan_features) if scan_features else 'Basic Port Scan'
    
    SCAN_TASKS[task_id]['status'] = 'running'
    SCAN_TASKS[task_id]['message'] = f'[NMAP] Initializing scan with: {features_text}'
    SCAN_TASKS[task_id]['progress'] = 10
    
    try:
        # Update status before scan
        SCAN_TASKS[task_id]['message'] = f'[NMAP] Executing scan on {target}...'
        SCAN_TASKS[task_id]['progress'] = 30
        
        # Taramayı Yap
        result = scanner.scan_target(target, options)
        
        # Update status after scan completes
        SCAN_TASKS[task_id]['message'] = '[PARSER] Processing scan results...'
        SCAN_TASKS[task_id]['progress'] = 80
        
        # Bitiş Durumu
        SCAN_TASKS[task_id]['status'] = 'completed'
        SCAN_TASKS[task_id]['message'] = f'[COMPLETE] Scan finished. Results ready.'
        SCAN_TASKS[task_id]['progress'] = 100
        SCAN_TASKS[task_id]['result'] = result

    except Exception as e:
        SCAN_TASKS[task_id]['status'] = 'failed'
        SCAN_TASKS[task_id]['message'] = f'[ERROR] Scan failed: {str(e)}'
        SCAN_TASKS[task_id]['progress'] = 0


# --- 3. API ENDPOINTLERİ (Başlarına /api ekledik) ---

@api.route('/api/scan', methods=['POST']) # <--- Adres /api/scan oldu
def start_scan():
    data = request.get_json()
    target = data.get('target')
    options = data.get('options', {})

    if not target:
        return jsonify({"success": False, "error": "Hedef belirtilmedi"}), 400

    task_id = str(uuid.uuid4())
    
    SCAN_TASKS[task_id] = {
        'status': 'pending',
        'message': 'Sıraya alındı...',
        'progress': 0,
        'result': None
    }

    thread = threading.Thread(target=run_scan_in_background, args=(task_id, target, options))
    thread.start()

    return jsonify({"success": True, "task_id": task_id})

@api.route('/api/status/<task_id>', methods=['GET']) # <--- Adres /api/status/... oldu
def check_status(task_id):
    task = SCAN_TASKS.get(task_id)
    
    if not task:
        return jsonify({"success": False, "error": "Böyle bir görev bulunamadı"}), 404
        
    return jsonify(task)