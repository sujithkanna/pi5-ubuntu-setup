import os
import sys
import yaml
import subprocess
from jinja2 import Template
import getpass
import shlex


REPO_TO_IMAGE = {
    'git@github.com:sujithkanna/docker-qbittorrent.git': 'hsalf-qbittorrent:latest'
}

WORKING_DIRECTORY = os.path.join(os.getcwd(), "DockerSetup")

NGINX_CONFIG_PATH = "/etc/nginx/sites-available"

nginx_template = """
server {
    listen 80;
    server_name {{ domain_name }};
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name {{ domain_name }};
    
    ssl_certificate /etc/letsencrypt/live/{{ domain_name }}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{{ domain_name }}/privkey.pem;
    
    # SSL settings (optional for better security)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA256';
    ssl_prefer_server_ciphers on;
    client_max_body_size 0;
    
    location / {
        proxy_pass http://localhost:{{ port }};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""
def run_command(command, cwd=None):
    """Runs a Bash command and returns the output."""
    try:
        print(f"Executing command: {command}")
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True, cwd=cwd)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr.strip()}")
        sys.exit(1) 
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1) 

def run_command_with_sudo(command, password, cwd=None):
    """Run command with sudo to handle permission issues and returns output."""
    password_escaped = shlex.quote(password)
    sudo_command = f"echo {password_escaped} | sudo -S {command}"
    return run_command(sudo_command, cwd)

def clone_repo(repo_url):
    """Clones the GitHub repository into the current directory."""
    current_dir = WORKING_DIRECTORY
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    clone_dir = os.path.join(current_dir, repo_name)
    
    command = f"git clone {repo_url} {clone_dir}"
    run_command(command)
    return clone_dir

def build_docker_image(dockerfile_dir, image_name):
    """Builds the Docker image using the Docker CLI."""
    command = f"docker build -t {image_name} {dockerfile_dir}"
    run_command(command)

def create_certificate(host):
    """Create an SSL certificate for the given host."""
    print(f"Creating certificate for {host}...")
    certbot_command = f"sudo certbot certonly --standalone --preferred-challenges http -d {host} --email sujith.niraikulathan@gmail.com --agree-tos --non-interactive"
    run_command(certbot_command)

def create_symlink(config_file_path, password, sites_enabled_directory="/etc/nginx/sites-enabled"):
    symlink_path = os.path.join(sites_enabled_directory, os.path.basename(config_file_path))
    run_command_with_sudo(f"ln -f {config_file_path} {symlink_path}", password)
    print(f"Symlink created at {symlink_path}")

def delete_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"{file_path} has been cleared.")

def setup_docker_user_group(env_file_path):
    print("Adding docker user to env file")
    with open(env_file_path, "a") as e:
        docker_user = run_command("id -u dockeruser")
        docker_group = run_command("id -g dockeruser")
        e.write(f"DOCKER_USER={docker_user}\n")
        e.write(f"DOCKER_GROUP={docker_group}\n")

def create_nginx_configs_and_env(data, project_directory, password):
    """Creates Nginx config files and a fresh .env file."""
    env_file_path = os.path.join(project_directory, '.env')
    delete_file(env_file_path)
    run_command_with_sudo(f"rm -f {NGINX_CONFIG_PATH}/default", password)
    setup_docker_user_group(env_file_path)
    template = Template(nginx_template)
    
    for service, details in data.get('services', {}).items():
        host = details.get('host')
        port = details.get('port')
        
        if host and port:
            config = template.render(domain_name=host, port=port)
            config_file = f"{NGINX_CONFIG_PATH}/{host}.conf"
            local_config_file = f"{project_directory}/{host}.conf"
        
            create_certificate(host)

            #Clear config files
            delete_file(local_config_file)
            run_command_with_sudo(f"rm -f {config_file}", password)

            with open(local_config_file, "w") as f:
                f.write(config)

            run_command_with_sudo(f"mv {local_config_file} {config_file}", password)
            create_symlink(config_file, password)

            with open(env_file_path, "a") as e:
                print(f"Adding docker port={port} to env file")
                e.write(f"{service.upper()}_PORT={port}\n")

        else:
            print(f"No host or port found for service {service}")
    
    print(f"All Nginx configurations and .env file have been created at {project_directory}")

def main():
    password = getpass.getpass("Enter your sudo password: ")

    run_command(f"rm -rf {WORKING_DIRECTORY}")

    for repo_url, image_name in REPO_TO_IMAGE.items():
        clone_dir = clone_repo(repo_url)
        build_docker_image(clone_dir, image_name)

    cloned_dir = clone_repo("git@github.com:sujithkanna/luffyhomes.git")

    run_command("sudo systemctl stop nginx")

    with open(os.path.join(cloned_dir, "nginx.yaml"), 'r') as file:
        data = yaml.safe_load(file)

    create_nginx_configs_and_env(data, cloned_dir, password)

    run_command("docker compose up -d", cloned_dir)
    run_command("sudo systemctl start nginx")

if __name__ == '__main__':
    main()
