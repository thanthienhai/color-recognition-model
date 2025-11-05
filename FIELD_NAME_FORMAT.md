# Field Name Format for Mixing Formula

## Overview

Color names in the mixing formula are converted to field-safe names for UART/JSON transmission.

## Conversion Rules

1. **Remove Vietnamese accents** - All diacritics removed
2. **Lowercase** - Convert to lowercase letters
3. **Underscores** - Replace spaces with underscores
4. **ASCII-safe** - Ready for serial transmission

## 16 Color Conversions

| Vietnamese Name | Field Name | Example Usage |
|----------------|------------|---------------|
| **Đen** | `den` | `"den": 0.9500` |
| **Trắng** | `trang` | `"trang": 0.9800` |
| **Vàng Chanh** | `vang_chanh` | `"vang_chanh": 0.4500` |
| **Đỏ** | `do` | `"do": 0.9868` |
| **Xanh Lá** | `xanh_la` | `"xanh_la": 0.7200` |
| **Xanh Biển Sâu** | `xanh_bien_sau` | `"xanh_bien_sau": 0.6100` |
| **Xanh Dương** | `xanh_duong` | `"xanh_duong": 0.9741` |
| **Tím** | `tim` | `"tim": 0.9642` |
| **Nâu** | `nau` | `"nau": 0.9713` |
| **Vàng Neon** | `vang_neon` | `"vang_neon": 0.5783` |
| **Xanh Neon** | `xanh_neon` | `"xanh_neon": 0.9976` |
| **Xanh Lam Neon** | `xanh_lam_neon` | `"xanh_lam_neon": 0.3200` |
| **Cam Neon** | `cam_neon` | `"cam_neon": 0.1540` |
| **Hồng Neon** | `hong_neon` | `"hong_neon": 0.2300` |
| **Tím Neon** | `tim_neon` | `"tim_neon": 0.0223` |
| **Vàng Kim** | `vang_kim` | `"vang_kim": 0.8062` |

## JSON Format Example

### Pure Red
```json
{
  "timestamp": "2025-11-05T16:23:39.041701",
  "product_name": "Red Paint",
  "volume": "1L",
  "color_analysis": {
    "dominant_color": "Đỏ",
    "confidence": 0.9868,
    "lab_values": {
      "L": 53.23,
      "a": 80.11,
      "b": 67.22
    },
    "rgb_values": {
      "R": 255,
      "G": 0,
      "B": 0
    }
  },
  "mixing_formula": {
    "do": 1.0
  },
  "total_parts": 1
}
```

### Purple Mix
```json
{
  "timestamp": "2025-11-05T16:23:39.042421",
  "product_name": "Purple Paint",
  "volume": "1L",
  "color_analysis": {
    "dominant_color": "Tím",
    "confidence": 0.9642,
    "lab_values": {
      "L": 29.78,
      "a": 58.93,
      "b": -36.49
    },
    "rgb_values": {
      "R": 128,
      "G": 0,
      "B": 128
    }
  },
  "mixing_formula": {
    "tim": 0.9681,
    "tim_neon": 0.0319
  },
  "total_parts": 99599
}
```

### Orange Mix
```json
{
  "timestamp": "2025-11-05T16:23:39.042939",
  "product_name": "Orange Paint",
  "volume": "1L",
  "color_analysis": {
    "dominant_color": "Vàng Kim",
    "confidence": 0.8062,
    "lab_values": {
      "L": 74.93,
      "a": 23.93,
      "b": 78.95
    },
    "rgb_values": {
      "R": 255,
      "G": 165,
      "B": 0
    }
  },
  "mixing_formula": {
    "vang_kim": 0.8397,
    "cam_neon": 0.1603
  },
  "total_parts": 24005
}
```

## Field Name Pattern

### Pattern: `[a-z_]+`

**Valid characters:**
- Lowercase letters: `a-z`
- Underscores: `_`
- Numbers (if needed): `0-9`

**Invalid characters:**
- Uppercase letters
- Spaces
- Vietnamese accents (đ, ă, â, ê, ô, ơ, ư, etc.)
- Special characters (-, /, \, etc.)

## Percentage Format

**Range:** `0.0` to `1.0`

**Precision:** 4 decimal places

**Examples:**
- `1.0` = 100%
- `0.9868` = 98.68%
- `0.5783` = 57.83%
- `0.0319` = 3.19%

**Conversion:**
```python
percentage_decimal = parts / total_parts
percentage_percent = percentage_decimal * 100
```

## Implementation

### Python Function
```python
def convert_color_name_to_field(color_name: str) -> str:
    """Convert Vietnamese color name to field name"""
    vietnamese_map = {
        'đ': 'd', 'Đ': 'D',
        'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    }
    
    result = ''.join(vietnamese_map.get(c, c) for c in color_name)
    return result.lower().replace(' ', '_')
```

### Usage Example
```python
# Get mixing formula with original names
mixing_formula = {"Đỏ": 1000, "Tím Neon": 50}

# Convert to field names for JSON
formula_json = {}
total_parts = sum(mixing_formula.values())

for color, parts in mixing_formula.items():
    field_name = convert_color_name_to_field(color)
    percentage = round(parts / total_parts, 4)
    formula_json[field_name] = percentage

# Result: {"do": 0.9524, "tim_neon": 0.0476}
```

## Benefits

✅ **UART Compatible** - ASCII-safe for serial transmission
✅ **JSON Friendly** - Valid JSON field names
✅ **Consistent** - Same conversion every time
✅ **Readable** - Still recognizable to Vietnamese speakers
✅ **Universal** - Works across all systems

## Testing

Run tests:
```bash
python3 test_field_name_conversion.py
python3 test_json_export_format.py
```

All 16 colors verified working correctly!

---

**Status:** ✅ Implemented and tested
**Location:** `ui/main.py` - `convert_color_name_to_field()` method
**Version:** 1.0
