"""
G1 Photo-to-3D Pipeline
========================
Converts a photograph of an object into a printable 3D model.
Techniques:
  - Edge detection (Sobel + thresholding)
  - Contour extraction
  - Depth estimation from shading (shape-from-shading)
  - Silhouette extrusion
  - Relief/heightmap generation
  - Symmetry-based revolution
  - Lithophane (thickness-based relief)

No GPU required. Uses PIL, numpy, scipy, scikit-image.

Integrated into Lightyear from G1 Print Pipeline.
https://github.com/2233morpheus/print-pipeline
"""

import numpy as np
from PIL import Image, ImageFilter
import trimesh
import os
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class PhotoConfig:
    """Configuration for photo-to-3D conversion."""
    target_width: int = 200       # mm, physical width of output
    max_depth: float = 30.0       # mm, max depth/height
    resolution: int = 256         # image processing resolution
    smoothing: float = 1.0        # gaussian blur sigma
    edge_threshold: float = 0.15  # edge detection sensitivity
    extrude_base: float = 2.0     # mm, minimum base thickness
    mode: str = "heightmap"       # heightmap, silhouette, revolution, lithophane


def load_and_preprocess(image_path: str, config: PhotoConfig) -> np.ndarray:
    """Load image, convert to grayscale, resize, normalize."""
    img = Image.open(image_path)

    # Resize maintaining aspect ratio
    aspect = img.width / img.height
    if aspect >= 1:
        w = config.resolution
        h = int(config.resolution / aspect)
    else:
        h = config.resolution
        w = int(config.resolution * aspect)

    img = img.resize((w, h), Image.LANCZOS)
    gray = img.convert('L')

    arr = np.array(gray, dtype=np.float64) / 255.0
    return arr


def detect_edges(gray: np.ndarray, threshold: float = 0.15) -> np.ndarray:
    """Detect edges using Sobel + thresholding (pure numpy)."""
    kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
    ky = kx.T

    from scipy.ndimage import convolve
    gx = convolve(gray, kx)
    gy = convolve(gray, ky)
    magnitude = np.sqrt(gx ** 2 + gy ** 2)
    magnitude /= magnitude.max() + 1e-8

    edges = (magnitude > threshold).astype(np.float64)
    return edges


def extract_contours(edges: np.ndarray) -> list:
    """Extract contour polygons from edge image using scikit-image."""
    try:
        from skimage.measure import find_contours
        contours = find_contours(edges, 0.5)
        return contours
    except ImportError:
        return _fallback_contours(edges)


def _fallback_contours(edges):
    """Simple contour extraction without skimage."""
    contours = []
    visited = np.zeros_like(edges, dtype=bool)
    ys, xs = np.where(edges > 0.5)

    for start_idx in range(len(ys)):
        y, x = ys[start_idx], xs[start_idx]
        if visited[y, x]:
            continue
        path = []
        cy, cx = y, x
        for _ in range(5000):
            if visited[cy, cx]:
                break
            visited[cy, cx] = True
            path.append([cy, cx])
            found = False
            for dy in [-1, 0, 1]:
                for dx in [-1, 0, 1]:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < edges.shape[0] and 0 <= nx < edges.shape[1]:
                        if edges[ny, nx] > 0.5 and not visited[ny, nx]:
                            cy, cx = ny, nx
                            found = True
                            break
                if found:
                    break
            if not found:
                break
        if len(path) >= 10:
            contours.append(np.array(path))

    return contours


def depth_from_shading(gray: np.ndarray, smoothing: float = 1.0) -> np.ndarray:
    """Estimate depth from image brightness (shape-from-shading)."""
    from scipy.ndimage import gaussian_filter
    depth = gaussian_filter(gray, sigma=smoothing)
    mean_border = np.mean([
        depth[0, :].mean(), depth[-1, :].mean(),
        depth[:, 0].mean(), depth[:, -1].mean()
    ])
    if mean_border > 0.5:
        depth = 1.0 - depth
    return depth


