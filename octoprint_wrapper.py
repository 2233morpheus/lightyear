#!/usr/bin/env python3
"""
OctoPrint wrapper module for photo-to-print pipeline.
Manages printer communication and job submission.
"""

import requests
import argparse
from pathlib import Path
import time


class OctoPrintClient:
    """Simple OctoPrint API client."""
    
    def __init__(self, host, api_key):
        """
        Initialize OctoPrint client.
        
        Args:
            host: OctoPrint host (e.g., 'http://192.168.178.47:5000')
            api_key: OctoPrint API key
        """
        self.host = host.rstrip('/')
        self.api_key = api_key
        self.headers = {'X-API-Key': api_key}
    
    def get_status(self):
        """Get printer status."""
        try:
            r = requests.get(f"{self.host}/api/printer", headers=self.headers, timeout=5)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            return {"error": str(e)}
    
    def upload_file(self, gcode_path, select=False, print_after=False):
        """
        Upload GCODE file to OctoPrint.
        
        Args:
            gcode_path: Path to GCODE file
            select: Auto-select after upload
            print_after: Auto-start print after upload
        """
        if not Path(gcode_path).exists():
            raise FileNotFoundError(f"GCODE file not found: {gcode_path}")
        
        with open(gcode_path, 'rb') as f:
            files = {'file': f}
            data = {'select': select, 'print': print_after}
            
            r = requests.post(
                f"{self.host}/api/files/local",
                headers=self.headers,
                files=files,
                data=data,
                timeout=30
            )
            r.raise_for_status()
            return r.json()
    
    def start_print(self):
        """Start printing current job."""
        r = requests.post(
            f"{self.host}/api/job",
            headers=self.headers,
            json={"command": "start"},
            timeout=5
        )
        r.raise_for_status()
        return r.json()
    
    def cancel_print(self):
        """Cancel current print job."""
        r = requests.post(
            f"{self.host}/api/job",
            headers=self.headers,
            json={"command": "cancel"},
            timeout=5
        )
        r.raise_for_status()
        return r.json()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload GCODE to OctoPrint')
    parser.add_argument('gcode', help='GCODE file to upload')
    parser.add_argument('--host', default='http://192.168.178.47:5000', help='OctoPrint host')
    parser.add_argument('--api-key', help='OctoPrint API key')
    parser.add_argument('--select', action='store_true', help='Auto-select after upload')
    parser.add_argument('--print', action='store_true', help='Auto-start print')
    
    args = parser.parse_args()
    
    if not args.api_key:
        raise ValueError("API key required (--api-key)")
    
    client = OctoPrintClient(args.host, args.api_key)
    
    # Check status
    status = client.get_status()
    print(f"Printer status: {status}")
    
    # Upload file
    result = client.upload_file(args.gcode, select=args.select, print_after=args.print)
    print(f"✓ Uploaded: {result}")
