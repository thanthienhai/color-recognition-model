# UART Mixing Feature - Implementation Summary

## Overview

Implemented the "Mix this color" button functionality with configurable UART/Local save options. The system generates JSON data with mixing formulas in percentage format (0.0 to 1.0).

## Configuration

### Default Settings (config.json)

```json
{
  "uart": {
    "enabled": false,        // UART disabled by default
    "port": "/dev/ttyUSB0",  // Default serial port
    "baudrate": 115200,       // Communication speed
    "timeout": 1              // Read timeout in seconds
  },
  "output": {
    "mixing_formulas_directory": "mixing_formulas/"  // Local save directory
  }
}
```

## Functionality

### 1. Button Behavior

**UART Disabled (default):**
- Saves JSON to local file in `mixing_formulas/` directory
- Filename format: `mixing_{product_name}_{timestamp}.json`
- Shows success popup with file location

**UART Enabled:**
- Sends JSON data via serial port
- Falls back to local save if UART fails
- Shows success/error popup with status

### 2. JSON Data Structure

```json
{
  "timestamp": "2025-11-05T15:32:18.384872",
  "product_name": "Test Product",
  "volume": "1L",
  "color_analysis": {
    "dominant_color": "Cam Neon",
    "confidence": 0.0895,
    "lab_values": {
      "L": 60.5,
      "a": 45.2,
      "b": 50.8
    },
    "rgb_values": {
      "R": 255,
      "G": 100,
      "B": 50
    }
  },
  "mixing_formula": {
    "Cam Neon": 0.0978,      // Percentage as 0.0 to 1.0
    "Nâu": 0.0864,
    "Đỏ": 0.0856,
    // ... more colors
  },
  "total_parts": 91563
}
```

### 3. Percentage Format

- **Storage format:** Decimal 0.0 to 1.0 (e.g., 0.0978 = 9.78%)
- **Conversion:** `percentage = parts / total_parts`
- **Precision:** 4 decimal places (0.0001 precision)
- **Total:** Always sums to ~1.0 (100%)

## Implementation Details

### Key Methods

1. **`start_mixing()`**
   - Main entry point when button clicked
   - Validates prediction data exists
   - Generates mixing formula
   - Routes to UART or local save

2. **`save_to_local(mixing_data)`**
   - Creates directory if needed
   - Generates timestamped filename
   - Saves JSON with UTF-8 encoding
   - Shows success popup

3. **`send_via_uart(mixing_data)`**
   - Opens serial connection
   - Sends JSON with newline terminator
   - Falls back to local save on error
   - Shows status popup

4. **`load_config()`**
   - Loads config.json at startup
   - Provides fallback defaults if missing
   - Logs UART status

### Error Handling

✓ **No prediction data:** Shows error, prevents mixing
✓ **UART not available:** Falls back to local save
✓ **PySerial not installed:** Shows error, saves locally
✓ **Serial port error:** Shows error, saves locally
✓ **File save error:** Shows error popup with details

### User Feedback

**Success Popups:**
- ✓ Green color scheme
- File location or UART status
- Color and formula info

**Error Popups:**
- ✗ Red color scheme
- Error description
- Fallback action if applicable

## Testing

### Test Results

```
✓ Config loading: UART disabled by default
✓ JSON generation: Correct structure
✓ Percentage calculation: Totals to 100%
✓ File save: Creates file successfully
✓ Data integrity: Load/save matches
✓ File size: ~728 bytes for typical formula
✓ Directory creation: Auto-creates if missing
```

### Sample Output

```
Test Color: RGB(255, 100, 50)
Dominant: Cam Neon (9.0% confidence)
Formula: 14 colors
Total Parts: 91,563

Mixing Formula:
  Cam Neon:     9.78%
  Nâu:          8.64%
  Đỏ:           8.56%
  ... (11 more)
  ───────────────────
  Total:       100.00%
```

## Usage

### For Users

1. **Capture color:**
   - Click "Đo màu (AI)"
   - Review analysis results

2. **Enter product info:**
   - Product name (optional)
   - Volume selection

3. **Mix color:**
   - Click "✓ PHA MÀU NÀY"
   - Wait for success/error popup
   - Check `mixing_formulas/` for saved files

### For Developers

**Enable UART:**
```json
{
  "uart": {
    "enabled": true,
    "port": "/dev/ttyUSB0",  // or COM3, /dev/ttyACM0, etc.
    "baudrate": 115200
  }
}
```

**Install PySerial (if using UART):**
```bash
pip install pyserial
```

**Access saved formulas:**
```python
import json

with open('mixing_formulas/mixing_Product_20251105_153218.json', 'r') as f:
    data = json.load(f)
    
formula = data['mixing_formula']
for color, percentage in formula.items():
    print(f"{color}: {percentage * 100:.2f}%")
```

## Files Modified

1. **config.json** - Added UART configuration
2. **ui/main.py** - Implemented mixing functionality
3. **mixing_formulas/** - Created directory for output

## Features

✅ **Configurable UART/Local save**
✅ **Percentage format (0.0-1.0)**
✅ **Timestamped filenames**
✅ **Error handling with fallback**
✅ **User-friendly popups**
✅ **UTF-8 support (Vietnamese)**
✅ **Auto-directory creation**
✅ **Data validation**
✅ **Complete metadata in JSON**

## Next Steps

The mixing button is fully functional and ready to use! 
- Default: Saves to local JSON files
- Optional: Enable UART in config.json for serial communication
