"""Steganography utilities for CTF challenges."""

# Import text steganography functions
from .text import (
    hide_text_whitespace,
    extract_text_whitespace,
    zero_width_encode,
    zero_width_decode,
    hide_in_text_zero_width,
    extract_from_text_zero_width
)

# Import image steganography functions
from .image import (
    hide_text_lsb,
    extract_text_lsb,
    analyze_image
)

# Import audio steganography functions (placeholder)
from .audio import (
    hide_text_audio,
    extract_text_audio,
    analyze_audio_spectrum,
    detect_lsb_audio
)

__all__ = [
    # Text steganography
    'hide_text_whitespace',
    'extract_text_whitespace',
    'zero_width_encode',
    'zero_width_decode',
    'hide_in_text_zero_width',
    'extract_from_text_zero_width',
    
    # Image steganography
    'hide_text_lsb',
    'extract_text_lsb',
    'analyze_image',
    
    # Audio steganography (placeholder)
    'hide_text_audio',
    'extract_text_audio',
    'analyze_audio_spectrum',
    'detect_lsb_audio'
]