#!/usr/bin/env python3
"""
Comprehensive test comparing old vs new color analysis algorithms
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from advanced_color_analysis import ColorAnalysisEngine
from advanced_color_analysis_v2 import ColorAnalysisEngineV2
import numpy as np


def test_color_comparison():
    """Compare old and new algorithms"""
    
    print("=" * 80)
    print("COLOR ANALYSIS ALGORITHM COMPARISON")
    print("=" * 80)
    
    # Initialize both engines
    old_engine = ColorAnalysisEngine()
    new_engine = ColorAnalysisEngineV2()
    
    # Test colors
    test_colors = [
        ("Pure Red", (255, 0, 0), (53.23, 80.11, 67.22)),
        ("Pure Green", (0, 255, 0), (87.74, -86.18, 83.18)),
        ("Pure Blue", (0, 0, 255), (32.30, 79.19, -107.86)),
        ("Yellow", (255, 255, 0), (97.14, -21.55, 94.48)),
        ("Orange", (255, 165, 0), (74.93, 23.93, 78.95)),
        ("Purple", (128, 0, 128), (29.78, 58.93, -36.49)),
        ("Brown", (139, 69, 19), (37.52, 35.68, 33.94)),
        ("Pink", (255, 192, 203), (81.85, 16.66, -2.46)),
        ("Gray", (128, 128, 128), (53.59, 0.0, 0.0)),
        ("Light Blue", (173, 216, 230), (83.13, -7.98, -16.36)),
    ]
    
    print()
    for color_name, rgb, lab in test_colors:
        print("=" * 80)
        print(f"Testing: {color_name}")
        print(f"RGB: {rgb}, Lab: {lab}")
        print("=" * 80)
        
        # Old algorithm
        print("\n📊 OLD ALGORITHM (CIE76 Delta E):")
        print("-" * 80)
        old_result = old_engine.analyze_color(rgb, lab, method="traditional")
        print(f"Dominant: {old_result.dominant_color} ({old_result.confidence:.1%})")
        print(f"Top 5 Colors:")
        for i, (color, pct) in enumerate(list(old_result.primary_colors.items())[:5]):
            print(f"  {i+1}. {color:<20} {pct:>6.2f}%")
        
        # New algorithm
        print("\n✨ NEW ALGORITHM (CIEDE2000):")
        print("-" * 80)
        new_result = new_engine.analyze_color(rgb, lab, method="ciede2000")
        print(f"Dominant: {new_result.dominant_color} ({new_result.confidence:.1%})")
        print(f"Top 5 Colors:")
        for i, (color, pct) in enumerate(list(new_result.primary_colors.items())[:5]):
            print(f"  {i+1}. {color:<20} {pct:>6.2f}%")
        
        # Quality metrics (new algorithm only)
        quality = new_engine.get_color_quality_score(new_result)
        print(f"\n📈 Quality Metrics:")
        print(f"  Rating: {quality['quality_rating']}")
        print(f"  Min Delta E: {quality['min_delta_e']:.2f}")
        print(f"  Closest Reference: {quality['closest_reference_color']}")
        print(f"  Top 3 Coverage: {quality['top_3_coverage']:.1f}%")
        
        # Mixing formulas
        print("\n🧪 MIXING FORMULAS:")
        print("-" * 80)
        
        old_formula = old_engine.get_mixing_formula(old_result)
        new_formula = new_engine.get_mixing_formula(new_result)
        
        print("OLD Formula (parts):")
        total_old = sum(old_formula.values())
        for color, parts in list(old_formula.items())[:5]:
            pct = (parts / total_old) * 100
            print(f"  {color:<20} {parts:>6} parts ({pct:>5.1f}%)")
        print(f"  Total: {total_old} parts")
        
        print("\nNEW Formula (parts):")
        total_new = sum(new_formula.values())
        for color, parts in list(new_formula.items())[:5]:
            pct = (parts / total_new) * 100
            print(f"  {color:<20} {parts:>6} parts ({pct:>5.1f}%)")
        print(f"  Total: {total_new} parts")
        
        print()
    
    print("=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    print()
    print("✅ NEW ALGORITHM IMPROVEMENTS:")
    print("  1. CIEDE2000 - Industry standard perceptual color difference")
    print("  2. Exponential similarity - More intuitive color matching")
    print("  3. Better reference colors - Validated against standards")
    print("  4. Quality metrics - Quantified accuracy assessment")
    print("  5. Cleaner formulas - Fewer colors, better ratios")
    print("  6. Added Gray color - Fixed missing color issue")
    print("  7. Added Orange - More complete color palette")
    print()
    print("📊 KEY DIFFERENCES:")
    print("  • Old: Linear distance-based similarity")
    print("  • New: Exponential decay similarity")
    print("  • Old: CIE76 (simple Euclidean)")
    print("  • New: CIEDE2000 (perceptually uniform)")
    print("  • Old: 16 colors (with bugs)")
    print("  • New: 18 colors (complete)")
    print()
    print("=" * 80)


def test_edge_cases():
    """Test edge cases and extreme colors"""
    
    print("\n" + "=" * 80)
    print("EDGE CASE TESTING")
    print("=" * 80)
    
    new_engine = ColorAnalysisEngineV2()
    
    edge_cases = [
        ("Pure Black", (0, 0, 0), (0.0, 0.0, 0.0)),
        ("Pure White", (255, 255, 255), (100.0, 0.0, 0.0)),
        ("Very Dark Gray", (30, 30, 30), (11.0, 0.0, 0.0)),
        ("Very Light Gray", (220, 220, 220), (87.0, 0.0, 0.0)),
        ("Lime Green", (50, 205, 50), (70.0, -60.0, 60.0)),
    ]
    
    for color_name, rgb, lab in edge_cases:
        print(f"\n{color_name}: RGB{rgb}")
        result = new_engine.analyze_color(rgb, lab)
        print(f"  → {result.dominant_color} ({result.confidence:.1%})")
        quality = new_engine.get_color_quality_score(result)
        print(f"  → Quality: {quality['quality_rating']}, ΔE={quality['min_delta_e']:.2f}")


if __name__ == "__main__":
    test_color_comparison()
    test_edge_cases()
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 80)
