#!/bin/zsh

# Get the current directory
CURRENT_DIR=$(pwd)

# Function to clone a repository
clone_repo() {
    local repo_url=$1

    # Extract the repo name (last part of the URL without .git)
    local repo_name=$(basename $repo_url .git)

    # Navigate to the current directory
    cd $CURRENT_DIR
    
    # Clone the repo if it doesn't exist, or pull updates if it does
    if [ -d "$CURRENT_DIR/$repo_name" ]; then
        echo "Repository '$repo_name' already exists, pulling updates..."
        cd $repo_name
        git pull
    else
        echo "Cloning repository '$repo_name'..."
        git clone $repo_url
        cd $repo_name
    fi

    # Return the cloned directory
    echo $CURRENT_DIR/$repo_name
}

# Function to build and run Docker Compose
build_and_run() {
    local cloned_dir=$1
    local build_name=$2

    # Navigate to the cloned repo directory
    cd $cloned_dir
    
    # Build the Docker containers (if Dockerfile is present)
    if [ -f "Dockerfile" ]; then
        echo "Building Docker image for '$(basename $cloned_dir)'..."
        docker build -t $(basename $build_name) .
    fi
}

# Example usage with repository URLs
repos=(
    "git@github.com:sujithkanna/docker-qbittorrent.git"
)
builds=(
    "hsalf-qbittorrent:latest"
)

for i in {1..${#repos[@]}}; do
    repo="${repos[$i-1]}"

    cloned_dir=$(clone_repo $repo)

    build_name="${builds[$i-1]}"

    build_and_run $cloned_dir $build_name
done

cd $CURRENT_DIR

cloned_dir=$(clone_repo "git@github.com:sujithkanna/luffyhomes.git")

cd $cloned_dir

sudo docker compose up -d
lazydocker