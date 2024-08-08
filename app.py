import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta

from flask import Flask, Response, request

from port_check_utils import check_port

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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

    logging.info(f"Received request from {client_ip} for port {port} with protocol {protocol} and confirmation data {confirmation_data}")

    if not port or not protocol:
        error_message = 'Port number and protocol are required'
        logging.error(error_message)
        if output_format == 'json':
            response = {'error': error_message}
            json_response = json.dumps(response, indent=4) + "\n"
            return Response(json_response, mimetype='application/json'), 400
        else:
            response_text = f"Error: {error_message}"
            return Response(response_text, mimetype='text/plain'), 400

    if confirmation_data and len(confirmation_data) > 20:
        error_message = 'Confirmation data too long. Maximum length is 20 characters.'
        logging.error(error_message)
        if output_format == 'json':
            response = {'error': error_message}
            json_response = json.dumps(response, indent=4) + "\n"
            return Response(json_response, mimetype='application/json'), 400
        else:
            response_text = f"Error: {error_message}"
            return Response(response_text, mimetype='text/plain'), 400

    protocol = protocol.lower()
    
    # Delay before processing the request - rate limiting up to 4 requests per minute
    # - First request without delay
    # - Second request with 1 second delay
    # - ... and so on
    rate_limited, wait_time = is_rate_limited(client_ip)
    if rate_limited:
        error_message = f'Too many requests. Please wait.'
        if output_format == 'json':
            response = {'error': error_message, 'wait_time': f'{wait_time:.2f} seconds'}
            json_response = json.dumps(response, indent=4) + "\n"
            return Response(json_response, mimetype='application/json'), 429
        else:
            response_text = f"Error: {error_message} Wait time: {wait_time:.2f} seconds"
            return Response(response_text, mimetype='text/plain'), 429

    try:
        status, received_data = check_port(client_ip, port, protocol, confirmation_data)
    except ValueError as e:
        error_message = str(e)
        logging.error(error_message)
        if output_format == 'json':
            response = {'error': error_message}
            json_response = json.dumps(response, indent=4) + "\n"
            return Response(json_response, mimetype='application/json'), 400
        else:
            response_text = f"Error: {error_message}"
            return Response(response_text, mimetype='text/plain'), 400

    response = {
        'you_ip': client_ip,
        'scan_port': port,
        'scan_protocol': protocol,
        'port_status': status,
        'received_data': received_data if received_data else None
    }
    response_text = f"you_ip: {client_ip}\n"
    response_text += f"scan_port: {port}\n"
    response_text += f"scan_protocol: {protocol}\n"
    response_text += f"port_status: {status}\n"

    if confirmation_data:
        response['confirmation_data'] = confirmation_data
        response_text += f"confirmation_data: {confirmation_data}\n"

    response_text += f"received_data: {received_data if received_data else None}\n"

    logging.info(f"Response to client: {response}")

    if output_format == 'json':
        json_response = json.dumps(response, indent=4) + "\n"
        return Response(json_response, mimetype='application/json')
    else:
        return Response(response_text, mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
