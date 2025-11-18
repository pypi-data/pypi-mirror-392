"""Forensics utilities for CTF challenges."""

# Import functions from files module
from .files import (
    extract_strings,
    get_file_signature,
    extract_metadata,
    find_hidden_files,
    create_hex_dump
)

# Import functions from network module
from .network import (
    parse_pcap_basic,
    extract_http_requests,
    extract_urls,
    extract_ip_addresses,
    extract_email_addresses,
    analyze_log_file
)

# Import functions from memory module
from .memory import (
    find_patterns,
    extract_processes,
    find_registry_keys,
    extract_urls_from_memory,
    search_memory_strings
)

__all__ = [
    # File analysis functions
    'extract_strings',
    'get_file_signature',
    'extract_metadata',
    'find_hidden_files',
    'create_hex_dump',
    # Network analysis functions
    'parse_pcap_basic',
    'extract_http_requests',
    'extract_urls',
    'extract_ip_addresses',
    'extract_email_addresses',
    'analyze_log_file',
    # Memory analysis functions
    'find_patterns',
    'extract_processes',
    'find_registry_keys',
    'extract_urls_from_memory',
    'search_memory_strings'
]