# 🚀 Lightyear - Photo to 3D Print Pipeline

Convert your photos directly to 3D-printable GCODE in seconds.

**Image → 3D Model (4 modes) → Sliced GCODE → Print**

Lightyear combines the power of **G1 Print Pipeline** with a streamlined, user-friendly interface designed for makers.

## 🎯 Vision

Remove the barriers to 3D printing. You shouldn't need CAD expertise or a degree in mesh topology. Point your camera at something, run one command, and get a printable file. That's the goal.

## ✨ Features

### Photo-to-3D Conversion
✅ **4 Intelligent Modes:**
- **Heightmap** — Fast, detail-preserving relief (default, best for photos)
- **Silhouette** — Extracts & extrudes object outlines (great for clear subjects on plain backgrounds)
- **Revolution** — Creates surfaces of revolution (perfect for vases, bottles, cylindrical objects)
- **Lithophane** — Artistic thickness-based relief for backlit prints (photos glow when backlit!)

✅ **Smart Processing:**
- Shape-from-shading depth estimation
- Edge detection with Sobel filters
- Contour extraction & smart fallbacks
- Automatic mesh repair (watertight + fix winding)
- No GPU required (pure CPU)

### Slicing & Export
✅ **PrusaSlicer CLI Integration**
- Automatic G-code generation
- Ender 3 V2 optimized profiles
- Tree supports, gyroid infill, adaptive layers
- Customizable materials & print speeds

✅ **Modular Architecture**
- Use individual modules or full pipeline
- Swappable components
- Easy to extend

### Printer Control (Roadmap)
⏳ **OctoPrint Integration** — Upload & print directly
⏳ **AI Failure Detection** — Real-time monitoring + auto-correction
⏳ **WhatsApp Control** — Remote print management

## 🚄 Quick Start

### Installation

```bash
# Clone repo
git clone https://github.com/2233morpheus/lightyear.git
cd lightyear

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install PrusaSlicer (required for GCODE generation)
# Ubuntu/Debian:
sudo apt install prusa-slicer
# Or Flatpak:
flatpak install flathub com.prusa3d.PrusaSlicer
```

### Usage

**One-liner — full pipeline:**
```bash
python3 photo_to_print.py photo.jpg
```
Output: `photo_heightmap.gcode` (ready to print!)

**Choose a mode:**
```bash
# Silhouette mode (better for clear subjects)
python3 photo_to_print.py photo.jpg --mode silhouette

# Lithophane mode (artistic backlit effect)
python3 photo_to_print.py portrait.jpg --mode lithophane --width 100

# Revolution mode (for cylindrical objects)
python3 photo_to_print.py vase.jpg --mode revolution --width 80 --scale-z 10
```

**Customize everything:**
```bash
python3 photo_to_print.py photo.jpg \
  --mode heightmap \
  --width 120 \
  --scale-z 8 \
  --printer "Ender 3" \
  --print-profile "0.15mm QUALITY" \
  --material "PETG" \
  --verbose
```

**Using individual modules:**
```bash
# Just convert image to STL
python3 image_processor.py photo.jpg --mode silhouette -o model.stl --width 50

# Just slice STL to GCODE
python3 slicer_wrapper.py model.stl -o model.gcode --printer "Ender 3"

# Upload to OctoPrint (when available)
python3 octoprint_wrapper.py model.gcode --host http://printer-ip:5000 --api-key YOUR_KEY --print
```

## 📊 Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `--mode` | heightmap | Conversion technique (heightmap, silhouette, revolution, lithophane) |
| `--width` | 50mm | Model base width |
| `--scale-z` | 5mm | Height exaggeration (N/A for lithophane) |
| `--printer` | Ender 3 | Printer profile |
| `--print-profile` | 0.2mm NORMAL | Layer height + speed |
| `--material` | PLA | Material type |

## 🎬 Examples

```bash
# Small, detailed portrait (lithophane)
python3 photo_to_print.py portrait.jpg --mode lithophane --width 80

# Large artistic relief
python3 photo_to_print.py landscape.jpg --mode heightmap --width 150 --scale-z 15

# Object silhouette
python3 photo_to_print.py toy.jpg --mode silhouette --width 40

# Fast low-quality preview
python3 photo_to_print.py test.jpg --print-profile "0.4mm DRAFT"

# High-quality PETG print
python3 photo_to_print.py detail.jpg --material "PETG" --print-profile "0.15mm QUALITY"
```

## 🏗️ Architecture