def heightmap_to_mesh(depth: np.ndarray, config: PhotoConfig) -> trimesh.Trimesh:
    """Convert depth/heightmap to a 3D mesh (relief surface + flat base)."""
    h, w = depth.shape
    scale_x = config.target_width / w
    scale_y = scale_x
    scale_z = config.max_depth

    ys, xs = np.mgrid[0:h, 0:w]
    verts_top = np.column_stack([
        xs.ravel() * scale_x,
        ys.ravel() * scale_y,
        depth.ravel() * scale_z + config.extrude_base,
    ])

    verts_bottom = np.column_stack([
        xs.ravel() * scale_x,
        ys.ravel() * scale_y,
        np.zeros(h * w),
    ])

    verts = np.vstack([verts_top, verts_bottom])
    n = h * w

    faces = []
    for j in range(h - 1):
        for i in range(w - 1):
            idx = j * w + i
            faces.append([idx, idx + 1, idx + w])
            faces.append([idx + 1, idx + w + 1, idx + w])

    for j in range(h - 1):
        for i in range(w - 1):
            idx = n + j * w + i
            faces.append([idx, idx + w, idx + 1])
            faces.append([idx + 1, idx + w, idx + w + 1])

    for i in range(w - 1):
        faces.append([i, i + 1, n + i])
        faces.append([i + 1, n + i + 1, n + i])
    for i in range(w - 1):
        top = (h - 1) * w + i
        bot = n + (h - 1) * w + i
        faces.append([top, bot, top + 1])
        faces.append([top + 1, bot, bot + 1])
    for j in range(h - 1):
        top = j * w
        bot = n + j * w
        faces.append([top, bot, top + w])
        faces.append([top + w, bot, bot + w])
    for j in range(h - 1):
        top = j * w + (w - 1)
        bot = n + j * w + (w - 1)
        faces.append([top, top + w, bot])
        faces.append([top + w, bot + w, bot])

    mesh = trimesh.Trimesh(vertices=verts, faces=np.array(faces))
    mesh.fix_normals()
    return mesh


def silhouette_to_mesh(gray: np.ndarray, config: PhotoConfig, threshold: float = 0.4) -> trimesh.Trimesh:
    """Extrude the silhouette of an object into a 3D mesh."""
    from scipy.ndimage import gaussian_filter, binary_fill_holes
    smooth = gaussian_filter(gray, sigma=1.0)

    border_mean = np.mean([
        smooth[0, :].mean(), smooth[-1, :].mean(),
        smooth[:, 0].mean(), smooth[:, -1].mean()
    ])
    if border_mean > 0.5:
        mask = smooth < threshold
    else:
        mask = smooth > (1 - threshold)

    mask = binary_fill_holes(mask)

    try:
        from skimage.measure import find_contours
        contours = find_contours(mask.astype(float), 0.5)
    except ImportError:
        contours = _fallback_contours(mask.astype(float))

    if not contours:
        return heightmap_to_mesh(depth_from_shading(gray), config)

    largest = max(contours, key=len)
    h, w = gray.shape
    scale = config.target_width / w

    poly_2d = largest[:, ::-1] * scale
    try:
        path = trimesh.path.Path2D(vertices=poly_2d,
                                    entities=[trimesh.path.entities.Line(list(range(len(poly_2d))))])
        mesh = path.extrude(config.max_depth)
    except Exception:
        return heightmap_to_mesh(depth_from_shading(gray), config)

    return mesh


