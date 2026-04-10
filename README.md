# mcp-delonghi-ecam

MCP server for DeLonghi ECAM espresso coffee machines via local network control.

[![PyPI](https://img.shields.io/pypi/v/mcp-delonghi-ecam.svg)](https://pypi.org/project/mcp-delonghi-ecam/)
[![Python](https://img.shields.io/pypi/pyversions/mcp-delonghi-ecam.svg)](https://pypi.org/project/mcp-delonghi-ecam/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

mcp-name: "io.github.daedalus/mcp-delonghi-ecam"

## Overview

This MCP server provides comprehensive control over DeLonghi ECAM series automatic espresso coffee machines through their local network API. It enables LLMs to interact with the coffee machine for brewing beverages, monitoring status, and managing machine settings.

## Supported Machines

- DeLonghi ECAM 550 series
- DeLonghi Dinamica Plus
- DeLonghi PrimaDonna Soul
- Other ECAM-based machines with local LAN API

## Install

```bash
pip install mcp-delonghi-ecam
```

## Usage

### As MCP Server

Run the server:

```bash
mcp-delonghi-ecam
```

Or programmatically:

```python
from mcp_delonghi_ecam import mcp

mcp.run()
```

### Tools Available

| Tool | Description |
|------|-------------|
| `connect` | Connect to coffee machine at IP address |
| `disconnect` | Disconnect from the machine |
| `get_status` | Get current machine status |
| `brew_beverage` | Brew a specific beverage |
| `stop_brewing` | Stop current brewing |
| `turn_on` | Turn machine on |
| `turn_off` | Turn machine off |
| `set_cup_light` | Control cup illumination |
| `set_cup_warmer` | Control cup warmer |
| `get_machine_info` | Get machine serial and model |
| `get_statistics` | Get usage statistics |
| `list_beverages` | List available beverages |
| `get_recipe` | Get recipe for a beverage |

### Example Usage

```python
# Connect to machine
await connect("192.168.1.100")

# Get status
status = await get_status("markdown")

# Brew espresso
result = await brew_beverage("espresso", 40, "normal", "medium")

# Brew cappuccino
result = await brew_beverage("cappuccino", 60, "strong", "high")

# Turn on cup warmer
await set_cup_warmer(True)
```

## Configuration

The server connects to the coffee machine on the local network using:
- **Default Port**: 10280
- **Protocol**: HTTP (local LAN API)

Make sure the coffee machine is connected to the same network as the MCP server.

## Development

```bash
git clone https://github.com/daedalus/mcp-delonghi-ecam.git
cd mcp-delonghi-ecam
pip install -e ".[test]"

# Run tests
pytest

# Format
ruff format src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## API Reference

### Beverage Types
- `espresso`, `coffee`, `long_coffee`, `espresso_2x`
- `doppio_plus`, `americano`, `cappuccino`
- `latte_macchiato`, `caffe_latte`, `flat_white`
- `espresso_macchiato`, `hot_milk`, `hot_water`, `steam`, `chocolate`

### Taste Levels
- `extra_mild`, `mild`, `normal`, `strong`, `extra_strong`

### Temperature Settings
- `low`, `medium`, `high`

## License

MIT License - see LICENSE file for details.

## Credits

Protocol information based on reverse-engineered specifications from:
- longshot (Rust implementation)
- ECAMpy
- delonghi-coffee-link-python
