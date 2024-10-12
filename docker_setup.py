import os
import subprocess

# Define a dictionary that maps Docker repository URLs to image names
REPO_TO_IMAGE = {
    'git@github.com:sujithkanna/docker-qbittorrent.git': 'hsalf-qbittorrent:latest'
}

def run_command(command, cwd=None):
    """Runs a Bash command and prints the output."""
    try:
        print(f"Executing command: {command}")
        result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}")
    except Exception as e:
        print(f"Error: {e}")

def clone_repo(repo_url):
    """Clones the GitHub repository into the current directory."""
    # Get the current working directory
    current_dir = os.getcwd()
    # Get the repo name from the URL and set the directory for cloning
    repo_name = repo_url.split('/')[-1].replace('.git', '')
    clone_dir = os.path.join(current_dir, repo_name)
    
    # Run the git clone command
    command = f"git clone {repo_url} {clone_dir}"
    run_command(command)
    return clone_dir

def build_docker_image(dockerfile_dir, image_name):
    """Builds the Docker image using the Docker CLI."""
    command = f"docker build -t {image_name} {dockerfile_dir}"
    run_command(command)

def run_docker_compose(clone_dir):
    """Runs docker-compose up in the cloned directory."""
    command = "docker-compose up -d"
    run_command(command, cwd=clone_dir)  # Run the docker-compose up command in the last cloned repo directory

def main():
    for repo_url, image_name in REPO_TO_IMAGE.items():
        # Clone the repository into the current directory
        clone_dir = clone_repo(repo_url)
        
        # Build the Docker image
        build_docker_image(clone_dir, image_name)

    # Clone the last repo (luffyhomes) and run docker-compose up in it
    cloned_dir = clone_repo("git@github.com:sujithkanna/luffyhomes.git")
    
    # Run docker-compose up in the last cloned directory
    run_docker_compose(cloned_dir)

if __name__ == '__main__':
    main()