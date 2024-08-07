import json
from collections import defaultdict
from datetime import datetime, timedelta

from flask import Flask, Response, request

from port_check_utils import check_port

app = Flask(__name__)

# Dictionary to track request times by IP
request_times = defaultdict(list)


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
    output_format = request.args.get('format', 'json')

    if not port or not protocol:
        if output_format == 'json':
            response = {'error': 'Port number and protocol are required'}
            json_response = json.dumps(response, indent=4) + "\n"
            return Response(json_response, mimetype='application/json'), 400
        else:
            response_text = "Error: Port number and protocol are required"
            return Response(response_text, mimetype='text/plain'), 400

    if confirmation_data and len(confirmation_data) > 20:
        if output_format == 'json':
            response = {'error': 'Confirmation data too long. Maximum length is 20 characters.'}
            json_response = json.dumps(response, indent=4) + "\n"
            return Response(json_response, mimetype='application/json'), 400
        else:
            response_text = "Error: Confirmation data too long. Maximum length is 20 characters."
            return Response(response_text, mimetype='text/plain'), 400

    protocol = protocol.lower()
    
    # Delay before processing the request - rate limiting up to 4 requests per minute
    # - First request without delay
    # - Second request with 1 second delay
    # - ... and so on
    rate_limited, wait_time = is_rate_limited(client_ip)
    if rate_limited:
        if output_format == 'json':
            response = {'error': 'Too many requests. Please wait.', 'wait_time': f'{wait_time:.2f} seconds'}
            json_response = json.dumps(response, indent=4) + "\n"
            return Response(json_response, mimetype='application/json'), 429
        else:
            response_text = f"Error: Too many requests. Please wait. Wait time: {wait_time:.2f} seconds"
            return Response(response_text, mimetype='text/plain'), 429

    try:
        status = check_port(client_ip, port, protocol, confirmation_data)
    except ValueError as e:
        if output_format == 'json':
            response = {'error': str(e)}
            json_response = json.dumps(response, indent=4) + "\n"
            return Response(json_response, mimetype='application/json'), 400
        else:
            response_text = f"Error: {str(e)}"
            return Response(response_text, mimetype='text/plain'), 400

    response = {
        'you_ip': client_ip,
        'scan_port': port,
        'scan_protocol': protocol,
        'port_status': status
    }
    response_text = f"you_ip: {client_ip}\n"
    response_text += f"scan_port: {port}\n"
    response_text += f"scan_protocol: {protocol}\n"
    response_text += f"port_status: {status}\n"

    if confirmation_data:
        response['confirmation_data'] = confirmation_data
        response_text += f"confirmation_data: {confirmation_data}\n"

    if output_format == 'json':
        json_response = json.dumps(response, indent=4) + "\n"
        return Response(json_response, mimetype='application/json')
    else:
        return Response(response_text, mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
