#!/usr/bin/env python3
import os
import sys
import subprocess
import glob
from pathlib import Path

def install_package(package_name, requirements_file=None):
    """Install a Python package with user confirmation"""
    if requirements_file and os.path.exists(requirements_file):
        response = input(f"Would you like to install all requirements from {requirements_file}? (y/N): ")
        if response.lower() == 'y':
            try:
                print(f"Installing requirements from {requirements_file}...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], check=True)
                print("Requirements installed successfully!")
                return True
            except subprocess.CalledProcessError:
                print(f"Failed to install requirements from {requirements_file}")
    
    response = input(f"Would you like to install {package_name} automatically? (y/N): ")
    if response.lower() == 'y':
        try:
            print(f"Installing {package_name}...")
            subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=True)
            print(f"{package_name} installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to install {package_name} automatically.")
    return False

# Check for required Python packages
try:
    import yaml
except ImportError:
    print("Error: PyYAML package is not installed.")
    if not install_package("PyYAML", "requirements.txt"):
        print("Please install it manually with: pip install PyYAML")
        print("Or install all requirements: pip install -r requirements.txt")
        sys.exit(1)
    
    # Try importing again after installation
    try:
        import yaml
    except ImportError:
        print("Still unable to import PyYAML. Please install it manually.")
        sys.exit(1)

