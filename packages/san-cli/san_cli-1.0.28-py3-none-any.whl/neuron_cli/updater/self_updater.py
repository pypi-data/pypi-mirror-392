"""Self-update system for SAN CLI"""

import subprocess
import requests
import json
import os
from datetime import datetime
from typing import Optional, Dict, List
from ..core.logger import logger
from ..core.config import Config
from ..version import __version__


class SelfUpdater:
    """Manage SAN CLI self-updates"""
    
    def __init__(self):
        self.config = Config()
        self.current_version = __version__
        self.pypi_url = "https://pypi.org/pypi/san-cli/json"
        self.versions_file = os.path.expanduser("~/.neuron/versions.json")
        self.api_url = self.config.data.get('api_url', 'https://support.nexuscore.cloud')
        
    def check_for_updates(self, silent: bool = False) -> Optional[str]:
        """Check if a new version is available on PyPI"""
        try:
            if not silent:
                logger.info("🔍 Checking for updates...")
            
            response = requests.get(self.pypi_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                latest_version = data['info']['version']
                
                if self._compare_versions(latest_version, self.current_version) > 0:
                    if not silent:
                        logger.info(f"✨ New version available: {latest_version} (current: {self.current_version})")
                    return latest_version
                else:
                    if not silent:
                        logger.info(f"✅ You're on the latest version: {self.current_version}")
                    return None
            else:
                if not silent:
                    logger.error(f"❌ Failed to check for updates: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            if not silent:
                logger.error(f"❌ Failed to check for updates: {e}")
            return None
    
    def check_and_notify(self) -> None:
        """Silent background check that only notifies if update available"""
        latest = self.check_for_updates(silent=True)
        if latest:
            logger.info(f"💡 New SAN CLI version available: {latest}")
            logger.info(f"   Run 'san update self' to update")
        
        # Update last check timestamp
        self.config.update_last_check()
    
    def auto_update_if_enabled(self) -> bool:
        """Check and auto-update if enabled in config"""
        auto_config = self.config.get_auto_update_config()
        
        if not auto_config.get("enabled"):
            return False
        
        if not self.config.should_check_for_updates():
            return False
        
        latest = self.check_for_updates(silent=True)
        
        if latest:
            if auto_config.get("auto_install"):
                logger.info(f"🔄 Auto-updating to {latest}...")
                return self.update_self(version=latest)
            else:
                logger.info(f"💡 New version available: {latest}")
                logger.info(f"   Run 'san update self' to update")
                self.config.update_last_check()
        
        return False
    
    def update_self(self, version: Optional[str] = None) -> bool:
        """Update SAN CLI to latest or specific version"""
        try:
            # Save current version before updating
            self._save_version_history(self.current_version)
            
            # Determine version to install
            if version:
                target_version = version
                logger.info(f"🔄 Updating to version {target_version}...")
            else:
                latest = self.check_for_updates()
                if not latest:
                    logger.info("✅ Already on latest version")
                    return True
                target_version = latest
                logger.info(f"🔄 Updating to latest version {target_version}...")
            
            # Check if pipx is available
            pipx_check = subprocess.run(['which', 'pipx'], capture_output=True)
            if pipx_check.returncode != 0:
                logger.error("❌ pipx not found. Please install with: brew install pipx")
                return False
            
            # Perform update
            logger.info("   📥 Downloading and installing...")
            result = subprocess.run(
                ['pipx', 'install', f'san-cli=={target_version}', '--force'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info(f"   ✅ Successfully updated to {target_version}")
                
                # Verify installation
                verify_result = subprocess.run(
                    ['san', '--version'],
                    capture_output=True,
                    text=True
                )
                
                if verify_result.returncode == 0:
                    installed_version = verify_result.stdout.strip().split()[-1]
                    logger.info(f"   ✅ Verified installation: {installed_version}")
                    
                    # Report to server
                    self._report_update(target_version, success=True)
                    
                    return True
                else:
                    logger.error("   ⚠️  Installation succeeded but verification failed")
                    return False
            else:
                logger.error(f"   ❌ Update failed: {result.stderr}")
                self._report_update(target_version, success=False, error=result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("   ❌ Update timed out")
            return False
        except Exception as e:
            logger.error(f"   ❌ Update failed: {e}")
            return False
    
    def rollback(self) -> bool:
        """Rollback to previous version"""
        try:
            history = self._load_version_history()
            
            if not history or len(history) < 2:
                logger.error("❌ No previous version to rollback to")
                return False
            
            # Get previous version (skip current)
            previous_version = None
            for entry in reversed(history):
                if entry['version'] != self.current_version:
                    previous_version = entry['version']
                    break
            
            if not previous_version:
                logger.error("❌ No previous version found")
                return False
            
            logger.info(f"🔄 Rolling back to version {previous_version}...")
            
            # Install previous version
            result = subprocess.run(
                ['pipx', 'install', f'san-cli=={previous_version}', '--force'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                logger.info(f"   ✅ Successfully rolled back to {previous_version}")
                
                # Report rollback to server
                self._report_rollback(previous_version)
                
                return True
            else:
                logger.error(f"   ❌ Rollback failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"   ❌ Rollback failed: {e}")
            return False
    
    def get_version_history(self) -> List[Dict]:
        """Get version history"""
        return self._load_version_history()
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two version strings. Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal"""
        try:
            parts1 = [int(x) for x in v1.split('.')]
            parts2 = [int(x) for x in v2.split('.')]
            
            for p1, p2 in zip(parts1, parts2):
                if p1 > p2:
                    return 1
                elif p1 < p2:
                    return -1
            
            # If all parts are equal, compare lengths
            if len(parts1) > len(parts2):
                return 1
            elif len(parts1) < len(parts2):
                return -1
            
            return 0
        except:
            return 0
    
    def _save_version_history(self, version: str):
        """Save version to history"""
        try:
            history = self._load_version_history()
            
            # Add new entry
            history.append({
                'version': version,
                'installed': datetime.utcnow().isoformat() + 'Z'
            })
            
            # Keep only last 10 versions
            history = history[-10:]
            
            # Save to file
            os.makedirs(os.path.dirname(self.versions_file), exist_ok=True)
            with open(self.versions_file, 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            logger.debug(f"Failed to save version history: {e}")
    
    def _load_version_history(self) -> List[Dict]:
        """Load version history"""
        try:
            if os.path.exists(self.versions_file):
                with open(self.versions_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def _report_update(self, version: str, success: bool, error: Optional[str] = None):
        """Report update to backend API"""
        try:
            device_id = self.config.data.get('device_id')
            jwt_token = self.config.data.get('jwt_token') or self.config.data.get('device_api_key')
            
            if not device_id or not jwt_token:
                logger.debug("No device credentials, skipping update report")
                return
            
            payload = {
                'device_id': device_id,
                'event_type': 'cli_update',
                'from_version': self.current_version,
                'to_version': version,
                'success': success,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
            if error:
                payload['error'] = error
            
            response = requests.post(
                f"{self.api_url}/api/v1/devices/{device_id}/events",
                json=payload,
                headers={'Authorization': f'Bearer {jwt_token}'},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.debug(f"Update reported to server")
            else:
                logger.debug(f"Failed to report update: HTTP {response.status_code}")
                
        except Exception as e:
            logger.debug(f"Failed to report update: {e}")
    
    def _report_rollback(self, version: str):
        """Report rollback to backend API"""
        try:
            device_id = self.config.data.get('device_id')
            jwt_token = self.config.data.get('jwt_token') or self.config.data.get('device_api_key')
            
            if not device_id or not jwt_token:
                return
            
            payload = {
                'device_id': device_id,
                'event_type': 'cli_rollback',
                'from_version': self.current_version,
                'to_version': version,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
            response = requests.post(
                f"{self.api_url}/api/v1/devices/{device_id}/events",
                json=payload,
                headers={'Authorization': f'Bearer {jwt_token}'},
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                logger.debug(f"Rollback reported to server")
                
        except Exception as e:
            logger.debug(f"Failed to report rollback: {e}")
