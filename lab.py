# This file contains examples of how to use the port testing functions locally.
# It is intended for local experiments with the port testing library.

from port_check_utils import check_tcp_port, check_udp_port


def local_test():
    ip = "192.168.1.1"  # Example IP address
    port = 80  # Example port number

    print("Testing IP:", ip)
    print("Testing Port:", port)

    # Test TCP and UDP ports and store results in separate variables
    tcp_result = check_tcp_port(ip, port)
    udp_result = check_udp_port(ip, port)

    # Output the results to the console
    print("TCP Port Test Result:", tcp_result)
    print("UDP Port Test Result:", udp_result)

if __name__ == '__main__':
    local_test()
