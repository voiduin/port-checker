import logging
from socket import AF_INET, SOCK_STREAM, socket
from typing import Optional, Tuple

from scapy.all import IP, TCP, UDP, Raw, send, sniff, sr1

logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s')

def check_tcp_port(
            ip: str,
            port: int,
            confirmation_data: Optional[str] = None
            ) -> Tuple[str, Optional[str]]:
    logging.info(f"Checking TCP port {port} on IP {ip} with confirmation data: {confirmation_data}")

    if confirmation_data:
        # Use socket lib for check with full connect
        try:
            with socket(AF_INET, SOCK_STREAM) as s:
                s.connect((ip, port))
                s.sendall(confirmation_data.encode())
                data = s.recv(1024)
                received_data = data.decode()

                if received_data == confirmation_data:
                    return ("Reachable and Verified", received_data)
                else:
                    return ("Reachable but Incorrect Data", received_data)
        except Exception as e:
            logging.error(f"Error connecting to {ip}:{port} with error: {str(e)}")
            return ("Not Reachable", None)
    else:
        # Use scapy lib for check without connection
        # Send SYN packet and wait SYN-ACK
        syn_packet = IP(dst=ip)/TCP(dport=int(port), flags="S")
        response = sr1(syn_packet, timeout=1, verbose=0)
        if response is None:
            return ("Filtered", None)
        elif response.haslayer(TCP) and (response.getlayer(TCP).flags & 0x12):  # Check correct flag SYN-ACK in answer
            return ("Reachable", None)
        else:
            return ("Unreachable", None)

def check_udp_port(
            ip: str,
            port: int,
            confirmation_data: Optional[str] = None
            ) -> Tuple[str, Optional[str]]:
    logging.info(f"Checking UDP port {port} on IP {ip} with confirmation data: {confirmation_data}")
    pkt = IP(dst=ip)/UDP(dport=int(port))
    received_data = None

    if confirmation_data:
        pkt /= Raw(load=confirmation_data)
    resp = sr1(pkt, timeout=2, verbose=0)
    if resp is None:
        logging.info(f"No response for UDP port {port} on IP {ip}")
        return "Reachable or Filtered", received_data
    else:
        logging.info(f"Response object: {resp.show(dump=True)}")

    if resp.haslayer(UDP):
        if resp.haslayer(Raw): # If we have any rcv data
            received_data = resp.getlayer(Raw).load[:20]  # Cut rcv data to 20 symbols like max len confirmation_data
            logging.info(f"Received data: {received_data}")

            # Check rcv string with conf.data
            if confirmation_data and confirmation_data in str(resp):
                logging.info(f"Port {port} on IP {ip} is reachable and verified with confirmation data")
                return "Reachable and Verified", received_data

        logging.info(f"Port {port} on IP {ip} is reachable")
        return "Reachable", received_data
    else:
        logging.info(f"Port {port} on IP {ip} is unreachable")
        return "Unreachable", received_data

def check_port(
            ip: str,
            port: int,
            protocol: str,
            confirmation_data: Optional[str] = None
            ) -> Tuple[str, Optional[str]]:
    logging.info(f"Checking port {port} with protocol {protocol} on IP {ip}")
    if protocol == 'tcp':
        status, received_data = check_tcp_port(ip, port, confirmation_data)
    elif protocol == 'udp':
        status, received_data = check_udp_port(ip, port, confirmation_data)
    else:
        raise ValueError("Unsupported protocol")
    logging.info(f"Status: {status}, Received Data: {received_data}")
    return status, received_data
