"""
Simple script to test if Interactive Brokers API ports are accessible.
"""

import socket
import time

def test_port(host, port):
    """Test if a port is open and accessible."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f"[SUCCESS] Port {port} is OPEN")
            return True
        else:
            print(f"[FAILED] Port {port} is CLOSED (error code: {result})")
            return False
    except Exception as e:
        print(f"[ERROR] Error testing port {port}: {e}")
        return False
    finally:
        sock.close()

if __name__ == "__main__":
    host = "127.0.0.1"
    ports_to_test = [
        (4001, "IB Gateway Live"),
        (4002, "IB Gateway Paper"),
        (7496, "TWS Live"),
        (7497, "TWS Paper"),
    ]
    
    print("Testing Interactive Brokers API ports...\n")
    
    open_ports = []
    
    for port, description in ports_to_test:
        print(f"Testing {description} port ({port}):")
        if test_port(host, port):
            open_ports.append((port, description))
        print("")
    
    if open_ports:
        print("\nOpen ports found:")
        for port, description in open_ports:
            print(f"- Port {port} ({description})")
        print("\nUse one of these open ports in your configuration.")
    else:
        print("\nNo open IB ports found.")
        
    print("\nTroubleshooting tips:")
    print("1. Make sure IB Gateway or TWS is running")
    print("2. Verify API settings (API -> Settings)")
    print("3. Check that 'Enable ActiveX and Socket Clients' is enabled")
    print("4. Ensure correct port is specified in configuration")
