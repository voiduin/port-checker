import json
from collections import defaultdict
from datetime import datetime, timedelta

from flask import Flask, Response, jsonify, request
from scapy.all import IP, TCP, UDP, Raw, sr1

app = Flask(__name__)

# Dictionary to track request times by IP
request_times = defaultdict(list)

def check_tcp_port(ip, port, confirmation_data=None):
    pkt = IP(dst=ip)/TCP(dport=int(port), flags='S')
    if confirmation_data:
        pkt /= Raw(load=confirmation_data)
    resp = sr1(pkt, timeout=2, verbose=0)
    if resp is None:
        return "Filtered"
    elif resp.haslayer(TCP):
        if confirmation_data and confirmation_data in str(resp):
            return "Reachable and Verified"
        elif resp.getlayer(TCP).flags == 0x12:
            return "Reachable"
    return "Unreachable"

def check_udp_port(ip, port, confirmation_data=None):
    pkt = IP(dst=ip)/UDP(dport=int(port))
    if confirmation_data:
        pkt /= Raw(load=confirmation_data)
    resp = sr1(pkt, timeout=2, verbose=0)
    if resp is None:
        return "Reachable or Filtered"
    elif resp.haslayer(UDP):
        if confirmation_data and confirmation_data in str(resp):
            return "Reachable and Verified"
        return "Reachable"
    else:
        return "Unreachable"

def check_port(ip, port, protocol, confirmation_data=None):
    if protocol == 'tcp':
        return check_tcp_port(ip, port, confirmation_data)
    elif protocol == 'udp':
        return check_udp_port(ip, port, confirmation_data)
    else:
        raise ValueError("Unsupported protocol")

def is_rate_limited(ip):
    now = datetime.now()
    one_minute_ago = now - timedelta(minutes=1)
    times = request_times[ip]
    # Clear outdated records
    request_times[ip] = [time for time in times if time > one_minute_ago]
    if len(request_times[ip]) >= 4:
        earliest_time = min(request_times[ip])
        wait_time = (earliest_time + timedelta(minutes=1) - now).total_seconds()
        return True, wait_time
    request_times[ip].append(now)
    return False, 0

@app.route('/check_port', methods=['GET'])
def port_check():
    client_ip = request.remote_addr  # Get client IP
    port = request.args.get('port')
    protocol = request.args.get('protocol')
    confirmation_data = request.args.get('confirmation_data')

    if not port or not protocol:
        response = {'error': 'Port number and protocol are required'}
        return Response(json.dumps(response, indent=4), mimetype='application/json'), 400

    if confirmation_data and len(confirmation_data) > 20:
        response = {'error': 'Confirmation data too long. Maximum length is 20 characters.'}
        return Response(json.dumps(response, indent=4), mimetype='application/json'), 400

    protocol = protocol.lower()
    
    # Delay before processing the request - rate limiting up to 4 requests per minute
    # - First request without delay
    # - Second request with 1 second delay
    # - ... and so on
    rate_limited, wait_time = is_rate_limited(client_ip)
    if rate_limited:
        response = {'error': 'Too many requests. Please wait.', 'wait_time': f'{wait_time:.2f} seconds'}
        return Response(json.dumps(response, indent=4), mimetype='application/json'), 429

    try:
        status = check_port(client_ip, port, protocol, confirmation_data)
    except ValueError as e:
        response = {'error': str(e)}
        return Response(json.dumps(response, indent=4), mimetype='application/json'), 400

    response = {
        'you_ip': client_ip,
        'port': port,
        'protocol': protocol,
        'status': status
    }

    if confirmation_data:
        response['confirmation_data'] = confirmation_data

    return Response(json.dumps(response, indent=4), mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