class ConfigManager:
    def __init__(self):
        self.config_file = 'config.yml'
        self.docker_compose_file = 'docker-compose.yml'
        self.nginx_config_dir = 'docker/nginx/config'
        self.apache_config_dir = 'docker/apache-php-56/config/sites-enabled'
        self.templates_dir = 'docker/nginx/config/templates'
        self.docker_templates_dir = 'templates'
        
    def init_config(self):
        """Initialize default config.yml file"""
        if os.path.exists(self.config_file):
            response = input(f'{self.config_file} already exists. Overwrite? (y/N): ')
            if response.lower() != 'y':
                print("Operation cancelled.")
                return False
        
        default_config = {
            'supersite.test': {
                'main_host': 'supersite.test',
                'redirect_aliases': ['www.supersite.test'],
                'aliases': ['api.supersite.test'],
                'php_version': 'apache-php-56',
                'https': True
            },
            'normalsite.test': {
                'main_host': 'normalsite.test',
                'redirect_aliases': ['www.normalsite.test'],
                'aliases': ['api.normalsite.test'],
                'php_version': 'php-84',
                'https': False
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
        
        print(f"Default {self.config_file} created successfully.")
        return True
    
    def load_config(self):
        """Load config.yml file"""
        if not os.path.exists(self.config_file):
            print(f"{self.config_file} does not exist. Run 'python manage.py init' first.")
            return None
        
        with open(self.config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def stop_containers(self):
        """Stop all running containers"""
        print("Stopping Docker containers...")
        try:
            subprocess.run(['docker', 'compose', 'stop'], check=True)
            print("Containers stopped successfully.")
        except subprocess.CalledProcessError:
            print("Warning: Failed to stop containers.")
        except FileNotFoundError:
            print("Warning: Docker not found. Skipping container stop.")
    
    def get_php_servers(self, config):
        """Get list of PHP servers needed based on config"""
        servers = set()
        for site_data in config.values():
            php_version = site_data.get('php_version', 'php-84')
            servers.add(php_version)
        return sorted(list(servers))
    
    def generate_nginx_config(self, host_data, php_version):
        """Generate nginx config for a host"""
        main_host = host_data['main_host']
        redirect_aliases = host_data.get('redirect_aliases', [])
        aliases = host_data.get('aliases', [])
        is_https = host_data.get('https', False)
        
        config = ""
        
        if is_https:
            # For HTTPS sites, generate HTTP redirect server
            config += f"""server {{
    listen 80;
    server_name {main_host} {' '.join(redirect_aliases)} {' '.join(aliases)};
    
    # Redirect all HTTP traffic to HTTPS
    return 301 https://{main_host}$request_uri;
}}
"""
        else:
            # For HTTP sites, generate redirect servers for redirect_aliases
            for alias in redirect_aliases:
                config += f"""server {{
    listen 80;
    server_name {alias};
    
    # Redirect alias to main host
    return 301 http://{main_host}$request_uri;
}}
"""
            
            # For HTTP sites, use the template approach for main host
            if php_version.startswith('apache-php-'):
                template_file = f'{self.templates_dir}/site.test.conf-{php_version}'
            else:
                template_file = f'{self.templates_dir}/site.test.conf-{php_version}'
            
            if not os.path.exists(template_file):
                print(f"Template file not found: {template_file}")
                return None
            
            with open(template_file, 'r') as f:
                template = f.read()
            
            # Replace placeholders
            config_content = template.replace('site.test', main_host)
            
            # Add aliases to server_name in main config
            all_server_names = [main_host] + aliases
            if all_server_names:
                server_name_line = f"    server_name {' '.join(all_server_names)};"
                config_content = config_content.replace(f"    server_name {main_host};", server_name_line)
            
            config += config_content
        
        return config
    
    def generate_https_config(self, host_data):
        """Generate HTTPS nginx config with self-signed certificate"""
        php_version = host_data.get('php_version', 'apache-php-56')
        main_host = host_data['main_host']
        redirect_aliases = host_data.get('redirect_aliases', [])
        aliases = host_data.get('aliases', [])
        
        # Check if we have www aliases that need redirecting
        www_aliases = [alias for alias in redirect_aliases if alias.startswith('www.')]
        non_www_redirect_aliases = [alias for alias in redirect_aliases if not alias.startswith('www.')]
        
        config = ""
        
        # Create redirect server blocks for www aliases
        for www_alias in www_aliases:
            config += f"""server {{
    listen 443 ssl;
    http2 on;
    
    # server name:
    server_name {www_alias};
    
    # SSL configuration
    ssl_certificate /etc/nginx/ssl/{main_host}.crt;
    ssl_certificate_key /etc/nginx/ssl/{main_host}.key;
    include conf.d/includes/ssl.inc;
    
    # Redirect www to non-www
    return 301 https://{main_host}$request_uri;
}}

"""
        
        # Create main server block for main host and non-www aliases + regular aliases
        main_server_names = [main_host] + non_www_redirect_aliases + aliases
        
        if php_version.startswith('apache-php-'):
            # Apache backend - use proxy
            config += f"""server {{
    listen 443 ssl;
    http2 on;
    
    # server name:
    server_name {' '.join(main_server_names)};
    
    # SSL configuration
    ssl_certificate /etc/nginx/ssl/{main_host}.crt;
    ssl_certificate_key /etc/nginx/ssl/{main_host}.key;
    include conf.d/includes/ssl.inc;

    # root directory
    root /srv/projects/{main_host};
    include conf.d/includes/restrictions.inc;

    satisfy  any;
    allow 192.168.1.0/24;
    deny all;
    auth_basic              "Restricted";
    auth_basic_user_file    .htpasswd;

    ######################################
    # Apache config
    ######################################
    location / {{
        proxy_pass http://{php_version};
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    include conf.d/includes/assets.inc;
}}"""
        else:
            # PHP-FPM backend - use fastcgi
            config += f"""server {{
    listen 443 ssl;
    http2 on;
    
    # server name:
    server_name {' '.join(main_server_names)};
    
    # SSL configuration
    ssl_certificate /etc/nginx/ssl/{main_host}.crt;
    ssl_certificate_key /etc/nginx/ssl/{main_host}.key;
    include conf.d/includes/ssl.inc;

    # root directory
    root /srv/projects/{main_host};
    include conf.d/includes/restrictions.inc;

    satisfy  any;
    allow 192.168.1.0/24;
    deny all;
    auth_basic              "Restricted";
    auth_basic_user_file    .htpasswd;

    ######################################
    # FPM config
    ######################################
    location ~ \\.php$ {{
        try_files $uri = 404;
        include fastcgi_params;
        fastcgi_pass  {php_version}:9000;
        fastcgi_index index.php;
        fastcgi_param  SCRIPT_FILENAME  $document_root$fastcgi_script_name;
        fastcgi_param  SERVER_NAME    $host;
        fastcgi_param  HTTPS          $https if_not_empty;
    }}

    location / {{
        index  index.php index.html index.htm;
        try_files $uri $uri/ /index.php?$args;
    }}

    include conf.d/includes/assets.inc;
}}"""
        
        return config
    
    def generate_apache_config(self, host_data):
        """Generate Apache virtual host config"""
        main_host = host_data['main_host']
        redirect_aliases = host_data.get('redirect_aliases', [])
        aliases = host_data.get('aliases', [])
        
        # Combine all aliases for ServerAlias
        all_aliases = redirect_aliases + aliases
        
        apache_template = f"""<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    ServerName {main_host}
    {'ServerAlias ' + ' '.join(all_aliases) if all_aliases else ''}
    DocumentRoot /srv/projects/{main_host}
</VirtualHost>"""
        return apache_template
    
    def generate_ssl_certificates(self, config):
        """Generate self-signed SSL certificates for HTTPS hosts"""
        ssl_dir = 'docker/nginx/ssl'
        os.makedirs(ssl_dir, exist_ok=True)
        
        # Generate Diffie-Hellman parameter file if needed
        dhparam_file = f"{ssl_dir}/dhparam.pem"
        if not os.path.exists(dhparam_file):
            print("Generating Diffie-Hellman parameters (this may take a moment)...")
            try:
                subprocess.run([
                    'openssl', 'dhparam', '-out', dhparam_file, '2048'
                ], check=True, capture_output=True)
                print("  Diffie-Hellman parameters generated successfully.")
            except subprocess.CalledProcessError as e:
                print(f"  Warning: Failed to generate dhparam.pem: {e}")
        
        https_hosts = [host for host, data in config.items() if data.get('https', False)]
        
        if https_hosts:
            print("Generating SSL certificates...")
            for host_key, host_data in config.items():
                if host_data.get('https', False):
                    main_host = host_data['main_host']
                    cert_file = f"{ssl_dir}/{main_host}.crt"
                    key_file = f"{ssl_dir}/{main_host}.key"
                    
                    if not os.path.exists(cert_file) or not os.path.exists(key_file):
                        print(f"  Generating certificate for {main_host}")
                        try:
                            subprocess.run([
                                'openssl', 'req', '-x509', '-nodes', '-days', '365',
                                '-newkey', 'rsa:2048',
                                '-keyout', key_file,
                                '-out', cert_file,
                                '-subj', f'/C=US/ST=State/L=City/O=Dev/CN={main_host}'
                            ], check=True, capture_output=True)
                        except subprocess.CalledProcessError as e:
                            print(f"  Failed to generate certificate for {main_host}: {e}")
    
    def create_project_directories(self, config):
        """Create project directories and index.php files for each host"""
        print("Creating project directories...")
        
        for host, host_data in config.items():
            main_host = host_data['main_host']
            project_dir = f"projects/{main_host}"
            
            # Create project directory if it doesn't exist
            if not os.path.exists(project_dir):
                os.makedirs(project_dir, exist_ok=True)
                print(f"  Created project directory: {project_dir}")
            
            # Create index.php file if it doesn't exist
            index_file = f"{project_dir}/index.php"
            if not os.path.exists(index_file):
                with open(index_file, 'w') as f:
                    f.write('<?php\n')
                    f.write('// PHP Version Test File\n')
                    f.write('echo "Welcome to " . $_SERVER[\'HTTP_HOST\'] . "!<br>";\n')
                    f.write('echo "PHP Version: " . phpversion() . "<br>";\n')
                    f.write('echo "Server Time: " . date(\'Y-m-d H:i:s\') . "<br>";\n')
                    f.write('phpinfo();\n')
                    f.write('?>\n')
                print(f"  Created index.php for {main_host}")
            else:
                print(f"  Project directory and index.php already exist for {main_host}")
    
    def generate_docker_compose(self, config):
        """Generate docker-compose.yml based on config"""
        php_servers = self.get_php_servers(config)
        
        # Load base template
        base_template = None
        for server in php_servers:
            template_file = f'{self.docker_templates_dir}/docker-compose-{server}.yml'
            if os.path.exists(template_file):
                with open(template_file, 'r') as f:
                    base_template = f.read()
                break
        
        if not base_template:
            print("No suitable template found")
            return False
        
        # Remove deprecated version attribute and add all PHP servers to the template
        lines = base_template.split('\n')
        # Remove version line if it exists
        lines = [line for line in lines if not line.startswith('version:')]
        insert_index = len(lines) - 1  # Before the last line
        
        for server in php_servers:
            if f'{server}:' not in base_template:
                template_file = f'{self.docker_templates_dir}/docker-compose-{server}.yml'
                if os.path.exists(template_file):
                    with open(template_file, 'r') as f:
                        server_template = f.read()
                    
                    # Extract server configuration
                    server_lines = server_template.split('\n')
                    in_server = False
                    server_config = []
                    
                    for line in server_lines:
                        if line.strip().startswith(f'{server}:'):
                            in_server = True
                            server_config.append(line)
                        elif in_server and line.strip() and not line.startswith(' '):
                            break
                        elif in_server:
                            server_config.append(line)
                    
                    if server_config:
                        lines.insert(insert_index, '')
                        for config_line in server_config:
                            lines.insert(insert_index, config_line)
                            insert_index += 1
        
        # Enable HTTPS port if needed
        https_hosts = [host for host, data in config.items() if data.get('https', False)]
        if https_hosts:
            lines = [line.replace('# -"443:443"', '- "443:443"') for line in lines]
            lines = [line.replace('# - ./docker/nginx/ssl:/etc/nginx/ssl:ro', '- ./docker/nginx/ssl:/etc/nginx/ssl:ro') for line in lines]
        
        with open(self.docker_compose_file, 'w') as f:
            f.write('\n'.join(lines))
        
        return True
    
    def check_mysql_env(self):
        """Check if mysql.env exists and create it from example if needed"""
        if not os.path.exists('mysql.env'):
            if os.path.exists('mysql.env.example'):
                response = input("mysql.env not found. Create it from mysql.env.example? (y/N): ")
                if response.lower() == 'y':
                    import shutil
                    shutil.copy2('mysql.env.example', 'mysql.env')
                    print("mysql.env created successfully from example.")
                    return True
                else:
                    print("Warning: mysql.env not created. Database configuration may be incomplete.")
                    return False
            else:
                print("Warning: Neither mysql.env nor mysql.env.example found.")
                return False
        return True
    
    def generate_configs(self):
        """Generate all configurations based on config.yml"""
        config = self.load_config()
        if not config:
            return False
        
        # Check mysql.env
        mysql_env_ok = self.check_mysql_env()
        
        # Show proposed changes
        print("\nProposed changes:")
        print(f"  - Hosts to configure: {list(config.keys())}")
        php_servers = self.get_php_servers(config)
        print(f"  - PHP servers needed: {php_servers}")
        https_hosts = [host for host, data in config.items() if data.get('https', False)]
        print(f"  - HTTPS hosts: {https_hosts}")
        if not mysql_env_ok:
            print("  - Warning: mysql.env configuration missing")
        
        response = input("\nProceed with generating configurations? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            return False
        
        # Stop containers
        self.stop_containers()
        
        # Generate SSL certificates
        self.generate_ssl_certificates(config)
        
        # Generate docker-compose.yml
        if not self.generate_docker_compose(config):
            print("Failed to generate docker-compose.yml")
            return False
        print("docker-compose.yml generated successfully.")
        
        # Create project directories and index.php files
        self.create_project_directories(config)
        
        # Clean up existing configs
        nginx_configs = glob.glob(f'{self.nginx_config_dir}/*.conf')
        for config_file in nginx_configs:
            if config_file not in [f'{self.nginx_config_dir}/default.conf', 
                                 f'{self.nginx_config_dir}/adminer.conf',
                                 f'{self.nginx_config_dir}/mailhog.conf']:
                os.remove(config_file)
        
        apache_configs = glob.glob(f'{self.apache_config_dir}/*.conf')
        for config_file in apache_configs:
            if config_file != f'{self.apache_config_dir}/default.conf':
                os.remove(config_file)
        
        # Generate nginx configs
        for host, host_data in config.items():
            nginx_config = self.generate_nginx_config(host_data, host_data.get('php_version', 'php-84'))
            if nginx_config:
                config_file = f'{self.nginx_config_dir}/{host_data["main_host"]}.conf'
                with open(config_file, 'w') as f:
                    f.write(nginx_config)
                print(f"  Nginx config created: {config_file}")
                
                # Generate HTTPS config if needed
                if host_data.get('https', False):
                    https_config = self.generate_https_config(host_data)
                    https_config_file = f'{self.nginx_config_dir}/https_{host_data["main_host"]}.conf'
                    with open(https_config_file, 'w') as f:
                        f.write(https_config)
                    print(f"  HTTPS config created: {https_config_file}")
            
            # Generate Apache config if using Apache PHP
            if host_data.get('php_version', '').startswith('apache-php-'):
                apache_config = self.generate_apache_config(host_data)
                apache_config_file = f'{self.apache_config_dir}/{host_data["main_host"]}.conf'
                with open(apache_config_file, 'w') as f:
                    f.write(apache_config)
                print(f"  Apache config created: {apache_config_file}")
        
        print("\nConfiguration generation completed successfully!")
        print("You can now start the containers with: docker compose up -d")
        return True
    
    def show_help(self):
        """Show help information"""
        print("Docker Compose PHP Manager")
        print("")
        print("Usage: python manage.py <command>")
        print("")
        print("Commands:")
        print("  init     - Create default config.yml file")
        print("  generate - Generate docker-compose.yml and all config files")
        print("           - Also creates project directories and test index.php files")
        print("  help     - Show this help message")
        print("")
        print("Note: The 'generate' command will automatically create project directories")
        print("      in the 'projects/' folder with test index.php files for each host.")

def main():
    manager = ConfigManager()
    
    if len(sys.argv) < 2:
        manager.show_help()
        return
    
    command = sys.argv[1]
    
    if command == 'init':
        manager.init_config()
    elif command == 'generate':
        manager.generate_configs()
    elif command == 'help':
        manager.show_help()
    else:
        print(f"Unknown command: {command}")
        manager.show_help()

if __name__ == '__main__':
    main()