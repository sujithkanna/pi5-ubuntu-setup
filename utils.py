import os
import subprocess
from jinja2 import Template

def run_command(command, cwd=None):
    """Runs a Bash command and prints the output."""
    try:
        print(f"Executing command: {command}")
        subprocess.run(command, shell=True, check=True, text=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}")
    except Exception as e:
        print(f"Error: {e}")

def clone_repo(repo_url):
    """Clones the GitHub repository into the current directory."""
    current_dir = os.getcwd()
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
    certbot_command = f"sudo certbot certonly --standalone --preferred-challenges http -d {host}"
    run_command(certbot_command)

def create_symlink(config_file_path, sites_enabled_directory="/etc/nginx/sites-enabled"):
    """Create a symlink for the configuration file in the `sites-enabled` directory."""
    if not os.path.exists(sites_enabled_directory):
        os.makedirs(sites_enabled_directory)

    symlink_path = os.path.join(sites_enabled_directory, os.path.basename(config_file_path))

    if os.path.exists(symlink_path):
        os.remove(symlink_path)

    os.symlink(config_file_path, symlink_path)
    print(f"Symlink created at {symlink_path}")

def delete_and_create_env_file(env_file_path):
    """Delete the .env file if it exists, then create a fresh one."""
    if os.path.exists(env_file_path):
        os.remove(env_file_path)
        print(f"{env_file_path} has been cleared.")

def create_nginx_configs_and_env(data, project_directory, template_path):
    """Creates Nginx config files and a fresh .env file."""
    env_file_path = os.path.join(project_directory, '.env')
    delete_and_create_env_file(env_file_path)

    with open(template_path, 'r') as template_file:
        nginx_template = template_file.read()

    template = Template(nginx_template)
    
    for service, details in data.get('services', {}).items():
        host = details.get('host')
        port = details.get('port')
        
        if host and port:
            config = template.render(domain_name=host, port=port)
            config_file = f"/etc/nginx/sites-available/{host}"
            create_certificate(host)
            with open(config_file, "w") as f:
                f.write(config)
                create_symlink(config_file_path=config_file)

        else:
            print(f"No host or port found for service {service}")
    
    print(f"All Nginx configurations and .env file have been created at {project_directory}")