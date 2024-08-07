import logging
from socket import AF_INET, SOCK_STREAM, socket
from typing import Optional, Tuple

from scapy.all import IP, TCP, UDP, Raw, send, sniff, sr1


def check_tcp_port(ip: str, port: int, confirmation_data: Optional[str] = None) -> Tuple[str, Optional[str]]:
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
