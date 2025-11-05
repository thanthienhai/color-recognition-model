#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for color storage functionality
"""

import sys
import os

# Add paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'ui'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_color_storage():
    """Test color storage module"""
    print("=" * 60)
    print("TESTING COLOR STORAGE MODULE")
    print("=" * 60)
    
    try:
        from ui.color_storage import ColorStorage
        
        # Load storage
        storage = ColorStorage()
        
        print(f"\n✓ Color storage loaded successfully")
        print(f"  Total colors: {len(storage.get_all_colors())}")
        
        # Display all colors
        print("\n📋 Saved Colors:")
        print("-" * 60)
        for color in storage.get_all_colors():
            print(f"  • {color['name']}")
            print(f"    ID: {color['id']}")
            print(f"    RGB: {color['rgb']}")
            print(f"    Hex: {color['hex']}")
            print(f"    Dominant: {color['dominant_color']} ({color['confidence']:.1%})")
            print(f"    Formula: {color['formula']}")
            print(f"    Description: {color['description']}")
            print()
        
        # Test search
        print("\n🔍 Testing search for 'xanh':")
        results = storage.search_colors('xanh')
        print(f"  Found {len(results)} colors")
        for color in results:
            print(f"    - {color['name']}")
        
        # Test adding a new color
        print("\n➕ Testing add new color:")
        new_id = storage.add_color(
            name="Test Màu Tím",
            rgb=(128, 0, 128),
            lab=(29.78, 58.93, -36.49),
            dominant_color="Tím",
            confidence=0.92,
            formula={"Tím": 90, "Đen": 8, "Tím Neon": 2},
            description="Màu tím test"
        )
        print(f"  Added color with ID: {new_id}")
        print(f"  New total: {len(storage.get_all_colors())}")
        
        # Delete the test color
        print(f"\n🗑️  Deleting test color ({new_id}):")
        deleted = storage.delete_color(new_id)
        print(f"  Deleted: {deleted}")
        print(f"  Final total: {len(storage.get_all_colors())}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_color_storage()
    sys.exit(0 if success else 1)
