#!/usr/bin/env python3

import argparse
import os


def main():
    parser = argparse.ArgumentParser(description="Parse IPs string")
    parser.add_argument("hosts", help="List of IPs separated by comma, example: 192.168.56.105,192.168.56.105")
    parser.add_argument("--key", required=True, help="Private SSH key path, example: ~/.ssh/deploy_key")
    args = parser.parse_args()

    ssh_key_path = os.path.expanduser(args.key)
    hosts = [ip.strip() for ip in args.hosts.split(',')]

    print("[*] Got IP addresses:")
    for ip in hosts:
        print(f"  - {ip}")
    
    print(f"[*] SSH-key path: {ssh_key_path}")

if __name__ == "__main__":
    main()