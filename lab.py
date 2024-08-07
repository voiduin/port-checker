# This file contains examples of how to use the port testing functions locally.
# It is intended for local experiments with the port testing library.

import argparse

from port_check_utils import check_port


def local_test(ip, port, protocol, conf_data):
    print("Testing Configuration:")
    print("  IP Address:        ", ip)
    print("  Port:              ", port)
    print("  Protocol:          ", protocol)
    print("  Confirmation data: ", conf_data if conf_data else "No data provided")


    # Use the updated check_port function to test the specified port, protocol and conf_data
    result, received_data = check_port(ip, port, protocol, conf_data)

    # Output the results to the console
    print("\nTest Result:")
    print(f"  {protocol.upper()} Port:      {result}")
    print("  Received data:", received_data if received_data else "Not Detected")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Test TCP and UDP ports on a given IP address, port, protocol, and optional conf_data.")
    parser.add_argument('--ip', type=str, default='192.168.1.1', help='IP address to test (default: 192.168.1.1)')
    parser.add_argument('--port', type=int, default=80, help='Port number to test (default: 80)')
    parser.add_argument('--protocol', type=str, default='tcp', help='Protocol to test (default: tcp), choose either "tcp" or "udp"')
    parser.add_argument('--conf_data', type=str, default=None, help='Optional confirmation data to send')

    args = parser.parse_args()

    local_test(args.ip, args.port, args.protocol, args.conf_data)
