"""File analysis utilities."""

import os
import re
import struct
from typing import List, Dict, Optional
from ..exceptions import ForensicsError

# Common file signatures
FILE_SIGNATURES = {
    b'\xFF\xD8\xFF': 'JPEG',
    b'\x89PNG\r\n\x1a\n': 'PNG',
    b'GIF87a': 'GIF87a',
    b'GIF89a': 'GIF89a',
    b'RIFF': 'RIFF/WAV/AVI',
    b'%PDF': 'PDF',
    b'PK\x03\x04': 'ZIP',
    b'PK\x05\x06': 'ZIP (empty)',
    b'PK\x07\x08': 'ZIP (spanned)',
    b'\x7fELF': 'ELF',
    b'MZ': 'EXE/DLL',
    b'\xCA\xFE\xBA\xBE': 'Java Class',
    b'\x1f\x8b\x08': 'GZIP',
    b'BZh': 'BZIP2',
    b'\x50\x4b\x03\x04': 'ZIP',
    b'\x52\x61\x72\x21\x1a\x07\x00': 'RAR'
}


def extract_strings(file_path: str, min_length: int = 4, encoding: str = 'utf-8') -> List[str]:
    """
    Extract printable strings from a file.
    
    Args:
        file_path: Path to file
        min_length: Minimum string length
        encoding: Text encoding to use
        
    Returns:
        List of extracted strings
        
    Example:
        >>> strings = extract_strings('binary_file.exe', min_length=6)
        >>> print(len(strings))
    """
    if not os.path.exists(file_path):
        raise ForensicsError(f"File not found: {file_path}")
    
    strings = []
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # ASCII strings
        ascii_pattern = rb'[ -~]{' + str(min_length).encode() + rb',}'
        ascii_strings = re.findall(ascii_pattern, data)
        strings.extend([s.decode('ascii', errors='ignore') for s in ascii_strings])
        
        # Unicode strings (UTF-16)
        unicode_pattern = rb'(?:[ -~]\x00){' + str(min_length).encode() + rb',}'
        unicode_strings = re.findall(unicode_pattern, data)
        for s in unicode_strings:
            try:
                decoded = s.decode('utf-16le', errors='ignore')
                if len(decoded.strip()) >= min_length:
                    strings.append(decoded.strip())
            except:
                pass
    
    except Exception as e:
        raise ForensicsError(f"Error extracting strings: {e}")
    
    return list(set(strings))  # Remove duplicates


def get_file_signature(file_path: str) -> Dict[str, str]:
    """
    Identify file type based on magic bytes.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with file information
        
    Example:
        >>> info = get_file_signature('image.jpg')
        >>> print(info['type'])
        'JPEG'
    """
    if not os.path.exists(file_path):
        raise ForensicsError(f"File not found: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            header = f.read(16)
        
        detected_type = "Unknown"
        for signature, file_type in FILE_SIGNATURES.items():
            if header.startswith(signature):
                detected_type = file_type
                break
        
        file_size = os.path.getsize(file_path)
        
        return {
            'path': file_path,
            'size': file_size,
            'type': detected_type,
            'header_hex': header.hex(),
            'header_ascii': ''.join([chr(b) if 32 <= b <= 126 else '.' for b in header])
        }
    
    except Exception as e:
        raise ForensicsError(f"Error analyzing file signature: {e}")


def extract_metadata(file_path: str) -> Dict[str, any]:
    """
    Extract basic metadata from file.
    
    Args:
        file_path: Path to file
        
    Returns:
        Dictionary with metadata
    """
    if not os.path.exists(file_path):
        raise ForensicsError(f"File not found: {file_path}")
    
    try:
        stat_info = os.stat(file_path)
        
        metadata = {
            'filename': os.path.basename(file_path),
            'size_bytes': stat_info.st_size,
            'created': stat_info.st_ctime,
            'modified': stat_info.st_mtime,
            'accessed': stat_info.st_atime,
            'permissions': oct(stat_info.st_mode)[-3:],
        }
        
        # Add file signature info
        sig_info = get_file_signature(file_path)
        metadata.update(sig_info)
        
        return metadata
    
    except Exception as e:
        raise ForensicsError(f"Error extracting metadata: {e}")


def find_hidden_files(directory: str) -> List[str]:
    """
    Find hidden files in directory (files starting with .).
    
    Args:
        directory: Directory to search
        
    Returns:
        List of hidden files
    """
    if not os.path.exists(directory):
        raise ForensicsError(f"Directory not found: {directory}")
    
    hidden_files = []
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.startswith('.') and file not in ['.', '..']:
                    hidden_files.append(os.path.join(root, file))
    
    except Exception as e:
        raise ForensicsError(f"Error searching for hidden files: {e}")
    
    return hidden_files


def create_hex_dump(file_path: str, offset: int = 0, length: int = 256) -> str:
    """
    Create hex dump of file content.
    
    Args:
        file_path: Path to file
        offset: Starting offset
        length: Number of bytes to dump
        
    Returns:
        Hex dump string
    """
    if not os.path.exists(file_path):
        raise ForensicsError(f"File not found: {file_path}")
    
    try:
        with open(file_path, 'rb') as f:
            f.seek(offset)
            data = f.read(length)
        
        hex_dump_lines = []
        for i in range(0, len(data), 16):
            chunk = data[i:i+16]
            hex_part = ' '.join([f'{b:02x}' for b in chunk])
            ascii_part = ''.join([chr(b) if 32 <= b <= 126 else '.' for b in chunk])
            
            line = f"{offset + i:08x}  {hex_part:<47} |{ascii_part}|"
            hex_dump_lines.append(line)
        
        return '\n'.join(hex_dump_lines)
    
    except Exception as e:
        raise ForensicsError(f"Error creating hex dump: {e}")
