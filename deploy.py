#!/usr/bin/env python3

import argparse
import os
import socket
import subprocess

import paramiko


def get_load_avg(ip, ssh_key_path):
    print(f"\n[*] Getting load average for {ip}")
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(
            hostname=ip,
            username="root",
            key_filename=ssh_key_path,
            timeout=5
        )

        stdin, stdout, stderr = ssh_client.exec_command("cat /proc/loadavg | awk '{print $1}'")
        load_avg = stdout.read().decode().strip()
        print(f"[*] Load avg: {load_avg}")
        return float(load_avg)

    except Exception as e:
        print(f"[*] Error connecting to {ip}: {e}")
        return float('inf')

    finally:
        ssh_client.close()


def generate_inventory(db_host, client_host, ssh_key_path):
    inventory_content = (
        "[postgres]\n"
        f"{db_host} ansible_user=root ansible_ssh_private_key_file={ssh_key_path}\n"
        "[client]\n"
        f"{client_host} ansible_user=root ansible_ssh_private_key_file={ssh_key_path}\n"
    )

    with open("inventory.ini", "w") as f:
        f.write(inventory_content.strip())

    print("[*] Generated inventory.ini:")
    print(inventory_content.strip())


def is_host_resolvable(hostname):
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.gaierror:
        return False


def resolve_hostname(host):
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        print(f"[!] Cannot resolve hostname: {host}")
        exit(1)


def main():
    parser = argparse.ArgumentParser(description="Parse IPs string")
    parser.add_argument("hosts", help="List of IPs separated by comma, example: 192.168.56.105,192.168.56.105")
    parser.add_argument("--key", required=True, help="Private SSH key path, example: ~/.ssh/deploy_key")
    parser.add_argument("--db_password", required=True, help="Password for PostgreSQL user 'student'")
    args = parser.parse_args()

    ssh_key_path = os.path.expanduser(args.key)
    if not os.path.exists(ssh_key_path):
        print(f"[!] SSH key not found: {ssh_key_path}")
        exit(1)

    print(f"[*] SSH-key path: {ssh_key_path}\n")

    hosts = [ip.strip() for ip in args.hosts.split(',')]
    if len(hosts) != 2:
        print(f"[!] Expected 2 IP addresses: {len(hosts)}")
        exit(1)

    print("[*] Got IP addresses:")
    for ip in hosts:
        if not is_host_resolvable(ip):
            print(f"[!] Host '{ip}' could not be resolved. Check DNS or /etc/hosts.")
            exit(1)

    db_password = args.db_password
    if not db_password:
        print(f"[!] Need to provide password for PostgreSQL user 'student'")
        exit(1)

    loads = {}
    for ip in hosts:
        loads[ip] = get_load_avg(ip, ssh_key_path)

    db_host = min(loads, key=loads.get)
    print(f"\n[✓] Selected host: {db_host}\n")

    client_host = [ip for ip in hosts if ip != db_host][0]
    client_ip = resolve_hostname(client_host)

    generate_inventory(db_host, client_host, ssh_key_path)

    subprocess.run([
        "ansible-playbook",
        "-i", "inventory.ini",
        "playbook.yaml",
        "--extra-vars", f"client_host={client_ip} db_host={db_host} db_user_password={db_password}",
    ], check=True)

    print("\n[✓] PostgreSQL installation completed successfully!\n")



if __name__ == "__main__":
    main()
