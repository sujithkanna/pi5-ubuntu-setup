Run this command to setup ubuntu server basic setup
```bash
wget -O initial_setup.sh https://raw.githubusercontent.com/sujithkanna/pi5-ubuntu-setup/refs/heads/main/initial_setup.sh | sudo bash
```

Run the following script to setup existing hdd mount points (Do this before docker setup)
```bash
wget -O- https://raw.githubusercontent.com/sujithkanna/pi5-ubuntu-setup/refs/heads/main/hdd_setup.py | python3
```

Ensure you have added your local system ssh to github to access private repos required for the below script to complete successfully
Run the following script to setup docker and nginx server
```bash
wget -O- https://raw.githubusercontent.com/sujithkanna/pi5-ubuntu-setup/refs/heads/main/server_setup.py | python3
```
