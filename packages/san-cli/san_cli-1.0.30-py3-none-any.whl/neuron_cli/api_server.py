#!/usr/bin/env python3
"""
SAN CLI API Server - HTTP API wrapper for SAN CLI commands

This server runs on the host machine and provides HTTP endpoints
for SPACE Agent and other services to interact with SAN CLI.

Features:
- Dynamic port allocation (8099-8199)
- Service announcement via /var/run/san-cli-api.json
- Rich telemetry and package inventory
- Health monitoring
- Offline job queue with callbacks
"""

import os
import sys
import json
import time
import socket
import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS

from .version import __version__
from .marketplace.manager import MarketplaceManager
from .core.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('/tmp/san-cli-api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global state
start_time = time.time()
current_port = None
job_queue = []  # Offline job queue
config = Config()
marketplace = MarketplaceManager()


def find_free_port(start=8099, end=8199) -> int:
    """Find a free port in the given range (inclusive)"""
    for port in range(start, end + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('', port))
            sock.close()
            logger.info(f"✅ Found free port: {port}")
            return port
        except OSError:
            continue
    raise RuntimeError(f"No free ports available in range {start}-{end}")


def get_installed_packages() -> List[Dict]:
    """Get list of installed marketplace packages"""
    try:
        packages = marketplace.list_installed()
        return [
            {
                "name": pkg.get("name"),
                "version": pkg.get("version"),
                "status": pkg.get("status", "unknown"),
                "type": pkg.get("type"),
            }
            for pkg in packages
        ]
    except Exception as e:
        logger.error(f"Failed to get installed packages: {e}")
        return []


def get_system_info() -> Dict:
    """Get system information"""
    import platform
    return {
        "platform": platform.system().lower(),
        "arch": platform.machine().lower(),
        "python_version": platform.python_version(),
        "hostname": socket.gethostname(),
    }


def update_announcement():
    """Update announcement file periodically (every 30 seconds)"""
    announcement_path = "/var/run/san-cli-api.json"
    
    # Try /var/run first, fall back to /tmp if permission denied
    try:
        Path("/var/run").mkdir(parents=True, exist_ok=True)
    except PermissionError:
        announcement_path = "/tmp/san-cli-api.json"
        logger.warning("Cannot write to /var/run, using /tmp instead")
    
    while True:
        try:
            announcement = {
                "service": "san-cli-api",
                "port": current_port,
                "status": "alive",
                "pid": os.getpid(),
                "version": __version__,
                "timestamp": int(time.time()),
                "health": {
                    "uptime_seconds": int(time.time() - start_time),
                    "last_heartbeat": int(time.time())
                },
                "installed_packages": get_installed_packages(),
                "system_info": get_system_info(),
                "capabilities": [
                    "marketplace_install",
                    "marketplace_uninstall",
                    "marketplace_update",
                    "marketplace_list",
                    "system_info",
                    "health_check"
                ],
                "job_queue_size": len(job_queue)
            }
            
            with open(announcement_path, 'w') as f:
                json.dump(announcement, f, indent=2)
            
            logger.debug(f"📡 Updated announcement: {len(get_installed_packages())} packages")
        except Exception as e:
            logger.error(f"Failed to update announcement: {e}")
        
        time.sleep(30)


# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "uptime_seconds": int(time.time() - start_time),
        "version": __version__,
        "timestamp": int(time.time())
    })


@app.route('/api/v1/info', methods=['GET'])
def get_info():
    """Get service information"""
    return jsonify({
        "service": "san-cli-api",
        "version": __version__,
        "port": current_port,
        "uptime_seconds": int(time.time() - start_time),
        "installed_packages": get_installed_packages(),
        "system_info": get_system_info(),
        "capabilities": [
            "marketplace_install",
            "marketplace_uninstall",
            "marketplace_update",
            "marketplace_list",
            "system_info",
            "health_check"
        ]
    })


