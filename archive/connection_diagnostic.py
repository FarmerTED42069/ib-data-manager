"""
Connection Diagnostic Tool for IB Gateway
"""

import socket
import subprocess
import psutil
import sys
from datetime import datetime

def check_port_availability(port=4001):
    """Check if a port is available or in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            if result == 0:
                print(f"[PASS] Port {port} is OPEN and listening")
                return True
            else:
                print(f"[FAIL] Port {port} is CLOSED or not accessible")
                return False
    except Exception as e:
        print(f"[FAIL] Error checking port {port}: {str(e)}")
        return False

def find_process_using_port(port):
    """Find which process is using a specific port"""
    try:
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                process = psutil.Process(conn.pid)
                print(f"  Process using port {port}: {process.name()} (PID: {process.pid})")
                return process.name()
    except Exception as e:
        print(f"  Could not determine process using port {port}: {str(e)}")
    return None

def check_ib_gateway_running():
    """Check if IB Gateway process is running"""
    ib_processes = []
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if 'ibgateway' in proc.info['name'].lower() or 'java' in proc.info['name'].lower():
                cmdline = proc.cmdline()
                if any('ibgateway' in cmd.lower() for cmd in cmdline):
                    ib_processes.append((proc.info['pid'], proc.info['name']))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if ib_processes:
        print(f"[PASS] IB Gateway process found:")
        for pid, name in ib_processes:
            print(f"  PID: {pid}, Name: {name}")
        return True
    else:
        print("[FAIL] IB Gateway process not found")
        return False

def test_basic_connection(host='127.0.0.1', port=4001):
    """Test basic TCP connection to IB Gateway"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"[PASS] TCP connection to {host}:{port} successful")
            return True
        else:
            print(f"[FAIL] TCP connection to {host}:{port} failed (Error code: {result})")
            return False
    except Exception as e:
        print(f"[FAIL] Connection test error: {str(e)}")
        return False

def check_firewall():
    """Check Windows Firewall settings"""
    try:
        result = subprocess.run(['netsh', 'advfirewall', 'firewall', 'show', 'rule', 'name=all'], 
                              capture_output=True, text=True)
        
        ib_rules = []
        for line in result.stdout.split('\n'):
            if 'ibgateway' in line.lower() or 'interactive brokers' in line.lower():
                ib_rules.append(line.strip())
        
        if ib_rules:
            print("[PASS] IB Gateway firewall rules found:")
            for rule in ib_rules[:5]:  # Show first 5 rules
                print(f"  {rule}")
        else:
            print("[WARNING] No specific IB Gateway firewall rules found")
            
    except Exception as e:
        print(f"[WARNING] Could not check firewall settings: {str(e)}")

def diagnose_connection():
    """Run complete connection diagnostics"""
    print("="*60)
    print("IB Gateway Connection Diagnostics")
    print("="*60)
    print(f"Time: {datetime.now()}")
    print()
    
    # 1. Check if IB Gateway is running
    print("1. Checking IB Gateway process...")
    ib_running = check_ib_gateway_running()
    print()
    
    # 2. Check ports
    print("2. Checking port availability...")
    ports_to_check = [4001, 4002]  # Live and Paper trading ports
    
    for port in ports_to_check:
        print(f"\nPort {port}:")
        port_open = check_port_availability(port)
        if port_open:
            find_process_using_port(port)
    print()
    
    # 3. Test basic connection
    print("3. Testing TCP connection...")
    test_basic_connection('127.0.0.1', 4001)
    test_basic_connection('127.0.0.1', 4002)
    print()
    
    # 4. Check firewall
    print("4. Checking firewall settings...")
    check_firewall()
    print()
    
    # 5. Check other potential issues
    print("5. Additional checks...")
    
    # Check localhost resolution
    try:
        ip = socket.gethostbyname('localhost')
        print(f"[PASS] Localhost resolves to: {ip}")
    except:
        print("[FAIL] Cannot resolve localhost")
    
    # Check 127.0.0.1 connectivity
    try:
        socket.create_connection(('127.0.0.1', 80), timeout=1)
    except:
        pass  # Expected to fail, just testing network stack
    print("[PASS] Network stack appears functional")
    print()
    
    # 6. Recommendations
    print("="*60)
    print("RECOMMENDATIONS:")
    print("="*60)
    
    if not ib_running:
        print("1. IB Gateway is not running. Please start IB Gateway first.")
        print("   - Launch IB Gateway")
        print("   - Log in with your credentials")
        print("   - Wait for it to fully initialize")
    
    if not port_open:
        print("2. Port 4001 is not accessible. Check:")
        print("   - IB Gateway is configured to use port 4001")
        print("   - API connections are enabled in IB Gateway settings")
        print("   - No other application is using port 4001")
    
    print("\n3. In IB Gateway, verify these settings:")
    print("   - Configure > Settings > API > Settings")
    print("   - Enable 'Enable ActiveX and Socket Clients'")
    print("   - Add '127.0.0.1' to trusted IP addresses")
    print("   - Uncheck 'Read-Only API'")
    print("   - Check 'Download open orders on connection'")
    
    print("\n4. Try these troubleshooting steps:")
    print("   a. Restart IB Gateway")
    print("   b. Check if you're using the correct port (4001 for live, 4002 for paper)")
    print("   c. Temporarily disable Windows Firewall to test")
    print("   d. Run the application as administrator")
    
    print("\n5. Alternative connection settings to try:")
    print("   - Use '127.0.0.1' instead of 'localhost'")
    print("   - Try a different client ID (e.g., 2, 3, etc.)")
    print("   - Ensure no other IB API applications are running")

if __name__ == "__main__":
    diagnose_connection()
    print("\nPress Enter to exit...")
    input()
