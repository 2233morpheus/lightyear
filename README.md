# 🚀 Lightyear - Photo to 3D Print Pipeline

Convert your photos directly to 3D-printable GCODE in seconds.

**Image → 3D Model → Sliced GCODE → Print**

## Vision

Remove the barriers to 3D printing. You shouldn't need to know CAD, mesh topology, or slicing parameters. Point your camera at something, and get a printable file. That's the goal.

## Features

✅ **Image to 3D Mesh** - Heightmap-based conversion (fast, no AI needed)  
✅ **Automatic Slicing** - PrusaSlicer CLI integration  
✅ **One-Command Pipeline** - `photo_to_print.py image.jpg`  
✅ **Modular Design** - Use individual modules or the full pipeline  
✅ **Printer-Ready** - Outputs valid GCODE for Ender 3 V2 and compatible printers  

## Quick Start

### Installation

```bash
# Clone repo
git clone https://github.com/2233morpheus/lightyear.git
cd lightyear

# Create venv with dependencies
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install numpy pillow trimesh requests

# Install PrusaSlicer (required for slicing)
# On Ubuntu/Debian:
sudo apt install prusa-slicer
# Or via Flatpak:
flatpak install flathub com.prusa3d.PrusaSlicer
```

### Usage

**One-liner - full pipeline:**
```bash
python3 photo_to_print.py photo.jpg
```

Output: `photo.gcode` (ready to print!)

**Customized settings:**
```bash
python3 photo_to_print.py photo.jpg --width 80 --scale-z 8 --printer "Ender 3"
```

**Using individual modules:**

```bash
# Just convert image to STL
python3 image_processor.py photo.jpg -o model.stl --width 50 --scale-z 5

# Just slice STL to GCODE
python3 slicer_wrapper.py model.stl -o model.gcode --printer "Ender 3"

# Upload to OctoPrint (when printer is online)
python3 octoprint_wrapper.py model.gcode --host http://192.168.178.47:5000 --api-key YOUR_KEY --print
```

## Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `--width` | 50mm | Model base width |
| `--scale-z` | 5mm | Height exaggeration (smaller = flatter) |
| `--printer` | "Ender 3" | Printer profile in PrusaSlicer |
| `--print-profile` | "0.2mm NORMAL" | Layer height + speed preset |
| `--material` | "PLA" | Material type for temp/speed |

## Examples

```bash
# Small detailed print
python3 photo_to_print.py portrait.jpg --width 30 --scale-z 3

# Large artistic piece
python3 photo_to_print.py landscape.jpg --width 120 --scale-z 10

# Fast low-quality preview
python3 photo_to_print.py test.jpg --print-profile "0.4mm DRAFT"
```

## Architecture

```
photo.jpg
   ↓
image_processor.py
   ↓ (heightmap → mesh)
model.stl (957 KB)
   ↓
slicer_wrapper.py
   ↓ (PrusaSlicer CLI)
model.gcode (164 KB)
   ↓
octoprint_wrapper.py (optional)
   ↓ (upload + print)
🖨️ Printer
```

## Hardware Support

**Tested:**
- Ender 3 V2 (with OctoPrint)
- Generic RepRap-compatible machines

**In Progress:**
- Multi-material slicing
- Auto-supports generation
- Failure detection + auto-correction

## Roadmap

- [ ] ML-based 3D reconstruction (TripoSR, Shap-E) for quality improvements
- [ ] OctoPrint integration (full automation)
- [ ] Web UI for easy image upload
- [ ] Batch processing (folder → multiple prints)
- [ ] Material library (optimize temps/speeds)
- [ ] Print failure detection

## Current Limitations

1. **Quality:** Heightmap method is fast but loses 3D detail. Use for artistic/decorative prints, not precision parts.
2. **Mesh:** STL files aren't always watertight. PrusaSlicer auto-repairs, but complex models may need post-processing.
3. **Printer:** Only tested on Ender 3 V2. Other printers need profile adjustment.

## Known Issues

- Floating objects detected by slicer (expected for heightmap-based models)
- Some materials require manual profile tweaking
- PrusaSlicer CLI doesn't support all GUI features

## Development

### Testing

```bash
# Test image conversion
python3 image_processor.py test.jpg -o test.stl

# Test slicing
python3 slicer_wrapper.py test.stl -o test.gcode

# Test full pipeline with verbose output
python3 photo_to_print.py test.jpg --verbose
```

### Contributing

Pull requests welcome! Areas we need help:
- Better ML models for 3D reconstruction
- More printer profiles
- Web UI
- OctoPrint integration completion

## License

MIT (see LICENSE file)

## Credits

Built on G1's foundation. Lightyear continues the mission of making 3D printing accessible to everyone.

---

**Questions?** Open an issue or check the docs.  
**Want to contribute?** Fork + PR!

Happy printing! 🖨️✨
