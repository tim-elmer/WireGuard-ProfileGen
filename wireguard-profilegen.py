#! /usr/local/bin/python3.11

from argparse import ArgumentParser
from configparser import ConfigParser
from copy import deepcopy
from subprocess import run

argument_parser = ArgumentParser(epilog='example: wireguard-profilegen.py peer 192.168.100.2/32 meaningofli.fe:51820 notarealpublickey= 192.168.100.0/24 -d "1.1.1.1, 1.0.0.1"')
argument_parser.add_argument('peer_name', help='The name of the peer. For file naming only. Note that this name and the tunnel name may not be longer than 15 characters.')
argument_parser.add_argument('peer_address', help='The IP address of the peer, including a /32-bit mask. e.g. 192.168.1.42/32')
argument_parser.add_argument('endpoint', help='The VPN endpoint (router) and its port. Can be an IP address or DNS name. e.g.: 42.42.42.42:51820, meaningofli.fe:51820')
argument_parser.add_argument('endpoint_public_key', help='The public key of the VPN endpoint.')
argument_parser.add_argument('split_tunnel_allowed_ips', help='A list of subnets which should be reachable via the split-tunnel configuration.')
argument_parser.add_argument('-d', '--dns-server', help='The DNS server (s) for the tunnel in a comma-separated list. Typically the VPN endpoint''s IP address.')
argument_parser.add_argument('-k', '--pre-shared-key', help='The pre-shared key for the tunnel, if set.')
argument_parser.add_argument('--full-tunnel-name', default='full', help='The name to append to the full-tunnel configuration file.')
argument_parser.add_argument('--split-tunnel-name', default='split', help='The name to append to the split-tunnel configuration file.')
arguments = argument_parser.parse_args()

print('Generating keys\n')
private_key = run(['wg', 'genkey'], capture_output=True, check=True, text=True).stdout.strip()
public_key = run(['wg', 'genkey'], capture_output=True, input=private_key, check=True, text=True).stdout.strip()
print(f'Public Key: {public_key}\n')

general_config = ConfigParser()
general_config['Interface'] = {
    'Address': arguments.peer_address,
    'PrivateKey': private_key
}
general_config['Peer'] = {
    'Endpoint': arguments.endpoint,
    'PublicKey': arguments.endpoint_public_key
}

if arguments.dns_server:
    general_config['Interface']['DNS'] = arguments.dns_server
if arguments.pre_shared_key:
    general_config['Peer']['PreSharedKey'] = arguments.pre_shared_key

full_tunnel_config = deepcopy(general_config)
full_tunnel_config['Peer']['AllowedIPs'] = '0.0.0.0/0, ::/0'

split_tunnel_config = deepcopy(general_config)
split_tunnel_config['Peer']['AllowedIPs'] = arguments.split_tunnel_allowed_ips

with open(f'{arguments.peer_name}-{arguments.full_tunnel_name}.config', 'x') as full_tunnel_file:
    full_tunnel_config.write(full_tunnel_file)
with open(f'{arguments.peer_name}-{arguments.split_tunnel_name}.config', 'x') as split_tunnel_file:
    split_tunnel_config.write(split_tunnel_file)

private_key = general_config = full_tunnel_config = split_tunnel_config = None