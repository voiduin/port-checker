# 1. General info
This project implements a "port checker" server in Python.
It is designed to verify port accessibility, such as checking\
if a custom SSH port is accessible before changing from the standard port 22.

**Try now: Live Server Access**\
You can access our server at `ip.ahub.dev` for real-time operations.
For instance:
```bash
[usr@client] $ CHECK_SERVER_ADDR='ip.ahub.dev'

[usr@client] $ curl -Ls "${CHECK_SERVER_ADDR}:8000/check_port?port=3000&protocol=tcp"
{"port":"3000","protocol":"tcp","status":"Filtered","you_ip":"202.202.202.202"}
```

**TCP Statuses**
- **Reachable**: The target port responds to the connection attempt with a SYN-ACK (flags 0x12), indicating that the port is actively listening and accessible.
- **Reachable and Verified**: If a specific payload (confirmation_data) is sent, and the exact same payload is received in response, this confirms that the data sent and received are identical. Although this option is more commonly used for UDP port checks, it can also be applied to TCP.
- **Unreachable**: Any response that is neither a timeout nor a SYN-ACK, indicating that the port is not accessible (e.g., an RST is received).
- **Filtered**: The port does not respond to the connection attempt within the specified timeout. This could mean that a firewall is filtering the traffic.

**UDP Statuses**
- **Reachable**: The target port responds to the UDP packet, indicating that the port is open.
- **Reachable and Verified**: If a specific payload (confirmation_data) is sent, and the exact same payload is received in response, this confirms that the data sent and received are identical. This status is particularly relevant for UDP port checks.
- **Unreachable**: Any specific response that indicates the port is not accessible.
- **Reachable or Filtered**: No response is received for the UDP packet within the specified timeout, making it unclear whether the port is open or being filtered.

## 2. Requirements
> This guide assumes you are starting with a __**clean installation of Ubuntu**__.\
> If some of the software components are already installed on your system,\
> you may skip the corresponding installation steps.

Before installation, the following requirements must be met:
- Defined ssh server for access
- Docker - A simplified variant can be installed via the following link and curl command.
- python3-pip
- flask - is a lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications
- gunicorn - 'Green Unicorn' is a Python WSGI HTTP Server for UNIX, a pre-fork worker model based HTTP server.

### 2.1. Initial Server Setup

Set up your server firewall before starting:
```bash
[usr@srv] $ sudo ufw allow 8000
[usr@srv] $ sudo ufw allow <!YOU_CUSTOM_SSH_PORT!>
```

Secure your SSH server for enhanced security. You can use the following script suite for setup:\
[linux-host-setup](https://github.com/voiduin/linux-host-setup)

Install Docker:
Use the convenience script from Docker to install Docker quickly:
```bash
[usr@srv] $ curl -fsSL https://get.docker.com -o get-docker.sh && \
            sudo sh get-docker.sh && \
            rm get-docker.sh
```

See docker dock:
https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script

Don't forget to add the user to the Docker group to avoid using sudo every docker command:
```bash
[usr@srv] $ sudo usermod -aG docker "${USER}"
```

You can check it was successful by doing
```bash
[usr@srv] $ grep docker /etc/group
```

And see something like this in one of the lines.:
```bash
docker:x:998:[user]
```

Then change your users group ID to docker (to avoid having to log out and log in again):
```bash
[usr@srv] $ newgrp docker
```

Enable the firewall:
```bash
[usr@srv] $ sudo ufw enable
```

### 2.2. Python libraries
Then install next software (Tested on Ubuntu 22.04):

```bash
[usr@srv] $ sudo apt install python3-pip
[usr@srv] $ pip install flask
[usr@srv] $ pip install gunicorn
[usr@srv] $ pip install scapy
```

This setup ensures that all necessary tools and configurations are in place for a secure and efficient development environment.

## 3. Downloading the Repository
To download the repository, you have a few options

### 3.1. Clone the Repository via git
If you have Git installed on your system, you can clone the repository using\
the following command in your terminal or command prompt:
```bash
  # Clone the repo via HTTPS (Do not use SSH because it requires configured credentials)
[usr@srv] $ REPO_URL='https://github.com/voiduin/port-checker.git'&&\
            GOAL_DIR_NAME='port-checker'&&\
            git clone "${REPO_URL}" "${GOAL_DIR_NAME}"
```
This will create a local copy of the repository on your machine.

### 3.2. Download as ZIP file
Alternatively, you can download the repository as a ZIP file.\
Simply navigate to the repository's page here and click on the "Code" button.\
Then select "Download ZIP" to save the ZIP file to your computer.\
After downloading, extract the contents of the ZIP file to access the repository files.

# 4. Deployment in Docker
```bash
[usr@srv] $ cd port-checker
[usr@srv] $ docker build -t port-checker-app .
[usr@srv] $ docker run -d -p 8000:8000 port-checker-app
```

Checking Container Logs
```bash
docker ps
    # See your docker container id

docker logs <!container_id!>
```

If the startup is successful, you should see the last line as "Booting worker ..."

```bash
[2024-07-10 22:17:11 +0000] [1] [INFO] Starting gunicorn 22.0.0
[2024-07-10 22:17:11 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
[2024-07-10 22:17:11 +0000] [1] [INFO] Using worker: sync
[2024-07-10 22:17:11 +0000] [7] [INFO] Booting worker with pid: 7
```

# 5. Usage
When you start the server, you can check ports only on your current server.
- 101.101.101.101 is the server with the port checker.
- 202.202.202.202 is the client where you run curl.

Open your ports TCP and UDP on the client for a simple test:
```bash
    # TCP
[usr@client] $ nc -vl 3000

    # UDP
[usr@client] $ nc -vlu 3000
```

## 5.1. Port Accessibility Check
Then check if your port is accessible from another machine on the internet:
```bash
[usr@client] $ CHECK_SERVER_ADDR='101.101.101.101'

[usr@client] $ curl -Ls "${CHECK_SERVER_ADDR}:8000/check_port?port=3000&protocol=tcp"
{"port":"3000","protocol":"tcp","status":"Reachable","you_ip":"202.202.202.202"}

[usr@client] $ curl -Ls "${CHECK_SERVER_ADDR}:8000/check_port?port=3000&protocol=udp"
{"port":"3000","protocol":"udp","status":"Reachable or Filtered","you_ip":"202.202.202.202"}
```

## 5.2. Rate limiting error
For security purposes, this service allows you to check only 4 ports per minute. After exceeding this limit, you will receive an error message along with the time you need to wait before the next check.

Error example:
```bash
[usr@client] $ curl -Ls "${CHECK_SERVER_ADDR}:8000/check_port?port=3000&protocol=udp"
{"error":"Too many requests. Please wait.","wait_time":"9.62 seconds"}

[usr@client] $ curl -Ls "${CHECK_SERVER_ADDR}:8000/check_port?port=3000&protocol=udp"
{"error":"Too many requests. Please wait.","wait_time":"9.26 seconds"}

[usr@client] $ curl -Ls "${CHECK_SERVER_ADDR}:8000/check_port?port=3000&protocol=udp"
{"error":"Too many requests. Please wait.","wait_time":"8.84 seconds"}
```
In this example, after the fourth request, the service returns an error indicating you have made too many requests and provides the specific wait time required before you can make another port check.
