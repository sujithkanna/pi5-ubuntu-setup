#!/bin/bash
BLUE='\e[34m'
MAGENTA='\e[35m'
cprint() {
  local color=$MAGENTA
  local text=$1
  local RESET='\e[0m'

  echo -e "${color}${text}${RESET}"
}

read -p "Please enter your username for Git setup: " user_name
read -p "Please enter your email for Git setup: " email_address


sudo apt update

#Install zsh
cprint "Installing zsh"
sudo apt install -y zsh
cprint "Installing OhMyZsh"
sh -c "$(wget https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh -O -)" --skip-chsh #Skip is to skip auto switch terminal from bash to zsh


#Chrome
cprint  "Installing Chrome"
sudo apt install -y chromium-browser

#OpenSSH
cprint "Installing OpenSSH"
sudo apt install -y openssh-server
sudo systemctl start ssh
sudo systemctl enable ssh
sudo ufw allow ssh
sudo ufw reload

#Htop
cprint "Installing Htop"
sudo apt install -y htop

#Docker setup
cprint "Installing Docker"
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
echo "deb [arch=arm64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update
sudo apt install -y docker-ce
sudo usermod -aG docker $USER
sudo systemctl start docker
sudo systemctl enable docker

#Go lang (Required for LazyGit and LazyDocker)
cprint "Installing Go"
sudo apt install -y golang-go
cprint "Setting go path to bashrc"
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bashrc
cprint "Setting go path to zshrc"
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.zshrc

#LazyDocker
cprint "Installing LazyDocker"
go install github.com/jesseduffield/lazydocker@latest

#Git
cprint "Installing Git"
sudo apt install -y git
git config --global user.email "$email_address"
git config --global user.name "$user_name"

KEY_PATH="$HOME/.ssh/id_ed25519"
if [[ ! -f "$KEY_PATH" ]]; then
    # Generate the SSH key if it does not exist
    cprint "Creating ssh for email $email_address"
    ssh-keygen -t ed25519 -C "$email_address" -N "" -f "$KEY_PATH"
    cprint "SSH key generated at $KEY_PATH."
else
    cprint "SSH key already exists at $KEY_PATH."
fi
eval "$(ssh-agent -s)"
ssh-add "$KEY_PATH"
cprint "####################"
cprint "Copy the  following hash code and add it to Github"
cat ~/.ssh/id_ed25519.pub
cprint "####################"


#Lazy git
cprint "Installing LazyGit"
go install github.com/jesseduffield/lazygit@latest

#Nginx
cprint "Installing Nginx"
sudo apt install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx

#VsCode
cprint "Installing Vscode"
sudo apt install software-properties-common apt-transport-https wget
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=arm64] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
rm packages.microsoft.gpg
sudo apt update
sudo apt install code

#Static local IP
cprint "Setting up local static ip"
local_ip=$(hostname -I | awk '{print $1}')
cprint "Local IP: $local_ip"
sudo touch /etc/systemd/network/10-static-en.network
ip_configuration=$(cat <<EOF
[Match]
Name=eth0

[Network]
Address=$local_ip/24
Gateway=192.168.0.1
DNS=8.8.8.8
DNS=8.8.4.4
EOF
)
echo "$ip_configuration" | sudo tee /etc/systemd/network/10-static-en.network > /dev/null

sudo systemctl enable systemd-networkd
sudo systemctl start systemd-networkd

zsh