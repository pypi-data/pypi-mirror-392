"""Network forensics utilities."""

import re
from typing import List, Dict, Optional
from ..exceptions import ForensicsError


def parse_pcap_basic(pcap_path: str) -> Dict[str, any]:
    """
    Basic PCAP file analysis (placeholder - requires scapy for full implementation).
    
    Args:
        pcap_path: Path to PCAP file
        
    Returns:
        Basic analysis results
    """
    # This is a basic implementation - would need scapy for full functionality
    raise ForensicsError("PCAP parsing requires scapy library (not implemented in basic version)")


def extract_http_requests(log_data: str) -> List[Dict[str, str]]:
    """
    Extract HTTP requests from log data.
    
    Args:
        log_data: HTTP log data as string
        
    Returns:
        List of HTTP requests
        
    Example:
        >>> logs = 'GET /admin HTTP/1.1\\nHost: example.com'
        >>> requests = extract_http_requests(logs)
    """
    http_requests = []
    
    # Simple HTTP request pattern
    request_pattern = r'(GET|POST|PUT|DELETE|HEAD|OPTIONS)\s+([^\s]+)\s+HTTP/[\d.]+'
    
    matches = re.finditer(request_pattern, log_data, re.IGNORECASE)
    
    for match in matches:
        method, path = match.groups()
        
        # Extract additional info from surrounding context
        line_start = log_data.rfind('\n', 0, match.start()) + 1
        line_end = log_data.find('\n', match.end())
        if line_end == -1:
            line_end = len(log_data)
        
        full_line = log_data[line_start:line_end]
        
        request_info = {
            'method': method.upper(),
            'path': path,
            'full_line': full_line.strip()
        }
        
        # Try to extract IP address
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        ip_match = re.search(ip_pattern, full_line)
        if ip_match:
            request_info['ip'] = ip_match.group()
        
        # Try to extract User-Agent
        ua_pattern = r'User-Agent:\s*([^\r\n]+)'
        ua_match = re.search(ua_pattern, log_data[match.end():match.end()+500], re.IGNORECASE)
        if ua_match:
            request_info['user_agent'] = ua_match.group(1).strip()
        
        http_requests.append(request_info)
    
    return http_requests


def extract_urls(text_data: str) -> List[str]:
    """
    Extract URLs from text data.
    
    Args:
        text_data: Text containing URLs
        
    Returns:
        List of extracted URLs
    """
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text_data, re.IGNORECASE)
    return list(set(urls))  # Remove duplicates


def extract_ip_addresses(text_data: str) -> List[str]:
    """
    Extract IP addresses from text data.
    
    Args:
        text_data: Text containing IP addresses
        
    Returns:
        List of IP addresses
    """
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    ips = re.findall(ip_pattern, text_data)
    
    # Validate IP addresses
    valid_ips = []
    for ip in ips:
        parts = ip.split('.')
        if all(0 <= int(part) <= 255 for part in parts):
            valid_ips.append(ip)
    
    return list(set(valid_ips))


def extract_email_addresses(text_data: str) -> List[str]:
    """
    Extract email addresses from text data.
    
    Args:
        text_data: Text containing email addresses
        
    Returns:
        List of email addresses
    """
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text_data)
    return list(set(emails))


def analyze_log_file(log_file_path: str) -> Dict[str, any]:
    """
    Analyze network log file for interesting patterns.
    
    Args:
        log_file_path: Path to log file
        
    Returns:
        Analysis results
    """
    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            log_data = f.read()
        
        analysis = {
            'http_requests': extract_http_requests(log_data),
            'urls': extract_urls(log_data),
            'ip_addresses': extract_ip_addresses(log_data),
            'email_addresses': extract_email_addresses(log_data),
            'file_size': len(log_data),
            'line_count': len(log_data.split('\n'))
        }
        
        return analysis
    
    except Exception as e:
        raise ForensicsError(f"Error analyzing network log: {e}")
