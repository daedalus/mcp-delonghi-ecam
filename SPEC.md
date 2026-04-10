# SPEC.md — mcp-delonghi-ecam

## Purpose

MCP server to control DeLonghi ECAM series automatic espresso coffee machines via local network IP connection. Provides comprehensive control over beverage preparation, machine monitoring, and settings management.

## Scope

### In Scope
- Connection to ECAM machines via IP address on local network
- Beverage brewing (espresso, coffee, cappuccino, latte, etc.)
- Machine status monitoring (state, temperature, alarms)
- Machine control (power on/off, cup warmer, lights)
- Parameter reading and writing
- Recipe management (read default recipes, customize)
- Statistics retrieval (coffee count, maintenance)

### Not in Scope
- Bluetooth connectivity (IP-only for this server)
- Cloud/API authentication (local LAN control only)
- Machine firmware updates
- Audio/steam control

## Public API / Interface

### MCP Tools

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `connect` | Connect to coffee machine at IP address | `ip_address: str` |
| `disconnect` | Disconnect from the machine | None |
| `get_status` | Get current machine status | `response_format: ResponseFormat` |
| `brew_beverage` | Brew a specific beverage | `beverage: BeverageType, coffee_amount: int, taste: Taste, temperature: Temperature` |
| `stop_brewing` | Stop current brewing operation | None |
| `turn_on` | Turn the machine on | None |
| `turn_off` | Turn the machine off | None |
| `set_cup_light` | Control cup illumination | `enabled: bool` |
| `set_cup_warmer` | Control cup warmer | `enabled: bool` |
| `get_machine_info` | Get machine serial and model info | `response_format: ResponseFormat` |
| `get_statistics` | Get machine usage statistics | `response_format: ResponseFormat` |
| `list_beverages` | List available beverages on machine | None |
| `get_recipe` | Get recipe for a specific beverage | `beverage: BeverageType, response_format: ResponseFormat` |

### Enums

```python
class BeverageType(str, Enum):
    ESPRESSO = "espresso"
    REGULAR_COFFEE = "coffee"
    LONG_COFFEE = "long_coffee"
    ESPRESSO_2X = "espresso_2x"
    DOPPIO_PLUS = "doppio_plus"
    AMERICANO = "americano"
    CAPPUCCINO = "cappuccino"
    LATTE_MACCHIATO = "latte_macchiato"
    CAFFE_LATTE = "caffe_latte"
    FLAT_WHITE = "flat_white"
    ESPRESSO_MACCHIATO = "espresso_macchiato"
    HOT_MILK = "hot_milk"
    HOT_WATER = "hot_water"
    STEAM = "steam"
    CHOCOLATE = "chocolate"

class Taste(str, Enum):
    EXTRA_MILD = "extra_mild"
    MILD = "mild"
    NORMAL = "normal"
    STRONG = "strong"
    EXTRA_STRONG = "extra_strong"

class Temperature(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"
```

### Connection State
- `is_connected: bool` - Whether connected to a machine
- `machine_ip: str | None` - Current machine IP address

## Data Formats

### Status Response (JSON)
```json
{
  "state": "ReadyOrDispensing",
  "state_code": 7,
  "temperature": "Medium",
  "switches": {
    "water_spout": false,
    "water_tank_absent": false,
    "drip_tray_full": false
  },
  "alarms": [],
  "is_brewing": false,
  "progress": 0
}
```

### Machine Info Response (JSON)
```json
{
  "serial_number": "012345678901",
  "model": "ECAM 550.55",
  "software_version": "1.2.3",
  "bean_system": "Single"
}
```

## Edge Cases

1. **Connection failure**: Machine unreachable at IP - return error with specific message
2. **Machine busy**: Brew command while brewing - queue or return busy error
3. **Empty water tank**: Brewing with no water - return alarm status
4. **Empty bean hopper**: Brewing with no beans - return alarm status
5. **Waste container full**: Brewing when waste container full - return alarm status
6. **Machine off**: Command while machine off - turn on automatically or error
7. **Invalid IP format**: Invalid IP address input - Pydantic validation error
8. **Network timeout**: No response from machine - timeout error with retry suggestion
9. **Multiple connections**: Machine already connected elsewhere - conflict error
10. **Invalid beverage**: Requested beverage not available on model - not found error

## Performance & Constraints

- Connection timeout: 10 seconds
- Command timeout: 30 seconds
- Status polling interval: 2 seconds (for monitoring)
- Maximum beverage amount: 250 units
- Temperature range: 0-3 (mapped to Low/Medium/High)
- Taste range: 0-5 (mapped to Extra Mild to Extra Strong)

## Protocol Details

Based on reverse-engineered ECAM protocol:
- **Transport**: HTTP POST to machine's local API endpoint
- **Port**: 10280 (default ECAM local server port)
- **Endpoints**:
  - `/local_lan/key_exchange.json` - Key exchange for encrypted communication
  - `/local_lan/properties` - Property read/write
  - `/local_lan/monitoring` - Status monitoring
- **Authentication**: Local LAN mode (no cloud auth required)
- **Encoding**: Base64-encoded binary packets

### Packet Format
Request packets use ECAM binary protocol:
- Magic byte: `0x0d`
- Packet length
- Request ID
- Data bytes
- Checksum (2 bytes, CRC-like)

### Key Request IDs
- `0x60` (96): Monitor V0
- `0x70` (112): Monitor V1
- `0x75` (117): Monitor V2
- `0x83` (131): Beverage Dispensing Mode
- `0x84` (132): App Control (power on/off)
- `0x90` (144): Parameter Write
- `0x95` (149): Parameter Read
- `0xA2` (162): Statistics Read
