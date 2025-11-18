"""Memory analysis utilities."""

import re
from typing import List, Dict, Optional
from ..exceptions import ForensicsError


def find_patterns(memory_dump_path: str, pattern: str, context: int = 50) -> List[Dict[str, any]]:
    """
    Find patterns in memory dump with context.
    
    Args:
        memory_dump_path: Path to memory dump file
        pattern: Pattern to search for (regex)
        context: Number of bytes of context around match
        
    Returns:
        List of matches with context
    """
    try:
        with open(memory_dump_path, 'rb') as f:
            data = f.read()
        
        matches = []
        pattern_bytes = pattern.encode() if isinstance(pattern, str) else pattern
        
        for match in re.finditer(pattern_bytes, data):
            start_pos = max(0, match.start() - context)
            end_pos = min(len(data), match.end() + context)
            
            context_data = data[start_pos:end_pos]
            
            match_info = {
                'offset': match.start(),
                'match': match.group(),
                'context': context_data,
                'context_hex': context_data.hex(),
                'context_ascii': ''.join([chr(b) if 32 <= b <= 126 else '.' for b in context_data])
            }
            
            matches.append(match_info)
        
        return matches
    
    except Exception as e:
        raise ForensicsError(f"Error finding patterns in memory dump: {e}")


def extract_processes(memory_dump_path: str) -> List[str]:
    """
    Extract process names from memory dump (basic implementation).
    
    Args:
        memory_dump_path: Path to memory dump
        
    Returns:
        List of potential process names
    """
    try:
        with open(memory_dump_path, 'rb') as f:
            data = f.read()
        
        # Look for common executable patterns
        exe_pattern = rb'[a-zA-Z0-9_-]+\.exe'
        matches = re.findall(exe_pattern, data)
        
        # Convert to strings and remove duplicates
        processes = list(set([match.decode('ascii', errors='ignore') for match in matches]))
        
        return processes
    
    except Exception as e:
        raise ForensicsError(f"Error extracting processes: {e}")


def find_registry_keys(memory_dump_path: str) -> List[str]:
    """
    Find Windows registry keys in memory dump.
    
    Args:
        memory_dump_path: Path to memory dump
        
    Returns:
        List of registry keys
    """
    try:
        with open(memory_dump_path, 'rb') as f:
            data = f.read()
        
        # Registry key patterns
        reg_patterns = [
            rb'HKEY_LOCAL_MACHINE[^\x00]*',
            rb'HKEY_CURRENT_USER[^\x00]*',
            rb'HKEY_CLASSES_ROOT[^\x00]*',
            rb'SOFTWARE\\[^\x00]*'
        ]
        
        registry_keys = []
        
        for pattern in reg_patterns:
            matches = re.findall(pattern, data)
            registry_keys.extend([match.decode('ascii', errors='ignore') for match in matches])
        
        return list(set(registry_keys))
    
    except Exception as e:
        raise ForensicsError(f"Error finding registry keys: {e}")


def extract_urls_from_memory(memory_dump_path: str) -> List[str]:
    """
    Extract URLs from memory dump.
    
    Args:
        memory_dump_path: Path to memory dump
        
    Returns:
        List of URLs found in memory
    """
    try:
        with open(memory_dump_path, 'rb') as f:
            data = f.read().decode('ascii', errors='ignore')
        
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, data, re.IGNORECASE)
        
        return list(set(urls))
    
    except Exception as e:
        raise ForensicsError(f"Error extracting URLs from memory: {e}")


def search_memory_strings(memory_dump_path: str, search_terms: List[str]) -> Dict[str, List[Dict]]:
    """
    Search for specific strings in memory dump.
    
    Args:
        memory_dump_path: Path to memory dump
        search_terms: List of terms to search for
        
    Returns:
        Dictionary of search results
    """
    results = {}
    
    try:
        with open(memory_dump_path, 'rb') as f:
            data = f.read()
        
        for term in search_terms:
            term_bytes = term.encode() if isinstance(term, str) else term
            matches = []
            
            start = 0
            while True:
                pos = data.find(term_bytes, start)
                if pos == -1:
                    break
                
                # Get context around match
                context_start = max(0, pos - 100)
                context_end = min(len(data), pos + len(term_bytes) + 100)
                context = data[context_start:context_end]
                
                match_info = {
                    'offset': pos,
                    'context_ascii': ''.join([chr(b) if 32 <= b <= 126 else '.' for b in context]),
                    'context_hex': context.hex()
                }
                
                matches.append(match_info)
                start = pos + 1
            
            results[term] = matches
        
        return results
    
    except Exception as e:
        raise ForensicsError(f"Error searching memory strings: {e}")
