#!/usr/bin/env python3
"""
Image processing module for photo-to-print pipeline.
Converts 2D images to 3D meshes with multiple methods.

Integrates G1 Print Pipeline's advanced photo-to-3D techniques.
"""

import argparse
from pathlib import Path
from g1_photo_to_3d import photo_to_3d, lithophane_from_photo, PhotoConfig


def image_to_mesh(
    image_path,
    output_path,
    mode="heightmap",
    width=50,
    height=50,
    scale_z=5
):
    """
    Convert an image to a 3D mesh.
    
    Args:
        image_path: Path to input image
        output_path: Path for output STL file
        mode: Conversion mode (heightmap, silhouette, revolution, lithophane)
        width: Model width in mm
        height: Model height in mm
        scale_z: Height/depth scale factor (mm)
    
    Returns:
        mesh: Generated trimesh object
    """
    config = PhotoConfig(
        target_width=width,
        max_depth=scale_z,
        mode=mode
    )
    
    mesh, info = photo_to_3d(image_path, output_path, config)
    return mesh, info


def image_to_lithophane(
    image_path,
    output_path,
    width=100,
    max_thickness=3.0,
    min_thickness=0.4
):
    """
    Generate a lithophane from an image.
    Perfect for backlit prints of photos.
    
    Args:
        image_path: Path to input image
        output_path: Path for output STL file
        width: Model width in mm
        max_thickness: Thickest point (dark areas) in mm
        min_thickness: Thinnest point (bright areas) in mm
    
    Returns:
        mesh: Generated trimesh object
        info: Metadata about the generation
    """
    return lithophane_from_photo(
        image_path,
        output_path,
        width_mm=width,
        max_thickness=max_thickness,
        min_thickness=min_thickness
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert image to 3D mesh')
    parser.add_argument('image', help='Input image file')
    parser.add_argument('-o', '--output', help='Output STL file (default: image.stl)')
    parser.add_argument('-m', '--mode', default='heightmap', 
                       choices=['heightmap', 'silhouette', 'revolution', 'lithophane'],
                       help='Conversion mode (default: heightmap)')
    parser.add_argument('-w', '--width', type=float, default=50, help='Model width in mm (default: 50)')
    parser.add_argument('-z', '--scale-z', type=float, default=5, help='Height scale in mm (default: 5)')
    
    args = parser.parse_args()
    
    if not args.output:
        args.output = Path(args.image).stem + '.stl'
    
    if args.mode == 'lithophane':
        mesh, info = image_to_lithophane(args.image, args.output, width=args.width)
    else:
        mesh, info = image_to_mesh(
            args.image,
            args.output,
            mode=args.mode,
            width=args.width,
            scale_z=args.scale_z
        )
    
    print(f"✓ {args.mode.capitalize()} conversion complete")
    print(f"  Output: {args.output}")
    print(f"  Vertices: {info['vertices']}")
    print(f"  Faces: {info['faces']}")
    print(f"  Size: {Path(args.output).stat().st_size / 1024:.1f} KB")
