import argparse
import os
import json_leases_to_unbound
from argparse import ArgumentParser


def main_cli():
    parser = ArgumentParser()
    parser.add_argument('--log-level', help='set the logging level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    parser.add_argument('--source', help='source leases directory', default='/run/slaac-resolver/')
    parser.add_argument('--domain', help='default domain to use', default='lan')
    parser.add_argument('--unbound-server', help='unbound server to connect to (IP:port)', default=None)
    parser.add_argument('--config-file', help='unbound config file path', default=None)

    inputargs = parser.parse_args()
    json_leases_to_unbound.main(
        log_level=inputargs.log_level,
        source=inputargs.source,
        domain=inputargs.domain,
        unbound_server=inputargs.unbound_server,
        config_file=inputargs.config_file
    )