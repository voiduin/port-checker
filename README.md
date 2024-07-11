# 1. General info
This project implements a "port checker" server in Python.
It is designed to verify port accessibility, such as checking\
if a custom SSH port is accessible before changing from the standard port 22.

**Try now: Live Server Access**
You can access our server at `ip.ahub.dev` for real-time operations.
For instance:
```bash
[usr@client] $ CHECK_SERVER_ADDR='ip.ahub.dev'

[usr@client] $ curl -Ls "${CHECK_SERVER_ADDR}:8000/check_port?port=80&protocol=tcp"
{"port":"80","protocol":"tcp","status":"not available","you_ip":"202.202.202.202"}
```

## 2. Requirements
Installation or verification is required:
- Docker - A simplified variant can be installed via the following link and curl command.
- python3-pip
- flask
- gunicorn

Tested on Ubuntu 22.04:
```bash
    # Install Docker:
[usr@srv] $ curl -fsSL https://get.docker.com -o get-docker.sh && \
  sudo sh get-docker.sh && \
  rm get-docker.sh

    # Install other requirements:
[usr@srv] $ sudo apt install python3-pip
[usr@srv] $ pip install flask
[usr@srv] $ pip install gunicorn
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

# 5. Usage
When you start the server, you can check ports only on your current server.
- 101.101.101.101 is the server with the port checker.
- 202.202.202.202 is the client where you run curl.

Open you ports TCP and UDP on client:
```
    # TCP
[usr@client] $ nc -vl 3000

    # UDP
[usr@client] $ nc -vlu 3000
```

Then check you port accessable from internet:
```bash
[usr@client] $ CHECK_SERVER_ADDR='101.101.101.101'

[usr@client] $ curl -Ls "${CHECK_SERVER_ADDR}:8000/check_port?port=80&protocol=tcp"
{"port":"80","protocol":"tcp","status":"not available","you_ip":"202.202.202.202"}

[usr@client] $ curl -Ls "${CHECK_SERVER_ADDR}:8000/check_port?port=80&protocol=udp"
{"port":"80","protocol":"udp","status":"not available","you_ip":"202.202.202.202"}
```
