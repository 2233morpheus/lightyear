#!/usr/bin/env python3
"""
Slicer wrapper module for photo-to-print pipeline.
Wraps PrusaSlicer CLI for GCODE generation.
"""

import subprocess
import argparse
from pathlib import Path


def slice_stl_to_gcode(
    stl_path,
    output_path,
    printer_profile="Ender 3",
    print_profile="0.2mm NORMAL",
    material_profile="PLA"
):
    """
    Slice STL file to GCODE using PrusaSlicer.
    
    Args:
        stl_path: Path to input STL file
        output_path: Path for output GCODE file
        printer_profile: Printer profile name
        print_profile: Print profile name
        material_profile: Material profile name
    """
    
    # Check if file exists
    if not Path(stl_path).exists():
        raise FileNotFoundError(f"STL file not found: {stl_path}")
    
    # Build PrusaSlicer command
    cmd = [
        "flatpak", "run", "com.prusa3d.PrusaSlicer",
        str(stl_path),
        "--export-gcode",
        "-o", str(output_path),
        "--printer-profile", printer_profile,
        "--print-profile", print_profile,
        "--material-profile", material_profile
    ]
    
    # Run slicer
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"PrusaSlicer failed: {result.stderr}")
    
    return result.stdout


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Slice STL to GCODE')
    parser.add_argument('stl', help='Input STL file')
    parser.add_argument('-o', '--output', help='Output GCODE file (default: model.gcode)')
    parser.add_argument('--printer', default='Ender 3', help='Printer profile')
    parser.add_argument('--print-profile', default='0.2mm NORMAL', help='Print profile')
    parser.add_argument('--material', default='PLA', help='Material profile')
    
    args = parser.parse_args()
    
    if not args.output:
        args.output = Path(args.stl).stem + '.gcode'
    
    output = slice_stl_to_gcode(
        args.stl,
        args.output,
        printer_profile=args.printer,
        print_profile=args.print_profile,
        material_profile=args.material
    )
    
    print(f"✓ Sliced {args.stl}")
    print(f"  → {args.output}")
    if Path(args.output).exists():
        print(f"  Size: {Path(args.output).stat().st_size / 1024:.1f} KB")
