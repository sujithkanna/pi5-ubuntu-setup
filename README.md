Run this command to setup ubuntu server basic setup
```bash
wget https://raw.githubusercontent.com/sujithkanna/pi5-ubuntu-setup/refs/heads/main/initial_setup.sh && sudo bash initial_setup.sh && rm initial_setup.sh
```

Run the following script to setup existing hdd mount points (Do this before docker setup)
```bash
wget https://raw.githubusercontent.com/sujithkanna/pi5-ubuntu-setup/refs/heads/main/hdd_setup.py && sudo python3 hdd_setup.py && rm python3 hdd_setup.py
```

Ensure you have added your local system ssh to github to access private repos required for the below script to complete successfully
Run the following script to setup docker and nginx server
```bash
wget https://raw.githubusercontent.com/sujithkanna/pi5-ubuntu-setup/refs/heads/main/server_setup.py && sudo python3 server_setup.py && rm server_setup.py
```
