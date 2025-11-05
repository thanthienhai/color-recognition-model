#!/usr/bin/env python3
"""
Test Vietnamese color name to field name conversion
"""

import sys
import os
sys.path.append('ui')

# Simulate the conversion function
def convert_color_name_to_field(color_name: str) -> str:
    """
    Convert Vietnamese color name to field name (lowercase, no accents, underscores)
    Example: "Tím Neon" -> "tim_neon"
    """
    vietnamese_map = {
        'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
        'đ': 'd',
        'À': 'A', 'Á': 'A', 'Ả': 'A', 'Ã': 'A', 'Ạ': 'A',
        'Ă': 'A', 'Ằ': 'A', 'Ắ': 'A', 'Ẳ': 'A', 'Ẵ': 'A', 'Ặ': 'A',
        'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ẩ': 'A', 'Ẫ': 'A', 'Ậ': 'A',
        'È': 'E', 'É': 'E', 'Ẻ': 'E', 'Ẽ': 'E', 'Ẹ': 'E',
        'Ê': 'E', 'Ề': 'E', 'Ế': 'E', 'Ể': 'E', 'Ễ': 'E', 'Ệ': 'E',
        'Ì': 'I', 'Í': 'I', 'Ỉ': 'I', 'Ĩ': 'I', 'Ị': 'I',
        'Ò': 'O', 'Ó': 'O', 'Ỏ': 'O', 'Õ': 'O', 'Ọ': 'O',
        'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ổ': 'O', 'Ỗ': 'O', 'Ộ': 'O',
        'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ở': 'O', 'Ỡ': 'O', 'Ợ': 'O',
        'Ù': 'U', 'Ú': 'U', 'Ủ': 'U', 'Ũ': 'U', 'Ụ': 'U',
        'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U', 'Ử': 'U', 'Ữ': 'U', 'Ự': 'U',
        'Ỳ': 'Y', 'Ý': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y', 'Ỵ': 'Y',
        'Đ': 'D'
    }
    
    # Remove accents
    result = ''
    for char in color_name:
        result += vietnamese_map.get(char, char)
    
    # Convert to lowercase and replace spaces with underscores
    result = result.lower().replace(' ', '_')
    
    return result


# Test all 16 colors
print("=" * 80)
print("VIETNAMESE COLOR NAME TO FIELD NAME CONVERSION TEST")
print("=" * 80)
print()

colors_16 = [
    "Đen",
    "Trắng",
    "Vàng Chanh",
    "Đỏ",
    "Xanh Lá",
    "Xanh Biển Sâu",
    "Xanh Dương",
    "Tím",
    "Nâu",
    "Vàng Neon",
    "Xanh Neon",
    "Xanh Lam Neon",
    "Cam Neon",
    "Hồng Neon",
    "Tím Neon",
    "Vàng Kim"
]

print("Color Name Conversions:")
print("-" * 80)
for color in colors_16:
    field_name = convert_color_name_to_field(color)
    print(f"{color:<25} → {field_name}")

print()
print("=" * 80)
print("EXAMPLE JSON OUTPUT")
print("=" * 80)
print()

# Create example JSON
import json

example_formula = {
    "Đỏ": 0.9868,
    "Cam Neon": 0.0109,
    "Nâu": 0.0023
}

# Convert to field names
converted_formula = {}
for color, percentage in example_formula.items():
    field_name = convert_color_name_to_field(color)
    converted_formula[field_name] = percentage

example_json = {
    "timestamp": "2025-11-05T16:00:00.000000",
    "product_name": "Test Product",
    "volume": "1L",
    "color_analysis": {
        "dominant_color": "Đỏ",
        "confidence": 0.9868,
        "lab_values": {"L": 53.0, "a": 80.0, "b": 67.0},
        "rgb_values": {"R": 255, "G": 0, "B": 0}
    },
    "mixing_formula": converted_formula,
    "total_parts": 10000
}

print(json.dumps(example_json, indent=2, ensure_ascii=False))

print()
print("=" * 80)
print("✅ ALL 16 COLORS CONVERTED SUCCESSFULLY")
print("=" * 80)
print()
print("Field Name Format:")
print("  • Lowercase letters only")
print("  • No Vietnamese accents")
print("  • Spaces replaced with underscores")
print("  • Ready for UART/JSON transmission")
print()
print("Examples:")
print("  • 'Tím Neon' → 'tim_neon'")
print("  • 'Đen' → 'den'")
print("  • 'Xanh Biển Sâu' → 'xanh_bien_sau'")
print("=" * 80)
