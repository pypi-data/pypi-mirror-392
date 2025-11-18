# SubnetHostCount
Simple python to count hosts in a list of subnets and ip addresses


# CIDR Host Counter

This script reads a file containing IPv4 CIDR notations or individual IP addresses and calculates the total number of valid hosts. It excludes network and broadcast addresses for subnets, but counts single IPs (e.g., `10.0.0.5`) as one valid host.

## Features

- Accepts a file containing:
  - IPv4 CIDR ranges (e.g., `192.168.1.0/24`)
  - Individual IP addresses (e.g., `10.0.0.5`)
- Excludes network and broadcast addresses from the host count
- Ignores empty lines and lines starting with `#`
- Warns about invalid lines with a descriptive message
- Identifies duplicates (-D to list hosts appearing in multiple files)
- Calculates RFC1918 private vs public host counts (-r)

## Usage

### Prerequisites

Python 3.6+

### Command

```bash
python HostCount.py -d path/to/cidrs.txt
```
or
```bash
subnethostcount -d path/to/cidrs.txt
```

### 
Optional flags:
- `-D`, `--duplicates`  
  When processing a directory, list hosts that appear in more than one file and which files they appear in.

- `-r`, `--rfc1918`  
  Show how many hosts are in RFC1918 private address space vs how many are not (prints per-file and totals).

