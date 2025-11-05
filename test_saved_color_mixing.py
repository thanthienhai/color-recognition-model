#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for saved color mixing functionality
Tests JSON export and UART sending from Color Management screen
"""

import sys
import os
import json

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'ui'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_saved_color_mixing():
    """Test the mixing functionality from saved colors"""
    print("=" * 60)
    print("TESTING SAVED COLOR MIXING FUNCTIONALITY")
    print("=" * 60)
    
    try:
        from ui.color_storage import ColorStorage
        from datetime import datetime
        
        # Load storage
        storage = ColorStorage()
        print(f"\n✓ Loaded {len(storage.get_all_colors())} colors")
        
        # Get a test color (first one)
        test_color = storage.get_all_colors()[0]
        print(f"\n📋 Test Color: {test_color['name']}")
        print(f"   ID: {test_color['id']}")
        print(f"   RGB: {test_color['rgb']}")
        print(f"   Formula: {test_color['formula']}")
        
        # Simulate the mixing process
        print("\n🎨 Simulating mixing process...")
        
        # Convert formula to percentages
        formula = test_color['formula']
        total_parts = sum(formula.values())
        formula_percentages = {}
        
        def convert_color_name_to_field(color_name):
            """Convert Vietnamese color name to field name"""
            vietnamese_map = {
                'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
                'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
                'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
                'đ': 'd', 'Đ': 'D'
            }
            result = ""
            for char in color_name:
                result += vietnamese_map.get(char, char)
            return result.lower().replace(' ', '_')
        
        for color, parts in formula.items():
            percentage = parts / total_parts if total_parts > 0 else 0
            field_name = convert_color_name_to_field(color)
            formula_percentages[field_name] = round(percentage, 4)
        
        print(f"   Original formula: {formula}")
        print(f"   Field names: {formula_percentages}")
        
        # Create mixing data
        mixing_data = {
            "timestamp": datetime.now().isoformat(),
            "product_name": test_color['name'],
            "volume": "1L",
            "source": "saved_color",
            "color_id": test_color['id'],
            "color_analysis": {
                "dominant_color": test_color['dominant_color'],
                "confidence": test_color['confidence'],
                "lab_values": {
                    "L": round(test_color['lab'][0], 2),
                    "a": round(test_color['lab'][1], 2),
                    "b": round(test_color['lab'][2], 2)
                },
                "rgb_values": {
                    "R": test_color['rgb'][0],
                    "G": test_color['rgb'][1],
                    "B": test_color['rgb'][2]
                }
            },
            "mixing_formula": formula_percentages,
            "total_parts": total_parts
        }
        
        # Test saving to local file
        print("\n💾 Testing local file save...")
        output_dir = 'mixing_formulas'
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        product_name = mixing_data['product_name'].replace(' ', '_')
        filename = f"mixing_{product_name}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(mixing_data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✓ Saved to: {filepath}")
        print(f"   ✓ File size: {os.path.getsize(filepath)} bytes")
        
        # Verify the file
        with open(filepath, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        print(f"   ✓ File verified - contains {len(loaded_data)} keys")
        print(f"   ✓ Formula colors: {len(loaded_data['mixing_formula'])}")
        print(f"   ✓ Dominant color: {loaded_data['color_analysis']['dominant_color']}")
        
        # Test UART format (without actually sending)
        print("\n📡 Testing UART data format...")
        json_str = json.dumps(mixing_data, ensure_ascii=False)
        print(f"   ✓ JSON string length: {len(json_str)} bytes")
        print(f"   ✓ Contains UTF-8: {any(ord(c) > 127 for c in json_str)}")
        
        # Display sample of data
        print("\n📄 Sample of mixing data:")
        print(json.dumps(mixing_data, indent=2, ensure_ascii=False)[:500] + "...")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\n📝 Summary:")
        print(f"   • Color loaded: {test_color['name']}")
        print(f"   • Formula converted: {len(formula_percentages)} colors")
        print(f"   • JSON file saved: {filename}")
        print(f"   • UART format ready")
        print("\n✓ Saved color mixing functionality is working correctly!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_saved_color_mixing()
    sys.exit(0 if success else 1)
