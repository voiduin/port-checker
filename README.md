# 1. General info
This project implements a "port checker" server in Python.
It is designed to verify port accessibility, such as checking\
if a custom SSH port is accessible before changing from the standard port 22.

# 2. Usage
When you start the server, you can check ports only on your current server.
- 101.101.101.101 is the server with the port checker.
- 202.202.202.202 is the client where you run curl.

 ```bash
$ curl -Ls 101.101.101.101:8000/check_port?port=80
{"ip":"202.202.202.202","port":"80","status":"not available"}
 ```

# 3. Live Server Access
You can access our server at `ip.ahub.dev` for real-time operations. For instance:
```bash
$ curl -Ls ip.ahub.dev:8000/check_port?port=80
{"ip":"92.118.113.41","port":"80","status":"not available"}
```