@app.route('/api/v1/marketplace/list', methods=['GET'])
def list_packages():
    """List installed marketplace packages"""
    try:
        packages = get_installed_packages()
        return jsonify({
            "success": True,
            "packages": packages,
            "count": len(packages)
        })
    except Exception as e:
        logger.error(f"Failed to list packages: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/v1/marketplace/install', methods=['POST'])
def install_package():
    """Install a marketplace package"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid JSON request body"
            }), 400
        
        package_name = data.get('package')
        version = data.get('version', 'latest')
        callback_url = data.get('callback_url')  # For offline queue
        job_id = data.get('job_id')
        
        if not package_name:
            return jsonify({
                "success": False,
                "error": "Missing 'package' parameter"
            }), 400
        
        logger.info(f"📦 Installing package: {package_name} (version: {version})")
        
        # Try to install
        try:
            result = marketplace.install_package(package_name, version)
            
            response = {
                "success": True,
                "package": package_name,
                "version": version,
                "message": f"Package {package_name} installed successfully",
                "result": result
            }
            
            # If callback URL provided, send success notification
            if callback_url:
                queue_callback(callback_url, job_id, "completed", response)
            
            return jsonify(response)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Installation failed: {error_msg}")
            
            response = {
                "success": False,
                "package": package_name,
                "error": error_msg
            }
            
            # If callback URL provided, queue for retry or send failure
            if callback_url:
                queue_callback(callback_url, job_id, "failed", response)
            
            return jsonify(response), 500
            
    except Exception as e:
        logger.error(f"Request processing error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/v1/marketplace/uninstall', methods=['POST'])
def uninstall_package():
    """Uninstall a marketplace package"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid JSON request body"
            }), 400
        
        package_name = data.get('package')
        callback_url = data.get('callback_url')
        job_id = data.get('job_id')
        
        if not package_name:
            return jsonify({
                "success": False,
                "error": "Missing 'package' parameter"
            }), 400
        
        logger.info(f"🗑️  Uninstalling package: {package_name}")
        
        try:
            result = marketplace.uninstall_package(package_name)
            
            response = {
                "success": True,
                "package": package_name,
                "message": f"Package {package_name} uninstalled successfully",
                "result": result
            }
            
            if callback_url:
                queue_callback(callback_url, job_id, "completed", response)
            
            return jsonify(response)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Uninstallation failed: {error_msg}")
            
            response = {
                "success": False,
                "package": package_name,
                "error": error_msg
            }
            
            if callback_url:
                queue_callback(callback_url, job_id, "failed", response)
            
            return jsonify(response), 500
            
    except Exception as e:
        logger.error(f"Request processing error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/v1/marketplace/update', methods=['POST'])
def update_package():
    """Update a marketplace package"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid JSON request body"
            }), 400
        
        package_name = data.get('package')
        version = data.get('version', 'latest')
        callback_url = data.get('callback_url')
        job_id = data.get('job_id')
        
        if not package_name:
            return jsonify({
                "success": False,
                "error": "Missing 'package' parameter"
            }), 400
        
        logger.info(f"🔄 Updating package: {package_name} to {version}")
        
        try:
            result = marketplace.update_package(package_name, version)
            
            response = {
                "success": True,
                "package": package_name,
                "version": version,
                "message": f"Package {package_name} updated successfully",
                "result": result
            }
            
            if callback_url:
                queue_callback(callback_url, job_id, "completed", response)
            
            return jsonify(response)
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Update failed: {error_msg}")
            
            response = {
                "success": False,
                "package": package_name,
                "error": error_msg
            }
            
            if callback_url:
                queue_callback(callback_url, job_id, "failed", response)
            
            return jsonify(response), 500
            
    except Exception as e:
        logger.error(f"Request processing error: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def queue_callback(callback_url: str, job_id: str, status: str, result: Dict):
    """Queue a callback for offline processing"""
    callback_data = {
        "callback_url": callback_url,
        "job_id": job_id,
        "status": status,
        "result": result,
        "timestamp": int(time.time()),
        "retry_count": 0
    }
    job_queue.append(callback_data)
    logger.info(f"📋 Queued callback for job {job_id}: {status}")


def process_callback_queue():
    """Process queued callbacks (runs in background thread)"""
    import requests
    
    while True:
        try:
            if job_queue:
                callback = job_queue[0]  # Get first item
                
                try:
                    # Send callback
                    response = requests.post(
                        callback["callback_url"],
                        json={
                            "job_id": callback["job_id"],
                            "status": callback["status"],
                            "result": callback["result"],
                            "timestamp": callback["timestamp"]
                        },
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"✅ Callback sent for job {callback['job_id']}")
                        job_queue.pop(0)  # Remove from queue
                    else:
                        logger.warning(f"⚠️  Callback failed (HTTP {response.status_code})")
                        callback["retry_count"] += 1
                        
                        if callback["retry_count"] > 5:
                            logger.error(f"❌ Callback failed after 5 retries, dropping")
                            job_queue.pop(0)
                        else:
                            # Move to end of queue for retry
                            job_queue.append(job_queue.pop(0))
                            
                except requests.exceptions.RequestException as e:
                    logger.warning(f"⚠️  Callback network error: {e}")
                    callback["retry_count"] += 1
                    
                    if callback["retry_count"] > 5:
                        job_queue.pop(0)
                    else:
                        job_queue.append(job_queue.pop(0))
                        
        except Exception as e:
            logger.error(f"Callback queue processing error: {e}")
        
        time.sleep(10)  # Check every 10 seconds


def start_server():
    """Start the SAN CLI API server"""
    global current_port
    
    # Find free port
    current_port = find_free_port()
    
    logger.info(f"🚀 Starting SAN CLI API Server v{__version__}")
    logger.info(f"📡 Port: {current_port}")
    logger.info(f"📋 Announcement: /var/run/san-cli-api.json (or /tmp)")
    
    # Start background threads
    threading.Thread(target=update_announcement, daemon=True).start()
    threading.Thread(target=process_callback_queue, daemon=True).start()
    
    # Start Flask server
    app.run(host='0.0.0.0', port=current_port, debug=False)


if __name__ == '__main__':
    start_server()
