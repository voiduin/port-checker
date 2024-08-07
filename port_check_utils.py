from scapy.all import IP, TCP, UDP, Raw, sr1


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
