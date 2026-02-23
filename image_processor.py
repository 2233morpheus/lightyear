#!/usr/bin/env python3
"""
Image processing module for photo-to-print pipeline.
Converts 2D images to 3D meshes using heightmap method.
"""

import argparse
from pathlib import Path
import numpy as np
from PIL import Image
import trimesh


def image_to_mesh(image_path, output_path, width=50, height=50, scale_z=5):
    """
    Convert an image to a 3D mesh using heightmap method.
    
    Args:
        image_path: Path to input image
        output_path: Path for output STL file
        width: Model width in mm
        height: Model height in mm (usually same as width for square)
        scale_z: Height scale factor (mm)
    """
    # Load and process image
    img = Image.open(image_path)
    
    # Convert to grayscale
    if img.mode != 'L':
        img = img.convert('L')
    
    # Resize to reasonable mesh resolution (100x100 grid)
    img = img.resize((100, 100), Image.Resampling.LANCZOS)
    
    # Convert to numpy array (0-1 range)
    height_data = np.array(img, dtype=np.float32) / 255.0
    
    # Create mesh vertices (grid)
    y_res, x_res = height_data.shape
    
    # Create X, Y coordinates
    x = np.linspace(0, width, x_res)
    y = np.linspace(0, height, y_res)
    xx, yy = np.meshgrid(x, y)
    
    # Z coordinates from height data
    zz = height_data * scale_z
    
    # Create vertices array (flatten and stack)
    vertices = np.column_stack([xx.flatten(), yy.flatten(), zz.flatten()])
    
    # Create faces (triangles connecting vertices)
    faces = []
    for i in range(y_res - 1):
        for j in range(x_res - 1):
            # Get indices of quad corners
            v0 = i * x_res + j
            v1 = v0 + 1
            v2 = v0 + x_res
            v3 = v2 + 1
            
            # Create two triangles per quad
            faces.append([v0, v1, v2])
            faces.append([v1, v3, v2])
    
    faces = np.array(faces)
    
    # Create mesh
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
    
    # Export to STL
    mesh.export(output_path)
    
    return mesh


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert image to 3D mesh')
    parser.add_argument('image', help='Input image file')
    parser.add_argument('-o', '--output', help='Output STL file (default: image.stl)')
    parser.add_argument('-w', '--width', type=float, default=50, help='Model width in mm (default: 50)')
    parser.add_argument('-z', '--scale-z', type=float, default=5, help='Height scale in mm (default: 5)')
    
    args = parser.parse_args()
    
    if not args.output:
        args.output = Path(args.image).stem + '.stl'
    
    mesh = image_to_mesh(args.image, args.output, width=args.width, scale_z=args.scale_z)
    print(f"✓ Converted {args.image}")
    print(f"  → {args.output}")
    print(f"  Vertices: {len(mesh.vertices)}")
    print(f"  Faces: {len(mesh.faces)}")
    print(f"  Size: {Path(args.output).stat().st_size / 1024:.1f} KB")
