#!/usr/bin/env python3
"""
Photo-to-Print Pipeline
Convert images directly to 3D-printable GCODE.

Usage:
  python3 photo_to_print.py image.jpg
  python3 photo_to_print.py image.jpg --mode silhouette --width 80
  python3 photo_to_print.py portrait.jpg --mode lithophane --width 100
"""

import argparse
import sys
import time
from pathlib import Path
from image_processor import image_to_mesh, image_to_lithophane
from slicer_wrapper import slice_stl_to_gcode


def photo_to_print(
    image_path,
    mode="heightmap",
    width=50,
    scale_z=5,
    output_dir=None,
    printer_profile="Ender 3",
    print_profile="0.2mm NORMAL",
    material_profile="PLA",
    verbose=False
):
    """
    Complete pipeline: image → STL → GCODE
    
    Args:
        image_path: Input image file
        mode: Conversion mode (heightmap, silhouette, revolution, lithophane)
        width: Model width in mm
        scale_z: Z-axis scale factor (for non-lithophane modes)
        output_dir: Output directory
        printer_profile: Printer profile for slicing
        print_profile: Print profile for slicing
        material_profile: Material profile for slicing
        verbose: Print progress details
    
    Returns:
        Path to generated GCODE file
    """
    
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    if output_dir is None:
        output_dir = image_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    base_name = image_path.stem
    stl_path = output_dir / f"{base_name}_{mode}.stl"
    gcode_path = output_dir / f"{base_name}_{mode}.gcode"
    
    print(f"📷 Photo-to-Print Pipeline ({mode})")
    print(f"   Input:  {image_path}")
    
    # Step 1: Image → STL
    print(f"\n1️⃣  Converting image to 3D mesh ({mode} mode)...")
    start = time.time()
    
    if mode == 'lithophane':
        mesh, info = image_to_lithophane(str(image_path), str(stl_path), width=width)
    else:
        mesh, info = image_to_mesh(
            str(image_path),
            str(stl_path),
            mode=mode,
            width=width,
            scale_z=scale_z
        )
    
    elapsed = time.time() - start
    print(f"   ✓ STL generated: {stl_path}")
    print(f"   📊 {info['vertices']} vertices, {info['faces']} faces")
    print(f"   ⏱️  {elapsed:.1f}s")
    
    if verbose:
        print(f"\n   Details: {info}")
    
    # Step 2: STL → GCODE
    print(f"\n2️⃣  Slicing to GCODE...")
    start = time.time()
    slice_output = slice_stl_to_gcode(
        str(stl_path),
        str(gcode_path),
        printer_profile=printer_profile,
        print_profile=print_profile,
        material_profile=material_profile
    )
    elapsed = time.time() - start
    
    gcode_size = gcode_path.stat().st_size
    print(f"   ✓ GCODE generated: {gcode_path}")
    print(f"   📊 {gcode_size / 1024:.1f} KB")
    print(f"   ⏱️  {elapsed:.1f}s")
    
    if verbose:
        print(f"\n   Slicer output (first 500 chars):")
        print(f"   {slice_output[:500]}")
    
    print(f"\n✅ Pipeline complete!")
    print(f"   Ready to print: {gcode_path}")
    
    return gcode_path


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Photo-to-Print Pipeline: Convert images to 3D-printable GCODE',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  heightmap    - Fast height-based relief (default, best for details)
  silhouette   - Extrude object outline (good for clear subjects)
  revolution   - Surface of revolution (perfect for vases, bottles)
  lithophane   - Artistic thickness-based relief (backlit prints)

Examples:
  python3 photo_to_print.py photo.jpg
  python3 photo_to_print.py photo.jpg --mode silhouette --width 80
  python3 photo_to_print.py portrait.jpg --mode lithophane --width 100
  python3 photo_to_print.py vase_profile.jpg --mode revolution -w 60 -z 8
        """
    )
    
    parser.add_argument('image', help='Input image file')
    parser.add_argument('-m', '--mode', default='heightmap',
                       choices=['heightmap', 'silhouette', 'revolution', 'lithophane'],
                       help='Conversion mode (default: heightmap)')
    parser.add_argument('-w', '--width', type=float, default=50, help='Model width in mm (default: 50)')
    parser.add_argument('-z', '--scale-z', type=float, default=5, help='Z-axis scale in mm (default: 5)')
    parser.add_argument('-o', '--output', help='Output directory (default: same as image)')
    parser.add_argument('--printer', default='Ender 3', help='Printer profile (default: Ender 3)')
    parser.add_argument('--print-profile', default='0.2mm NORMAL', help='Print profile (default: 0.2mm NORMAL)')
    parser.add_argument('--material', default='PLA', help='Material profile (default: PLA)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        gcode = photo_to_print(
            args.image,
            mode=args.mode,
            width=args.width,
            scale_z=args.scale_z,
            output_dir=args.output,
            printer_profile=args.printer,
            print_profile=args.print_profile,
            material_profile=args.material,
            verbose=args.verbose
        )
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
