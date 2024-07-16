- [Port checker - General](#port-checker---general)
  - [1. Deployment](#1-deployment)
    - [1.1. Requirements](#11-requirements)
      - [Initial Server Setup](#initial-server-setup)
      - [Python libraries](#python-libraries)
    - [1.2. Downloading the Repository](#12-downloading-the-repository)
      - [Clone the Repository via git](#clone-the-repository-via-git)
      - [Download as ZIP file](#download-as-zip-file)
    - [1.3. Docker](#13-docker)
      - [Deployment](#deployment)
      - [Updating the Port Checker Application](#updating-the-port-checker-application)
  - [2. Usage](#2-usage)
    - [2.1. Port Accessibility Check](#21-port-accessibility-check)
    - [2.2. Rate limiting error](#22-rate-limiting-error)

# Port checker - General

## Why This Project is Useful for You

This project helps verify if your port is accessible from the external internet. It implements a "port checker" service in Python.

## IP Address Limitations

The port check can only be performed on the IP address of the device from which the request is made (only your current own external IP). **Setting a different IP address for the check is not supported.**

Usage Example (SSH):\
The tool can be used to check port accessibility, ensuring that specific ports\
like a custom SSH port are accessible before making changes, such as switching\
from the default port 22.

**Try now: Live Server Access**\
You can access our server at `ip.ahub.dev` for real-time operations.
For instance:

```console
[usr@client] $ CHECK_SERVER_ADDR='ip.ahub.dev'

    # Scanning port 80 using TCP protocol with a response in text format
[usr@client] $ curl -Ls "${CHECK_SERVER_ADDR}:8000/check_port?port=80&protocol=tcp&format=text"
you_ip: 202.202.202.202
scan_port: 80
scan_protocol: tcp
port_status: Filtered

    # Scanning port 3000 using UDP protocol with a response in JSON format (default format)
[usr@client] $ curl -Ls "${CHECK_SERVER_ADDR}:8000/check_port?port=3000&protocol=udp"
{
    "you_ip": "202.202.202.202",
    "scan_port": "3000",
    "scan_protocol": "udp",
    "port_status": "Reachable or Filtered"
}
```

**Request Parameters**

- **port** (required): The target port number on the client IP to check. It\
should be an integer representing the port number.
- **protocol** (required): The type of protocol to use for the port checkValid\
options are "tcp" or "udp".
- **confirmation_data** (optional): Additional data to send within the packet\
payload for confirming specific responses. String, maximum length of 20 characters.
- **format** (optional): Specifies the response format. Valid options are\
"json" (default) and "text". The "text" format is useful for easier parsing in\
shell scripts.

**Responses**

- **HTTP 200** (OK): Successfully retrieved the port status. The format of the response depends on the format parameter.
- **HTTP 400** (Bad Request): Required parameters are missing, or some parameters do not meet the criteria (e.g., confirmation_data too long).
- **HTTP 429** (Too Many Requests): The request has been rate-limited due to too many requests within a short time frame.

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

## 1. Deployment
### 1.1. Requirements

> This guide assumes you are starting with a __**clean installation of Ubuntu**__.\
> If some of the software components are already installed on your system,\
> you may skip the corresponding installation steps.

Before installation, the following requirements must be met:

- Defined ssh server for access
- Docker - A simplified variant can be installed via the following link and curl command.
- python3-pip
- flask - is a lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications
- gunicorn - 'Green Unicorn' is a Python WSGI HTTP Server for UNIX, a pre-fork worker model based HTTP server.

#### Initial Server Setup

Set up your server firewall before starting:

```console
[usr@srv] $ sudo ufw allow 8000
[usr@srv] $ sudo ufw allow <!YOU_CUSTOM_SSH_PORT!>
```

Secure your SSH server for enhanced security. You can use the following script suite for setup:\
[linux-host-setup](https://github.com/voiduin/linux-host-setup)

Install Docker:
Use the convenience script from Docker to install Docker quickly:

```console
[usr@srv] $ curl -fsSL https://get.docker.com -o get-docker.sh && \
            sudo sh get-docker.sh && \
            rm get-docker.sh
```

See docker dock:
https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script

Don't forget to add the user to the Docker group to avoid using sudo every docker command:

```console
[usr@srv] $ sudo usermod -aG docker "${USER}"
```

You can check it was successful by doing

```console
[usr@srv] $ grep docker /etc/group
```

And see something like this in one of the lines.:

```bash
docker:x:998:[user]
```

Then change your users group ID to docker (to avoid having to log out and log in again):

```console
[usr@srv] $ newgrp docker
```

Enable the firewall:

```console
[usr@srv] $ sudo ufw enable
```

#### Python libraries

Then install next software (Tested on Ubuntu 22.04):

```console
[usr@srv] $ sudo apt install python3-pip
[usr@srv] $ pip install flask
[usr@srv] $ pip install gunicorn
[usr@srv] $ pip install scapy
```

This setup ensures that all necessary tools and configurations are in place for a secure and efficient development environment.

### 1.2. Downloading the Repository

To download the repository, you have a few options

#### Clone the Repository via git

If you have Git installed on your system, you can clone the repository using\
the following command in your terminal or command prompt:

```console
  # Clone the repo via HTTPS (Do not use SSH because it requires configured credentials)
[usr@srv] $ REPO_URL='https://github.com/voiduin/port-checker.git'&&\
            GOAL_DIR_NAME='port-checker'&&\
            git clone "${REPO_URL}" "${GOAL_DIR_NAME}"
```
This will create a local copy of the repository on your machine.

#### Download as ZIP file

Alternatively, you can download the repository as a ZIP file.\
Simply navigate to the repository's page here and click on the "Code" button.\
Then select "Download ZIP" to save the ZIP file to your computer.\
After downloading, extract the contents of the ZIP file to access the repository files.

### 1.3. Docker

#### Deployment

```console
[usr@srv] $ cd port-checker
[usr@srv] $ docker build -t port-checker-app .
[usr@srv] $ docker run -d -p 8000:8000 port-checker-app
```

Checking Container Logs

```console
[usr@srv] $ docker ps
    # See your docker container id

[usr@srv] $ docker logs <!container_id!>
```

If the startup is successful, you should see the last line as "Booting worker ..."

```bash
[2024-07-10 22:17:11 +0000] [1] [INFO] Starting gunicorn 22.0.0
[2024-07-10 22:17:11 +0000] [1] [INFO] Listening at: http://0.0.0.0:8000 (1)
[2024-07-10 22:17:11 +0000] [1] [INFO] Using worker: sync
[2024-07-10 22:17:11 +0000] [7] [INFO] Booting worker with pid: 7
```

#### Updating the Port Checker Application

To update the Port Checker application, follow these steps:

```console
[usr@srv] $ docker ps | grep port-checker-app
[usr@srv] $ docker stop 2e30ef65a47d
[usr@srv] $ cd ..
[usr@srv] $ rm -rf port-checker/

[usr@srv] $ REPO_URL='https://github.com/voiduin/port-checker.git'&&\
            GOAL_DIR_NAME='port-checker'&&\
            git clone "${REPO_URL}" "${GOAL_DIR_NAME}"

[usr@srv] $ cd port-checker
[usr@srv] $ docker build -t port-checker-app .
[usr@srv] $ docker run -d -p 8000:8000 port-checker-app
```

This sequence stops the current running container, removes the old\
application directory, clones the latest version from the repository, and\
builds and runs the updated Docker container.

## 2. Usage

When you start the server, you can check ports only on your current server.

- 101.101.101.101 is the server with the port checker.
- 202.202.202.202 is the client where you run curl.

Open your ports TCP and UDP on the client for a simple test:

```console
    # TCP
[usr@client] $ nc -vl 3000

    # UDP
[usr@client] $ nc -vlu 3000
```

### 2.1. Port Accessibility Check

Then check if your port is accessible from another machine on the internet:

```console
[usr@client] $ CHECK_SERVER_ADDR='101.101.101.101'

[usr@client] $ curl -Ls "${CHECK_SERVER_ADDR}:8000/check_port?port=80&protocol=tcp&format=text"
you_ip: 202.202.202.202
scan_port: 80
scan_protocol: tcp
port_status: Filtered

[usr@client] $ curl -Ls "${CHECK_SERVER_ADDR}:8000/check_port?port=3000&protocol=udp"
{
    "you_ip": "202.202.202.202",
    "scan_port": "3000",
    "scan_protocol": "udp",
    "port_status": "Reachable or Filtered"
}
```

### 2.2. Rate limiting error

For security purposes, this service allows you to check only 4 ports per\
minute. After exceeding this limit, you will receive an error message along\
with the time you need to wait before the next check.

Error example:

```console
[usr@client] $ CHECK_SERVER_ADDR='101.101.101.101'

[usr@client] $ curl -Ls "${CHECK_SERVER_ADDR}:8000/check_port?port=3000&protocol=udp"
{
    "error": "Too many requests. Please wait.",
    "wait_time": "48.84 seconds"
}

[usr@client] $ curl -Ls "${CHECK_SERVER_ADDR}:8000/check_port?port=3000&protocol=udp"
{
    "error": "Too many requests. Please wait.",
    "wait_time": "26.13 seconds"
}
```

In this example, after the fourth request, the service returns an error\
indicating you have made too many requests and provides the specific wait\
time required before you can make another port check.
