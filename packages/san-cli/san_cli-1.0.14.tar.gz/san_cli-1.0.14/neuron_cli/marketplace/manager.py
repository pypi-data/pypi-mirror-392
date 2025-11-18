"""Marketplace package manager"""

import subprocess
import platform
import requests
from typing import List, Dict, Optional
from ..core.logger import logger
from ..core.config import Config
from ..installer import HostServiceInstaller, SystemDetector
from ..services import DockerServiceManager


class MarketplaceManager:
    """Manage marketplace packages"""
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.docker_manager = DockerServiceManager()
        self.detector = SystemDetector()
        self.config = Config()
        self.api_url = self.config.data.get('api_url', 'https://support.nexuscore.cloud')
        self.packages = self._get_builtin_packages()
    
    def _get_builtin_packages(self) -> Dict[str, Dict]:
        """Get built-in package definitions"""
        return {
            'mesh-ai-chat_mesh': {
                'name': 'mesh-ai-chat_mesh',
                'version': '1.0.0',
                'type': 'docker',
                'description': 'AI chat service with Ollama integration',
                'category': 'AI Services',
                'docker': {
                    'image': 'registry.nexuscore.cloud/mesh-ai-chat:latest',
                    'container_name': 'mesh-ai-chat_mesh',
                    'network': 'cave_mesh',
                    'ports': ['8024:8000'],
                    'environment': {
                        'OLLAMA_HOST': 'http://host.docker.internal:11434',
                        'DEFAULT_MODEL': 'llama3.1:8b',
                        'BRAND_API_KEY': 'nexuscore-support-api-key-44444',
                    },
                },
                'dependencies': ['ollama', 'space-agent'],
                'healthcheck': {'url': 'http://localhost:8024/health'},
            },
            'mesh-ai-rag_mesh': {
                'name': 'mesh-ai-rag_mesh',
                'version': '1.0.0',
                'type': 'docker',
                'description': 'RAG (Retrieval-Augmented Generation) service',
                'category': 'AI Services',
                'docker': {
                    'image': 'registry.nexuscore.cloud/mesh-ai-rag:latest',
                    'container_name': 'mesh-ai-rag_mesh',
                    'network': 'cave_mesh',
                    'ports': ['8025:8000'],
                    'environment': {
                        'OLLAMA_HOST': 'http://host.docker.internal:11434',
                        'DEFAULT_MODEL': 'llama3.1:8b',
                    },
                },
                'dependencies': ['ollama', 'space-agent'],
                'healthcheck': {'url': 'http://localhost:8025/health'},
            },
            'ai-flow-control_mesh': {
                'name': 'ai-flow-control_mesh',
                'version': '1.0.0',
                'type': 'docker',
                'description': 'AI-powered workflow orchestration',
                'category': 'AI Services',
                'docker': {
                    'image': 'registry.nexuscore.cloud/ai-flow-control:latest',
                    'container_name': 'ai-flow-control_mesh',
                    'network': 'cave_mesh',
                    'ports': ['8027:8000'],
                    'environment': {
                        'OLLAMA_HOST': 'http://ollama_mesh:11434',
                        'MESH_AI_CHAT_URL': 'http://mesh-ai-chat_mesh:8000',
                        'WHISPER_URL': 'http://host.docker.internal:8026',
                    },
                },
                'dependencies': ['ollama', 'space-agent'],
                'healthcheck': {'url': 'http://localhost:8027/health'},
            },
            'redis_mesh': {
                'name': 'redis_mesh',
                'version': '7.2.0',
                'type': 'docker',
                'description': 'Redis cache and message broker',
                'category': 'Infrastructure',
                'docker': {
                    'image': 'redis:7.2-alpine',
                    'container_name': 'redis_mesh',
                    'network': 'cave_mesh',
                    'ports': ['6379:6379'],
                },
                'dependencies': ['space-agent'],
                'healthcheck': {'command': 'redis-cli ping'},
            },
            'postgres_mesh': {
                'name': 'postgres_mesh',
                'version': '16.0',
                'type': 'docker',
                'description': 'PostgreSQL database',
                'category': 'Infrastructure',
                'docker': {
                    'image': 'postgres:16-alpine',
                    'container_name': 'postgres_mesh',
                    'network': 'cave_mesh',
                    'ports': ['5432:5432'],
                    'environment': {
                        'POSTGRES_PASSWORD': 'postgres',
                        'POSTGRES_DB': 'nexuscore',
                    },
                    'volumes': ['postgres_data:/var/lib/postgresql/data'],
                },
                'dependencies': ['space-agent'],
                'healthcheck': {'command': 'pg_isready'},
            },
        }
    
    def list_packages(self, category: Optional[str] = None) -> List[Dict]:
        """List available packages from API"""
        try:
            # Try to fetch from API first
            url = f"{self.api_url}/api/v1/marketplace/packages"
            params = {}
            if category:
                params['category'] = category
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # API returns {"packages": [...], "total": N}
                # Return API response even if empty (don't fallback to built-in)
                return data.get('packages', [])
        except Exception as e:
            logger.debug(f"Failed to fetch from API, using built-in packages: {e}")
        
        # Fallback to built-in packages only on error
        packages = list(self.packages.values())
        
        if category:
            packages = [p for p in packages if p.get('category') == category]
        
        return packages
    
    def search_packages(self, query: str) -> List[Dict]:
        """Search packages"""
        query = query.lower()
        results = []
        
        for pkg in self.packages.values():
            if (query in pkg['name'].lower() or 
                query in pkg['description'].lower() or
                query in pkg.get('category', '').lower()):
                results.append(pkg)
        
        return results
    
    def get_package(self, name: str) -> Optional[Dict]:
        """Get package by name from API"""
        try:
            # Try to fetch from API first
            url = f"{self.api_url}/api/v1/marketplace/packages/{name}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.debug(f"Failed to fetch from API, using built-in packages: {e}")
        
        # Fallback to built-in packages
        return self.packages.get(name)
    
    def install_package(self, name: str) -> bool:
        """Install a package"""
        pkg = self.get_package(name)
        if not pkg:
            logger.error(f"Package '{name}' not found")
            return False
        
        logger.info(f"📦 Installing {pkg['name']}")
        logger.info(f"   {pkg['description']}")
        
        # Check dependencies
        if not self._check_dependencies(pkg):
            return False
        
        # Install based on type
        pkg_type = pkg.get('type', 'docker')
        
        # Handle package types
        if pkg_type in ['docker', 'service', 'app']:  # service/app are aliases for docker
            return self._install_docker_package(pkg)
        elif pkg_type == 'native':
            return self._install_native_package(pkg)
        elif pkg_type == 'sdk':
            return self._install_sdk_package(pkg)
        elif pkg_type == 'script':
            return self._install_script_package(pkg)
        elif pkg_type == 'system':
            return self._install_system_package(pkg)
        elif pkg_type == 'host':
            return self._install_host_package(pkg)
        else:
            logger.error(f"   ❌ Unknown package type: {pkg_type}")
            return False
    
    def _check_dependencies(self, pkg: Dict) -> bool:
        """Check package dependencies"""
        deps = pkg.get('dependencies', [])
        
        if not deps:
            return True
        
        logger.info(f"   Checking dependencies...")
        
        for dep in deps:
            if dep == 'space-agent':
                if not self.docker_manager.exists('space-agent'):
                    logger.error(f"   ❌ Dependency missing: {dep}")
                    logger.info(f"   Install with: san-cli install")
                    return False
            elif dep == 'ollama':
                # Check if Ollama is installed
                try:
                    result = subprocess.run(['ollama', '--version'], capture_output=True, timeout=5)
                    if result.returncode != 0:
                        logger.error(f"   ❌ Dependency missing: {dep}")
                        logger.info(f"   Install with: san-cli install")
                        return False
                except FileNotFoundError:
                    logger.error(f"   ❌ Dependency missing: {dep}")
                    logger.info(f"   Install with: san-cli install")
                    return False
        
        logger.info(f"   ✅ All dependencies satisfied")
        return True
    
    def _install_docker_package(self, pkg: Dict) -> bool:
        """Install Docker package"""
        # Handle both nested docker config and flat structure
        if 'docker' in pkg:
            docker_config = pkg['docker']
            image = docker_config['image']
            container_name = docker_config.get('container_name', pkg['name'])
            network = docker_config.get('network', 'bridge')
            ports = docker_config.get('ports', [])
            environment = docker_config.get('environment', {})
            volumes = docker_config.get('volumes', [])
        else:
            # Flat structure from API
            image = pkg.get('docker_image')
            if not image:
                logger.error(f"   ❌ No docker_image specified")
                return False
            container_name = pkg.get('container_name', pkg['name'])
            network = pkg.get('network', 'bridge')
            ports = pkg.get('ports', [])
            environment = pkg.get('environment', {})
            volumes = pkg.get('volumes', [])
        
        try:
            # Authenticate with registry if needed
            if 'registry.nexuscore.cloud' in image:
                logger.info(f"   🔐 Authenticating with registry...")
                
                # Get registry credentials from backend API
                device_api_key = self.config.get('device_api_key') or self.config.get('jwt_token')
                if not device_api_key:
                    logger.error(f"   ❌ No device API key found in config")
                    return False
                
                try:
                    # Request registry credentials from backend
                    import requests
                    api_url = self.config.get('api_url', 'https://support.nexuscore.cloud')
                    response = requests.get(
                        f"{api_url}/registry/auth/{device_api_key}",
                        timeout=10
                    )
                    
                    if response.status_code != 200:
                        logger.error(f"   ❌ Failed to get registry credentials: {response.status_code}")
                        return False
                    
                    creds = response.json()
                    registry_user = creds.get('username')
                    registry_pass = creds.get('password')
                    
                    if not registry_user or not registry_pass:
                        logger.error(f"   ❌ Invalid registry credentials received")
                        return False
                    
                except Exception as e:
                    logger.error(f"   ❌ Failed to fetch registry credentials: {e}")
                    return False
                
                # Login to registry
                login_result = subprocess.run(
                    ['docker', 'login', 'registry.nexuscore.cloud', '-u', registry_user, '--password-stdin'],
                    input=registry_pass,
                    capture_output=True,
                    timeout=30,
                    text=True
                )
                if login_result.returncode == 0:
                    logger.info(f"   ✅ Registry authentication successful")
                else:
                    logger.error(f"   ❌ Registry login failed: {login_result.stderr.strip()}")
                    logger.error(f"   Cannot proceed without authentication")
                    return False
            
            # Pull image with real-time output
            logger.info(f"   📥 Pulling Docker image: {image}")
            logger.info(f"   (This may take a few minutes...)")
            
            # Use Popen to show real-time progress
            process = subprocess.Popen(
                ['docker', 'pull', image],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Stream output line by line
            for line in process.stdout:
                line = line.strip()
                if line:
                    # Show progress lines
                    if 'Pulling' in line or 'Downloading' in line or 'Extracting' in line or 'Pull complete' in line:
                        logger.info(f"      {line}")
            
            process.wait(timeout=300)
            
            if process.returncode != 0:
                logger.error(f"   ❌ Failed to pull image")
                return False
            
            logger.info(f"   ✅ Image pulled successfully")
            
            # Show image info
            inspect_result = subprocess.run(
                ['docker', 'inspect', '--format', '{{.Created}}', image],
                capture_output=True,
                text=True,
                timeout=10
            )
            if inspect_result.returncode == 0:
                created = inspect_result.stdout.strip()
                logger.info(f"   📅 Image created: {created[:19]}")
            
            # Stop existing container
            logger.info(f"   Stopping existing container...")
            subprocess.run(['docker', 'stop', container_name], capture_output=True)
            subprocess.run(['docker', 'rm', container_name], capture_output=True)
            
            # Build docker run command
            cmd = ['docker', 'run', '-d']
            cmd.extend(['--name', container_name])
            cmd.extend(['--network', network])
            cmd.append('--restart=unless-stopped')
            
            # Add ports
            for port in ports:
                cmd.extend(['-p', port])
            
            # Add environment variables
            # For SPACE Agent, inject config from SAN CLI
            if pkg['name'] == 'space-agent':
                environment.setdefault('DEVICE_ID', self.config.get('device_id'))
                environment.setdefault('DEVICE_API_KEY', self.config.get('device_api_key') or self.config.get('jwt_token'))
                environment.setdefault('BRAND_ID', self.config.get('brand_id', 'nexuscore'))
                environment.setdefault('GATEWAY_URL', self.config.get('gateway_url', 'wss://support.nexuscore.cloud:22092/ws'))
                logger.info(f"   🔧 Configuring with device: {environment.get('DEVICE_ID')}")
            
            for key, value in environment.items():
                if value:  # Only add if value is not None
                    cmd.extend(['-e', f'{key}={value}'])
            
            # Add volumes
            # For SPACE Agent, ensure docker socket is mounted
            if pkg['name'] == 'space-agent' and not any('/var/run/docker.sock' in v for v in volumes):
                volumes.append('/var/run/docker.sock:/var/run/docker.sock')
                logger.info(f"   🐳 Mounting Docker socket for container management")
            
            for volume in volumes:
                cmd.extend(['-v', volume])
            
            # Add image
            cmd.append(image)
            
            # Run container
            logger.info(f"   Starting container...")
            result = subprocess.run(cmd, capture_output=True, timeout=30)
            
            if result.returncode != 0:
                logger.error(f"   ❌ Failed to start container: {result.stderr.decode()}")
                return False
            
            # Verify health
            if pkg.get('healthcheck'):
                logger.info(f"   Verifying health...")
                import time
                time.sleep(3)
                
                healthcheck = pkg['healthcheck']
                if 'url' in healthcheck:
                    try:
                        result = subprocess.run(
                            ['curl', '-s', healthcheck['url']],
                            capture_output=True,
                            timeout=10
                        )
                        if result.returncode != 0:
                            logger.warning(f"   ⚠️  Health check failed (service may still be starting)")
                    except FileNotFoundError:
                        logger.warning(f"   ⚠️  curl not found, skipping health check")
                elif 'command' in healthcheck:
                    # Command-based health check (like redis-cli ping)
                    try:
                        result = subprocess.run(
                            ['docker', 'exec', container_name] + healthcheck['command'].split(),
                            capture_output=True,
                            timeout=10
                        )
                        if result.returncode != 0:
                            logger.warning(f"   ⚠️  Health check failed (service may still be starting)")
                    except Exception:
                        logger.warning(f"   ⚠️  Health check failed")
            
            logger.info(f"   ✅ {pkg['name']} installed successfully")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Installation failed: {e}")
            return False
    
    def _install_native_package(self, pkg: Dict) -> bool:
        """Install native package using install script"""
        try:
            # Get install script from package
            install_script = pkg.get('install_script')
            if not install_script:
                logger.error("   ❌ No install_script found in package")
                return False
            
            logger.info(f"   Executing native installation script...")
            
            # Execute install script with bash
            result = subprocess.run(
                ['bash', '-c', install_script],
                capture_output=True,
                timeout=600,  # 10 minute timeout
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"   ❌ Installation failed")
                logger.error(f"   Error: {result.stderr}")
                return False
            
            logger.info(f"   ✅ {pkg['name']} installed successfully")
            if result.stdout:
                logger.debug(f"   Output: {result.stdout}")
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.error(f"   ❌ Installation timed out (10 minutes)")
            return False
        except Exception as e:
            logger.error(f"   ❌ Installation failed: {e}")
            return False
    
    def _install_sdk_package(self, pkg: Dict) -> bool:
        """Install SDK package using npm, pip, or yarn"""
        try:
            # Get install method and package name
            install_method = pkg.get('install_method')
            package_name = pkg.get('package_name') or pkg.get('name')
            
            if not install_method:
                logger.error("   ❌ No install_method found in package")
                return False
            
            logger.info(f"   Installing via {install_method}...")
            
            # Build command based on install method
            if install_method == 'npm':
                cmd = ['npm', 'install', '-g', package_name]
            elif install_method in ['pip', 'pip3']:
                cmd = ['pip3', 'install', package_name]
            elif install_method == 'yarn':
                cmd = ['yarn', 'global', 'add', package_name]
            else:
                logger.error(f"   ❌ Unsupported install method: {install_method}")
                return False
            
            # Execute installation
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=300,  # 5 minute timeout
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"   ❌ Installation failed")
                logger.error(f"   Error: {result.stderr}")
                return False
            
            logger.info(f"   ✅ {package_name} installed successfully")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error(f"   ❌ Installation timed out (5 minutes)")
            return False
        except FileNotFoundError:
            logger.error(f"   ❌ {install_method} not found. Please install it first.")
            return False
        except Exception as e:
            logger.error(f"   ❌ Installation failed: {e}")
            return False
    
    def _install_script_package(self, pkg: Dict) -> bool:
        """Install script package by executing bash script"""
        try:
            # Get script content
            script_content = pkg.get('script')
            if not script_content:
                logger.error("   ❌ No script found in package")
                return False
            
            logger.info(f"   Executing installation script...")
            
            # Execute script directly with bash
            result = subprocess.run(
                ['bash', '-c', script_content],
                capture_output=True,
                timeout=300,  # 5 minute timeout
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"   ❌ Script execution failed")
                logger.error(f"   Error: {result.stderr}")
                return False
            
            logger.info(f"   ✅ {pkg['name']} installed successfully")
            if result.stdout:
                logger.info(f"   Output: {result.stdout}")
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.error(f"   ❌ Script execution timed out (5 minutes)")
            return False
        except Exception as e:
            logger.error(f"   ❌ Script execution failed: {e}")
            return False
    
    def _install_system_package(self, pkg: Dict) -> bool:
        """Install system package using OS package manager (apt/brew)"""
        try:
            package_name = pkg.get('package_name') or pkg.get('name')
            
            logger.info(f"   Installing system package: {package_name}...")
            
            # Detect OS and use appropriate package manager
            if self.os_type == 'darwin':
                # macOS - use Homebrew
                cmd = ['brew', 'install', package_name]
            elif self.os_type == 'linux':
                # Linux - use apt-get
                cmd = ['sudo', 'apt-get', 'install', '-y', package_name]
            else:
                logger.error(f"   ❌ Unsupported OS: {self.os_type}")
                return False
            
            # Execute installation
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=600,  # 10 minute timeout
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"   ❌ Installation failed")
                logger.error(f"   Error: {result.stderr}")
                return False
            
            logger.info(f"   ✅ {package_name} installed successfully")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error(f"   ❌ Installation timed out (10 minutes)")
            return False
        except FileNotFoundError as e:
            logger.error(f"   ❌ Package manager not found: {e}")
            return False
        except Exception as e:
            logger.error(f"   ❌ Installation failed: {e}")
            return False
    
    def _install_host_package(self, pkg: Dict) -> bool:
        """Install host package (legacy, use native instead)"""
        logger.warning("   ⚠️  'host' type is deprecated, use 'native' instead")
        return self._install_native_package(pkg)
    
    def uninstall_package(self, name: str) -> bool:
        """Uninstall a package"""
        pkg = self.get_package(name)
        if not pkg:
            logger.error(f"Package '{name}' not found")
            return False
        
        logger.info(f"🗑️  Uninstalling {pkg['name']}")
        
        if pkg['type'] == 'docker':
            container_name = pkg['docker']['container_name']
            
            # Stop and remove container
            subprocess.run(['docker', 'stop', container_name], capture_output=True)
            subprocess.run(['docker', 'rm', container_name], capture_output=True)
            
            logger.info(f"   ✅ {pkg['name']} uninstalled")
            return True
        
        return False
    
    def update_package(self, name: str) -> bool:
        """Update a package"""
        pkg = self.get_package(name)
        if not pkg:
            logger.error(f"Package '{name}' not found")
            return False
        
        logger.info(f"🔄 Updating {pkg['name']}")
        
        # For Docker packages, pull latest and restart
        if pkg['type'] == 'docker':
            docker_config = pkg['docker']
            
            # Pull latest image
            logger.info(f"   Pulling latest image...")
            result = subprocess.run(
                ['docker', 'pull', docker_config['image']],
                capture_output=True,
                timeout=300
            )
            
            if result.returncode != 0:
                logger.error(f"   ❌ Failed to pull image")
                return False
            
            # Restart container
            container_name = docker_config['container_name']
            logger.info(f"   Restarting container...")
            
            subprocess.run(['docker', 'stop', container_name], capture_output=True)
            subprocess.run(['docker', 'rm', container_name], capture_output=True)
            
            # Reinstall
            return self._install_docker_package(pkg)
        
        return False
    
    def get_categories(self) -> List[str]:
        """Get all package categories"""
        categories = set()
        for pkg in self.packages.values():
            if 'category' in pkg:
                categories.add(pkg['category'])
        return sorted(list(categories))
