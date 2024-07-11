from flask import Flask, request, jsonify
import socket
import time
from collections import defaultdict
from datetime import datetime, timedelta

app = Flask(__name__)

# Dictionary to track request times by IP
request_times = defaultdict(list)

def check_tcp_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # Connection timeout
    result = sock.connect_ex((ip, int(port)))
    sock.close()
    return result == 0  # Returns True if the port is open

def check_udp_port(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    try:
        sock.sendto(b'', (ip, int(port)))
        sock.recvfrom(1024)
        return True
    except socket.timeout:
        return False
    except Exception:
        return False
    finally:
        sock.close()

def check_port(ip, port, protocol):
    if protocol == 'tcp':
        return check_tcp_port(ip, port)
    elif protocol == 'udp':
        return check_udp_port(ip, port)
    else:
        raise ValueError("Unsupported protocol")

def is_rate_limited(ip):
    now = datetime.now()
    one_minute_ago = now - timedelta(minutes=1)
    times = request_times[ip]
    # Clear outdated records
    request_times[ip] = [time for time in times if time > one_minute_ago]
    if len(request_times[ip]) >= 4:
        return True
    request_times[ip].append(now)
    return False

@app.route('/check_port', methods=['GET'])
def port_check():
    ip = request.remote_addr  # Get client IP
    port = request.args.get('port')
    protocol = request.args.get('protocol')
    if not port or not protocol:
        return jsonify({'error': 'Port number and protocol are required'}), 400

    protocol = protocol.lower()
    
    # Delay before processing the request
    # - First request without delay
    # - Second request with 1 second delay
    # - ... Then up to 4 req
    if is_rate_limited(ip):
        return jsonify({'error': 'Too many requests. Please wait.'}), 429

    if protocol == 'tcp':
        is_open = check_tcp_port(ip, port)
    elif protocol == 'udp':
        is_open = check_udp_port(ip, port)
    else:
        return jsonify({'error': 'Invalid protocol specified. Use tcp or udp.'}), 400

    status = 'available' if is_open else 'not available'
    return jsonify({
        'you_ip': ip,
        'port': port,
        'protocol': protocol,
        'status': status
    })

if __name__ == '__main__':
    app.run(debug=True)
