import ipaddress
import argparse
import os
from collections import defaultdict

# RFC1918 networks
RFC1918_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
]

def is_rfc1918(ip_str):
    try:
        ip = ipaddress.ip_address(ip_str)
        return any(ip in net for net in RFC1918_NETWORKS)
    except ValueError:
        return False

def extract_unique_hosts_from_file(file_path):
    unique_hosts = set()

    try:
        with open(file_path, 'r') as f:
            for line_number, line in enumerate(f, start=1):
                entry = line.strip()
                if not entry or entry.startswith("#"):
                    continue  # Skip empty lines or comments

                try:
                    if '/' not in entry:
                        entry += '/32'
                    network = ipaddress.ip_network(entry, strict=False)
                    if isinstance(network, ipaddress.IPv4Network):
                        if network.prefixlen == 32:
                            unique_hosts.add(str(network.network_address))
                        else:
                            # Add usable hosts only (skip network and broadcast)
                            for host in network.hosts():
                                unique_hosts.add(str(host))
                except ValueError as e:
                    print(f"WARNING: {file_path} Line {line_number} - Invalid entry '{entry}': {e}")
    except Exception as e:
        print(f"ERROR: Could not read file {file_path}: {e}")

    return unique_hosts

def main():
    parser = argparse.ArgumentParser(description="Count unique valid hosts from CIDRs or IPs in files.")
    parser.add_argument("file", nargs='?', help="Path to file containing CIDR ranges or IPs, one per line.")
    parser.add_argument("-d", "--directory", help="Directory of files to process.")
    parser.add_argument("-D", "--duplicates", action="store_true",
                        help="When processing a directory, list hosts that appear in more than one file and which files they appear in.")
    parser.add_argument("-r", "--rfc1918", action="store_true",
                        help="Optionally show how many hosts are in RFC1918 space vs not (per-file and totals).")
    args = parser.parse_args()

    if args.directory:
        grand_total_hosts = set()
        file_hosts_map = {}
        print(f"\nProcessing directory: {args.directory}")
        for entry in sorted(os.listdir(args.directory)):
            full_path = os.path.join(args.directory, entry)
            if os.path.isfile(full_path):
                file_hosts = extract_unique_hosts_from_file(full_path)
                file_hosts_map[entry] = file_hosts
                print(f"{entry}: {len(file_hosts)} unique hosts")
                grand_total_hosts.update(file_hosts)
        print(f"\nTotal unique hosts across all files: {len(grand_total_hosts)}")

        # Build host -> set(files) mapping once for both -D output and the duplicate note
        host_to_files = defaultdict(set)
        for fname, hosts in file_hosts_map.items():
            for h in hosts:
                host_to_files[h].add(fname)
        duplicates_map = {host: sorted(list(files)) for host, files in host_to_files.items() if len(files) > 1}
        duplicate_count = len(duplicates_map)

        # If -D not used, but duplicates exist, print a concise note that duplicates were found and are only counted once
        if not args.duplicates and duplicate_count > 0:
            print(f"\nNote: {duplicate_count} host(s) were found in more than one file but are only counted once in the total unique host count. Use -D to list them.")

        if args.rfc1918:
            print("\nRFC1918 breakdown per file:")
            for fname in sorted(file_hosts_map.keys()):
                hosts = file_hosts_map[fname]
                rfc_count = sum(1 for h in hosts if is_rfc1918(h))
                non_rfc = len(hosts) - rfc_count
                print(f"{fname}: {rfc_count} RFC1918, {non_rfc} non-RFC1918")

            total_rfc = sum(1 for h in grand_total_hosts if is_rfc1918(h))
            total_non_rfc = len(grand_total_hosts) - total_rfc
            print(f"\nTotals across all files: {total_rfc} RFC1918, {total_non_rfc} non-RFC1918")

        if args.duplicates:
            # Use the mapping we already built to list duplicates
            if not duplicates_map:
                print("\nNo duplicate hosts found between files.")
            else:
                print(f"\nDuplicate hosts found between files: {len(duplicates_map)} hosts\n")
                for host in sorted(duplicates_map.keys(), key=lambda x: tuple(int(p) for p in x.split('.'))):
                    files_list = ", ".join(duplicates_map[host])
                    print(f"{host}: {files_list}")

    elif args.file:
        unique_hosts = extract_unique_hosts_from_file(args.file)
        print(f"\nTotal unique hosts in {args.file} (excluding network and broadcast): {len(unique_hosts)}")

        if args.rfc1918:
            rfc_count = sum(1 for h in unique_hosts if is_rfc1918(h))
            non_rfc = len(unique_hosts) - rfc_count
            print(f"{args.file}: {rfc_count} RFC1918, {non_rfc} non-RFC1918")

    else:
        print("ERROR: Either a file or a directory must be specified.")
        parser.print_help()

if __name__ == "__main__":
    main()
