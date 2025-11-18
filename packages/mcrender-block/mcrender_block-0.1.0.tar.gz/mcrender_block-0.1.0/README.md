# Minecraft Block Renderer

![CI](https://github.com/almajd3713/vibecoded_mc_renderer/workflows/CI/badge.svg)
[![PyPI version](https://badge.fury.io/py/mcrender-block.svg)](https://pypi.org/project/mcrender-block/)
[![Python Versions](https://img.shields.io/pypi/pyversions/mcrender-block.svg)](https://pypi.org/project/mcrender-block/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python CLI tool for rendering Minecraft blocks from jar files (vanilla or modded) into isometric PNG images.

## Features

- 🎮 Extract and render blocks from Minecraft jar files
- 🎨 Support for vanilla and modded Minecraft
- 📦 Isometric 3D-style rendering
- ⚙️ Configurable output dimensions
- 🎯 Batch rendering capabilities
- 🌈 Support for transparency, tinting, and overlays
- 🔧 **GregTech Support**: Dynamic material variants, voltage tiers, and machine overlays
- ⚡ Multi-layer rendering with emissive effects

## Installation

### From PyPI

```bash
pip install mcrender-block
```

### From source

```bash
git clone https://github.com/almajd3713/vibecoded_mc_renderer.git
cd vibecoded_mc_renderer
pip install -e .
```

### For development

```bash
pip install -e ".[dev]"
```

## Usage

### Basic Commands

#### Render a single block

```bash
mcrender render path/to/minecraft.jar minecraft:stone --output stone.png --size 128
```

#### List all available blocks

```bash
mcrender list-blocks path/to/minecraft.jar
```

#### Render multiple blocks

```bash
mcrender batch path/to/minecraft.jar --blocks minecraft:stone,minecraft:dirt --output-dir renders/
```

#### Get jar file info

```bash
mcrender info path/to/minecraft.jar
```

### GregTech Support

#### Render GregTech blocks with material/tier variants

```bash
# Render a machine with specific voltage tier
mcrender render gregtech.jar gregtech:electric_furnace \
  --tier lv \
  --active \
  --output furnace_lv_active.png

# Render with custom material color
mcrender render gregtech.jar gregtech:compressed_block \
  --material copper \
  --output copper_block.png
```

#### Render machines directly (GregTech-specific)

```bash
mcrender render-machine gregtech.jar electric_furnace \
  --tier hv \
  --active \
  --emissive 0.8 \
  --output furnace_hv.png
```

#### List GregTech resources

```bash
# List all available materials
mcrender list-gregtech gregtech.jar materials

# List voltage tiers
mcrender list-gregtech gregtech.jar tiers

# List machines with capabilities
mcrender list-gregtech gregtech.jar machines

# List material set styles
mcrender list-gregtech gregtech.jar material-sets
```

### Command-Line Options

#### `render` command
- `--material`, `-m`: Material for GregTech blocks (e.g., 'copper', 'steel')
- `--tier`, `-t`: Voltage tier (e.g., 'lv', 'mv', 'hv')
- `--active`, `-a`: Render in active state (for machines)
- `--size`, `-s`: Output image size (default: 128)
- `--output`, `-o`: Output file path

#### `render-machine` command
- `--tier`, `-t`: Voltage tier (default: 'lv')
- `--active`, `-a`: Render in active state
- `--material`, `-m`: Material override for casing
- `--emissive`, `-e`: Emissive glow strength (0.0-1.0, default: 1.0)
- `--size`, `-s`: Output image size
- `--output`, `-o`: Output file path

## How It Works

1. **Extract Resources**: Reads jar files as ZIP archives and indexes block assets
2. **Parse Models**: Parses JSON blockstates and models, resolving parent chains
3. **Load Textures**: Extracts PNG textures and applies transformations
4. **Render**: Creates isometric projection with proper face ordering and alpha compositing

## Development

Run tests:
```bash
pytest
```

**Note**: Tests automatically download Minecraft 1.12.2 jar (~10 MB) on first run and cache it for future use.

Format code:
```bash
black src/ tests/
ruff check src/ tests/
```

## License

MIT
