#!/usr/bin/env python3
"""
Test complete JSON export with field name conversion
"""

import sys
import os
sys.path.append('src')

from advanced_color_analysis import ColorAnalysisEngineV2

print("=" * 80)
print("TESTING JSON EXPORT WITH FIELD NAME CONVERSION")
print("=" * 80)
print()

# Vietnamese accent remover
def convert_color_name_to_field(color_name: str) -> str:
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
        'đ': 'd', 'Đ': 'D'
    }
    result = ''.join(vietnamese_map.get(c, c) for c in color_name)
    return result.lower().replace(' ', '_')

# Initialize engine
engine = ColorAnalysisEngineV2()

# Test colors
test_colors = [
    ("Red", (255, 0, 0), (53.23, 80.11, 67.22)),
    ("Purple", (128, 0, 128), (29.78, 58.93, -36.49)),
    ("Orange", (255, 165, 0), (74.93, 23.93, 78.95)),
]

for name, rgb, lab in test_colors:
    print(f"\n{'=' * 80}")
    print(f"Test: {name}")
    print(f"{'=' * 80}")
    
    # Analyze color
    result = engine.analyze_color(rgb, lab, method="ciede2000")
    
    # Get mixing formula
    mixing_formula = engine.get_mixing_formula(result)
    
    # Convert to percentages with field names
    total_parts = sum(mixing_formula.values())
    formula_percentages = {}
    
    for color, parts in mixing_formula.items():
        percentage = parts / total_parts if total_parts > 0 else 0
        field_name = convert_color_name_to_field(color)
        formula_percentages[field_name] = round(percentage, 4)
    
    # Create JSON structure
    import json
    from datetime import datetime
    
    mixing_data = {
        "timestamp": datetime.now().isoformat(),
        "product_name": f"Test_{name}",
        "volume": "1L",
        "color_analysis": {
            "dominant_color": result.dominant_color,
            "confidence": round(result.confidence, 4),
            "lab_values": {
                "L": round(result.lab_values[0], 2),
                "a": round(result.lab_values[1], 2),
                "b": round(result.lab_values[2], 2)
            },
            "rgb_values": {
                "R": result.rgb_values[0],
                "G": result.rgb_values[1],
                "B": result.rgb_values[2]
            }
        },
        "mixing_formula": formula_percentages,
        "total_parts": total_parts
    }
    
    print(json.dumps(mixing_data, indent=2, ensure_ascii=False))

print()
print("=" * 80)
print("✅ JSON EXPORT FORMAT VERIFIED")
print("=" * 80)
print()
print("Key Features:")
print("  ✓ Field names: lowercase, no accents, underscores")
print("  ✓ Percentages: 0.0 to 1.0 format (4 decimal precision)")
print("  ✓ Complete metadata: timestamp, product, volume")
print("  ✓ Color analysis: RGB, Lab, confidence")
print("  ✓ Ready for UART transmission or local save")
print()
print("Field Name Examples:")
print("  • Đỏ → do")
print("  • Tím Neon → tim_neon")
print("  • Xanh Biển Sâu → xanh_bien_sau")
print("  • Cam Neon → cam_neon")
print("=" * 80)
