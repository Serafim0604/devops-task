#!/usr/bin/env python3

import argparse
import os

import paramiko


def test_ssh_connection(ip, ssh_key_path):
    print(f"Testing ssh connection to {ip}...")

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh_client.connect(
            hostname=ip,
            username="root",
            key_filename=ssh_key_path,
            timeout=5
        )

        stdin, stdout, stderr = ssh_client.exec_command("hostname")
        hostname = stdout.read().decode().strip()
        print(f"[*] Successfully connected to {ip}, hostname: {hostname}")

    except Exception as e:
        print(f"[*] Error connecting to {ip}: {e}")

    finally:
        ssh_client.close()



def generate_inventory(ip, ssh_key_path):
    inventory_content = (
        "[postgres]\n"
        f"{ip} ansible_user=root ansible_ssh_private_key_file={ssh_key_path}\n"
    )

    with open("inventory.ini", "w") as f:
        f.write(inventory_content.strip())

    print("[*] Generated inventory.ini:")
    print(inventory_content.strip())


def main():
    parser = argparse.ArgumentParser(description="Parse IPs string")
    parser.add_argument("hosts", help="List of IPs separated by comma, example: 192.168.56.105,192.168.56.105")
    parser.add_argument("--key", required=True, help="Private SSH key path, example: ~/.ssh/deploy_key")
    args = parser.parse_args()

    ssh_key_path = os.path.expanduser(args.key)
    if not os.path.exists(ssh_key_path):
        print(f"[!] SSH key not found: {ssh_key_path}")
        exit(1)

    print(f"[*] SSH-key path: {ssh_key_path}")

    hosts = [ip.strip() for ip in args.hosts.split(',')]
    if len(hosts) != 2:
        print(f"[!] Expected 2 IP addresses: {len(hosts)}")
        exit(1)

    print("[*] Got IP addresses:")
    for ip in hosts:
        test_ssh_connection(ip, ssh_key_path)

    selected_host = hosts[0]
    generate_inventory(selected_host, ssh_key_path)


if __name__ == "__main__":
    main()
