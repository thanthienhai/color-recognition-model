#!/usr/bin/env python3
"""
Test script to verify mixing formula calculation and display
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from advanced_color_analysis import ColorAnalysisEngine

def test_formula_calculation():
    """Test the mixing formula calculation"""
    
    print("=" * 60)
    print("TESTING MIXING FORMULA CALCULATION")
    print("=" * 60)
    
    # Initialize engine
    try:
        engine = ColorAnalysisEngine()
        print("✓ Color Analysis Engine initialized")
    except Exception as e:
        print(f"✗ Failed to initialize engine: {e}")
        return
    
    # Test colors
    test_colors = [
        ("Red", (255, 0, 0), (53.23, 80.11, 67.22)),
        ("Green", (0, 255, 0), (87.74, -86.18, 83.18)),
        ("Blue", (0, 0, 255), (32.30, 79.19, -107.86)),
        ("Yellow", (255, 255, 0), (97.14, -21.55, 94.48)),
        ("Purple", (128, 0, 128), (29.78, 58.93, -36.49)),
        ("Orange", (255, 165, 0), (74.93, 23.93, 78.95)),
    ]
    
    for color_name, rgb, lab in test_colors:
        print(f"\n{'─' * 60}")
        print(f"Testing: {color_name}")
        print(f"RGB: {rgb}")
        print(f"Lab: {lab}")
        print(f"{'─' * 60}")
        
        try:
            # Analyze color
            prediction = engine.analyze_color(
                rgb_values=rgb,
                lab_values=lab,
                method="combined"
            )
            
            print(f"\n📊 Analysis Results:")
            print(f"  Dominant: {prediction.dominant_color}")
            print(f"  Confidence: {prediction.confidence:.1%}")
            
            print(f"\n🎨 Primary Colors (Top 5):")
            top_5 = list(prediction.primary_colors.items())[:5]
            for pcolor, percentage in top_5:
                print(f"  • {pcolor}: {percentage:.1f}%")
            
            # Get mixing formula
            mixing_formula = engine.get_mixing_formula(prediction)
            
            print(f"\n🧪 MIXING FORMULA:")
            total_parts = sum(mixing_formula.values())
            print(f"  Total: {total_parts} parts")
            print()
            print(f"  {'Color':<15} {'Parts':<10} {'Percentage':<10}")
            print(f"  {'-'*15} {'-'*10} {'-'*10}")
            
            for mcolor, parts in mixing_formula.items():
                percentage = (parts / total_parts) * 100 if total_parts > 0 else 0
                print(f"  {mcolor:<15} {parts:<10} {percentage:>6.1f}%")
            
            print(f"\n✓ Formula calculated successfully!")
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    test_formula_calculation()