```
photo.jpg
  ↓
image_processor.py
  ↓ (heightmap/silhouette/revolution)
model.stl (957 KB, 10k vertices)
  ↓
slicer_wrapper.py
  ↓ (PrusaSlicer CLI)
model.gcode (164 KB, ready to print)
  ↓
octoprint_wrapper.py (coming soon)
  ↓ (upload + print)
🖨️ Printer
  ↓
Print!
```

## 🔌 Hardware Support

**Tested & Optimized:**
- Ender 3 V2 (with OctoPrint - coming soon)

**Should work:**
- Any RepRap-compatible FDM printer
- Custom profiles easily configurable

**Roadmap:**
- Prusa i3 MK3S+
- Anycubic i3 Mega
- CR-10
- Custom multi-material rigs

## 🗺️ Roadmap

### Phase 1: Foundations (✅ Complete)
- ✅ Image→STL conversion (4 modes)
- ✅ PrusaSlicer integration
- ✅ GCODE generation
- ✅ Modular architecture
- ✅ Open source release

### Phase 2: Automation (In Progress)
- ⏳ OctoPrint integration (Docker setup ready)
- ⏳ Tailscale VPN for remote access
- ⏳ Direct printer upload + start
- ⏳ Print progress monitoring

### Phase 3: Intelligence (Planned)
- ⏳ AI failure detection (spaghetti, layer shift, warping, etc.)
- ⏳ Auto-corrective actions (pause, adjust temps, resume)
- ⏳ WhatsApp control & alerts
- ⏳ Learning from print history

### Phase 4: Polish (Future)
- ⏳ Material library (optimize temps/speeds per filament)
- ⏳ Web UI for non-technical users
- ⏳ Batch processing (folder → multiple prints)
- ⏳ Expected vs. actual layer comparison
- ⏳ Closed-loop optimization

### Phase 5: Scale
- ⏳ SaaS platform (users upload photos, we print)
- ⏳ Hosted printing service
- ⏳ Multi-printer management
- ⏳ Material marketplace

## 🏛️ Built on G1

Lightyear integrates advanced techniques from the **G1 Print Pipeline**:

| Component | Source | Status |
|-----------|--------|--------|
| Photo-to-3D (4 modes) | [g1_photo_to_3d.py](#) | ✅ Integrated |
| PrusaSlicer wrapper | [slicer_wrapper.py](#) | ✅ Working |
| OctoPrint API client | [octoprint_wrapper.py](#) | ✅ Ready |
| **Print optimization** | [print-pipeline](https://github.com/2233morpheus/print-pipeline) | 🔜 Coming |
| **Failure detection** | [print-monitor](https://github.com/2233morpheus/print-monitor) | 🔜 Coming |
| **Remote infrastructure** | [octoprint-remote](https://github.com/2233morpheus/octoprint-remote) | 🔜 Coming |

## 📚 Documentation

- [Installation Guide](#installation)
- [Usage Examples](#examples)
- [Parameter Reference](#parameters)
- [Mode Comparison](#photo-to-3d-conversion)
- [Troubleshooting](#faq)

## ❓ FAQ

### Q: Why are my prints coming out weird?
**A:** Try different modes! Heightmap works best for photos with good lighting and detail. Silhouette works better for isolated objects. Lithophane is pure art.

### Q: Can I use this for production?
**A:** Not yet. Phase 3 adds failure detection + auto-correction. Phase 2 (OctoPrint) is coming soon.

### Q: Does it work on Windows/Mac?
**A:** Yes! Python is cross-platform. PrusaSlicer works on all major OS. Just install dependencies and run.

### Q: Can I integrate my own slicer?
**A:** Absolutely. `slicer_wrapper.py` is modular. Fork the repo and add your slicer.

### Q: What about multi-material printing?
**A:** Coming in Phase 4, with material library support.

## 🤝 Contributing

Pull requests welcome! Areas we need help:
- Better ML models for 3D reconstruction
- More printer profiles
- Web UI
- Failure detection improvements
- Material optimizations

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

## 🙏 Credits

**Lightyear** carries forward **G1's** mission of making 3D printing accessible to everyone.

Built with:
- [G1 Print Pipeline](https://github.com/2233morpheus/print-pipeline) — Core algorithms
- [Print Monitor](https://github.com/2233morpheus/print-monitor) — Failure detection
- [OctoPrint Remote](https://github.com/2233morpheus/octoprint-remote) — Remote infrastructure

**Author:** Khaled Elmajed ([@2233morpheus](https://github.com/2233morpheus))

---

**Questions?** Open an issue.  
**Want to contribute?** Fork + PR!  
**Want to chat?** Reach out on GitHub.

### Happy printing! 🖨️✨

*From inspiration to creation, in seconds.*