def revolution_to_mesh(gray: np.ndarray, config: PhotoConfig, axis: str = 'center') -> trimesh.Trimesh:
    """Create a surface of revolution from the object's profile."""
    edges = detect_edges(gray)
    contours = extract_contours(edges)

    if not contours:
        return heightmap_to_mesh(depth_from_shading(gray), config)

    largest = max(contours, key=len)
    h, w = gray.shape
    scale = config.target_width / w

    profile_pts = largest[:, ::-1] * scale
    order = np.argsort(profile_pts[:, 1])
    profile_pts = profile_pts[order]

    center_x = config.target_width / 2
    right_mask = profile_pts[:, 0] >= center_x
    if np.sum(right_mask) < 3:
        right_mask = profile_pts[:, 0] >= np.median(profile_pts[:, 0])

    profile = profile_pts[right_mask]
    if len(profile) < 3:
        return heightmap_to_mesh(depth_from_shading(gray), config)

    radii = np.abs(profile[:, 0] - center_x)
    heights = profile[:, 1]

    heights = (heights - heights.min())
    if heights.max() > 0:
        heights = heights / heights.max() * config.max_depth

    n_pts = len(radii)
    n_angles = 32
    angles = np.linspace(0, 2 * np.pi, n_angles, endpoint=False)

    verts = []
    for i in range(n_pts):
        for a in angles:
            x = radii[i] * np.cos(a)
            y = radii[i] * np.sin(a)
            z = heights[i]
            verts.append([x, y, z])

    verts = np.array(verts)
    faces = []
    for i in range(n_pts - 1):
        for j in range(n_angles):
            j2 = (j + 1) % n_angles
            v00 = i * n_angles + j
            v01 = i * n_angles + j2
            v10 = (i + 1) * n_angles + j
            v11 = (i + 1) * n_angles + j2
            faces.append([v00, v10, v01])
            faces.append([v01, v10, v11])

    mesh = trimesh.Trimesh(vertices=verts, faces=np.array(faces))
    mesh.fix_normals()
    return mesh


def photo_to_3d(image_path: str, output_stl: str, config: PhotoConfig = None) -> Tuple[trimesh.Trimesh, dict]:
    """
    Main entry point: photo → 3D printable mesh.
    
    Args:
        image_path: Path to input photo
        output_stl: Path to save STL
        config: Conversion configuration
    
    Returns: (mesh, info_dict)
    """
    if config is None:
        config = PhotoConfig()

    gray = load_and_preprocess(image_path, config)

    if config.mode == "heightmap":
        depth = depth_from_shading(gray, config.smoothing)
        mesh = heightmap_to_mesh(depth, config)
    elif config.mode == "silhouette":
        mesh = silhouette_to_mesh(gray, config)
    elif config.mode == "revolution":
        mesh = revolution_to_mesh(gray, config)
    else:
        depth = depth_from_shading(gray, config.smoothing)
        mesh = heightmap_to_mesh(depth, config)

    mesh.fix_normals()
    if not mesh.is_watertight:
        trimesh.repair.fill_holes(mesh)
        trimesh.repair.fix_winding(mesh)

    os.makedirs(os.path.dirname(output_stl) or '.', exist_ok=True)
    mesh.export(output_stl)

    info = {
        'mode': config.mode,
        'vertices': len(mesh.vertices),
        'faces': len(mesh.faces),
        'watertight': mesh.is_watertight,
        'bounds_mm': mesh.extents.tolist(),
        'volume_mm3': float(mesh.volume) if mesh.is_watertight else 0,
    }

    return mesh, info


def lithophane_from_photo(
    image_path: str,
    output_stl: str,
    width_mm: float = 100,
    max_thickness: float = 3.0,
    min_thickness: float = 0.4,
    resolution: int = 200,
) -> Tuple[trimesh.Trimesh, dict]:
    """Generate a lithophane from a photo."""
    img = Image.open(image_path).convert('L')
    aspect = img.height / img.width
    w = resolution
    h = int(resolution * aspect)
    img = img.resize((w, h), Image.LANCZOS)
    gray = np.array(img, dtype=np.float64) / 255.0

    thickness = max_thickness - gray * (max_thickness - min_thickness)

    config = PhotoConfig(
        target_width=width_mm,
        max_depth=max_thickness,
        resolution=resolution,
        extrude_base=0,
    )

    thickness = thickness[::-1]

    mesh = heightmap_to_mesh(thickness, config)
    mesh.fix_normals()

    os.makedirs(os.path.dirname(output_stl) or '.', exist_ok=True)
    mesh.export(output_stl)

    height_mm = width_mm * aspect
    info = {
        'mode': 'lithophane',
        'width_mm': width_mm,
        'height_mm': round(height_mm, 1),
        'thickness_range': f"{min_thickness}-{max_thickness}mm",
        'vertices': len(mesh.vertices),
        'faces': len(mesh.faces),
        'print_orientation': 'vertical (standing up) for best detail',
        'recommended_settings': {
            'layer_height': 0.12,
            'infill': '100%',
            'walls': 1,
            'material': 'white PLA or natural PLA',
            'speed': '30mm/s',
        }
    }

    return mesh, info
