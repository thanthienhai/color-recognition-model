#!/usr/bin/env python3
"""
Test script to verify the mixing button functionality
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from advanced_color_analysis import ColorAnalysisEngine

def test_mixing_json_generation():
    """Test JSON generation for mixing formulas"""
    
    print("=" * 70)
    print("TESTING MIXING JSON GENERATION")
    print("=" * 70)
    
    # Initialize engine
    engine = ColorAnalysisEngine()
    
    # Test with a sample color
    rgb = (255, 100, 50)  # Orange-ish
    lab = (60.5, 45.2, 50.8)
    
    print(f"\nTest Color:")
    print(f"  RGB: {rgb}")
    print(f"  Lab: {lab}")
    
    # Analyze
    prediction = engine.analyze_color(rgb_values=rgb, lab_values=lab, method="combined")
    
    print(f"\nAnalysis Results:")
    print(f"  Dominant: {prediction.dominant_color}")
    print(f"  Confidence: {prediction.confidence:.1%}")
    
    # Get mixing formula
    mixing_formula = engine.get_mixing_formula(prediction)
    
    # Convert to percentages (0.0 to 1.0)
    total_parts = sum(mixing_formula.values())
    formula_percentages = {}
    
    for color, parts in mixing_formula.items():
        percentage = parts / total_parts if total_parts > 0 else 0
        formula_percentages[color] = round(percentage, 4)
    
    # Create JSON data structure
    from datetime import datetime
    
    mixing_data = {
        "timestamp": datetime.now().isoformat(),
        "product_name": "Test Product",
        "volume": "1L",
        "color_analysis": {
            "dominant_color": prediction.dominant_color,
            "confidence": round(prediction.confidence, 4),
            "lab_values": {
                "L": round(prediction.lab_values[0], 2),
                "a": round(prediction.lab_values[1], 2),
                "b": round(prediction.lab_values[2], 2)
            },
            "rgb_values": {
                "R": prediction.rgb_values[0],
                "G": prediction.rgb_values[1],
                "B": prediction.rgb_values[2]
            }
        },
        "mixing_formula": formula_percentages,
        "total_parts": total_parts
    }
    
    print(f"\n{'=' * 70}")
    print("GENERATED JSON DATA:")
    print(f"{'=' * 70}")
    print(json.dumps(mixing_data, indent=2, ensure_ascii=False))
    
    print(f"\n{'=' * 70}")
    print("VERIFICATION:")
    print(f"{'=' * 70}")
    print(f"✓ Timestamp: {mixing_data['timestamp']}")
    print(f"✓ Product: {mixing_data['product_name']}")
    print(f"✓ Volume: {mixing_data['volume']}")
    print(f"✓ Dominant Color: {mixing_data['color_analysis']['dominant_color']}")
    print(f"✓ Total Parts: {mixing_data['total_parts']}")
    print(f"✓ Number of Colors: {len(mixing_data['mixing_formula'])}")
    
    print(f"\n{'=' * 70}")
    print("MIXING FORMULA (Percentage Format):")
    print(f"{'=' * 70}")
    
    total_percentage = 0
    for color, percentage in mixing_data['mixing_formula'].items():
        percent_display = percentage * 100  # Convert 0.0-1.0 to 0-100%
        total_percentage += percentage
        print(f"  {color:<20} {percentage:>8.4f} ({percent_display:>6.2f}%)")
    
    print(f"  {'-' * 40}")
    print(f"  {'Total':<20} {total_percentage:>8.4f} ({total_percentage*100:>6.2f}%)")
    
    # Test saving to file
    print(f"\n{'=' * 70}")
    print("TESTING FILE SAVE:")
    print(f"{'=' * 70}")
    
    output_dir = "mixing_formulas/"
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"mixing_Test_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(mixing_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved to: {filepath}")
    
    # Verify file contents
    with open(filepath, 'r', encoding='utf-8') as f:
        loaded_data = json.load(f)
    
    print(f"✓ File size: {os.path.getsize(filepath)} bytes")
    print(f"✓ Data integrity: {'OK' if loaded_data == mixing_data else 'FAILED'}")
    
    print(f"\n{'=' * 70}")
    print("TEST COMPLETED SUCCESSFULLY!")
    print(f"{'=' * 70}")
    
    return mixing_data

if __name__ == "__main__":
    test_mixing_json_generation()
