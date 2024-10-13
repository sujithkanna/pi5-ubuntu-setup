import os
import yaml
from utils import run_command, clone_repo, build_docker_image, create_nginx_configs_and_env

REPO_TO_IMAGE = {
    'git@github.com:sujithkanna/docker-qbittorrent.git': 'hsalf-qbittorrent:latest'
}

def main():
    for repo_url, image_name in REPO_TO_IMAGE.items():
        clone_dir = clone_repo(repo_url)
        build_docker_image(clone_dir, image_name)

    cloned_dir = clone_repo("git@github.com:sujithkanna/luffyhomes.git")

    run_command("sudo systemctl stop nginx")

    with open(os.path.join(cloned_dir, "nginx.yaml"), 'r') as file:
        data = yaml.safe_load(file)

    template_path = "nginx_template.j2"

    create_nginx_configs_and_env(data, cloned_dir, template_path)

    run_command("docker compose up -d", cloned_dir)
    run_command("sudo systemctl start nginx")

if __name__ == '__main__':
    main()