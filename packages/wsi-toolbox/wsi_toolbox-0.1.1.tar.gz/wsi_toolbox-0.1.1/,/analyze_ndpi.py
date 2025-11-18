#!/usr/bin/env python3
import os
import sys
import tifffile
import struct
from pprint import pprint

def analyze_ndpi_structure(filepath):
    """Analyze NDPI file structure using tifffile"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {filepath}")
    print(f"File size: {os.path.getsize(filepath):,} bytes")
    print(f"{'='*60}\n")
    
    # Read with tifffile
    with tifffile.TiffFile(filepath) as tif:
        print("=== TIFF Structure ===")
        print(f"Number of pages: {len(tif.pages)}")
        
        # Basic info
        for i, page in enumerate(tif.pages[:5]):  # First 5 pages
            print(f"\nPage {i}:")
            print(f"  Shape: {page.shape}")
            print(f"  Dtype: {page.dtype}")
            print(f"  Compression: {page.compression}")
            print(f"  Photometric: {page.photometric}")
            print(f"  Planarconfig: {page.planarconfig}")
            if hasattr(page, 'resolution'):
                print(f"  Resolution: {page.resolution}")
            if hasattr(page, 'resolution_unit'):
                print(f"  Resolution unit: {page.resolution_unit}")
            
            # Tags
            print(f"  Tags ({len(page.tags)} total):")
            for tag in list(page.tags.values())[:10]:  # First 10 tags
                print(f"    {tag.name} ({tag.code}): {tag.value}")
        
        # IFD offsets
        print("\n=== IFD Offsets ===")
        for i, page in enumerate(tif.pages[:10]):
            print(f"Page {i}: offset = {page.offset}")
        
        # NDPI specific metadata
        print("\n=== NDPI Metadata ===")
        if hasattr(tif, 'ndpi_metadata'):
            print("NDPI metadata:", tif.ndpi_metadata)
        
        # Check for custom tags
        print("\n=== Custom/Unknown Tags ===")
        for i, page in enumerate(tif.pages[:3]):
            print(f"\nPage {i} custom tags:")
            for tag in page.tags.values():
                if tag.code >= 32768:  # Private tags
                    print(f"  Tag {tag.code}: {tag.name} = {tag.value[:100] if hasattr(tag.value, '__len__') else tag.value}")

def read_binary_header(filepath, size=1024):
    """Read and display binary header"""
    print("\n=== Binary Header (first 1KB) ===")
    with open(filepath, 'rb') as f:
        data = f.read(size)
        
        # Check TIFF magic number
        byte_order = data[:2]
        if byte_order == b'II':
            print("Byte order: Little-endian (Intel)")
            endian = '<'
        elif byte_order == b'MM':
            print("Byte order: Big-endian (Motorola)")
            endian = '>'
        else:
            print(f"Unknown byte order: {byte_order}")
            return
        
        # TIFF version (should be 42)
        version = struct.unpack(endian + 'H', data[2:4])[0]
        print(f"TIFF version: {version}")
        
        # First IFD offset
        first_ifd = struct.unpack(endian + 'I', data[4:8])[0]
        print(f"First IFD offset: {first_ifd}")
        
        # Display hex dump of first 256 bytes
        print("\nHex dump (first 256 bytes):")
        for i in range(0, min(256, len(data)), 16):
            hex_str = ' '.join(f'{b:02x}' for b in data[i:i+16])
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[i:i+16])
            print(f"{i:04x}: {hex_str:<48} {ascii_str}")

if __name__ == "__main__":
    # Analyze multiple NDPI files
    ndpi_files = [
        "./data/GB/Ex2557_17.ndpi",
    ]
    
    for filepath in ndpi_files:
        if os.path.exists(filepath):
            try:
                analyze_ndpi_structure(filepath)
                read_binary_header(filepath)
            except Exception as e:
                print(f"Error analyzing {filepath}: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"File not found: {filepath}")