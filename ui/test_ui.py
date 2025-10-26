#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Color Mixing UI
Tests that all screens load properly without errors
"""

import os
import sys

# Set environment to headless mode for testing
os.environ['KIVY_NO_CONSOLE'] = '1'

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock

# Import all screen classes from main
from main import (
    MixByFormulaScreen,
    ManualDispenseScreen,
    ScanColorScreen,
    ColorantManagerScreen,
    ColorantStatusWidget,
    MaintenanceScreen,
    CalibrationScreen
)


class TestColorMixingApp(App):
    """Test version of ColorMixingApp"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_results = []
        self.all_screens = [
            'mix_formula_screen',
            'manual_dispense_screen',
            'scan_color_screen',
            'colorant_manager_screen',
            'maintenance_screen',
            'calibration_screen'
        ]
    
    def build(self):
        """Build the test app"""
        print("=" * 60)
        print("TESTING COLOR MIXING UI")
        print("=" * 60)
        
        try:
            # Load screen .kv files
            kv_path = os.path.dirname(os.path.abspath(__file__))
            
            kv_files = [
                'mixbyformulascreen.kv',
                'manualdispensescreen.kv',
                'colorantmanagerscreen.kv',
                'maintenancescreen.kv',
                'calibrationscreen.kv',
                'scancolorscreen.kv'
            ]
            
            print("\n✓ Testing .kv file loading...")
            for kv_file in kv_files:
                kv_file_path = os.path.join(kv_path, kv_file)
                if os.path.exists(kv_file_path):
                    Builder.load_file(kv_file_path)
                    print(f"  ✓ Loaded: {kv_file}")
                    self.test_results.append(('PASS', f'Load {kv_file}'))
                else:
                    print(f"  ✗ Missing: {kv_file}")
                    self.test_results.append(('FAIL', f'Load {kv_file}'))
            
            # Load main.kv
            main_kv_path = os.path.join(kv_path, 'main.kv')
            root = Builder.load_file(main_kv_path)
            print(f"  ✓ Loaded: main.kv")
            self.test_results.append(('PASS', 'Load main.kv'))
            
            return root
            
        except Exception as e:
            print(f"  ✗ Error loading UI: {e}")
            self.test_results.append(('FAIL', f'UI Loading: {e}'))
            raise
    
    def on_start(self):
        """Schedule tests after startup"""
        Clock.schedule_once(self.run_tests, 0.5)
    
    def run_tests(self, dt):
        """Run all tests"""
        print("\n✓ Testing screen navigation...")
        
        try:
            screen_manager = self.root.ids.screen_manager
            
            for screen_name in self.all_screens:
                try:
                    screen_manager.current = screen_name
                    print(f"  ✓ Screen '{screen_name}' loaded successfully")
                    self.test_results.append(('PASS', f'Screen {screen_name}'))
                except Exception as e:
                    print(f"  ✗ Screen '{screen_name}' failed: {e}")
                    self.test_results.append(('FAIL', f'Screen {screen_name}: {e}'))
            
        except Exception as e:
            print(f"  ✗ Screen navigation failed: {e}")
            self.test_results.append(('FAIL', f'Screen navigation: {e}'))
        
        # Print summary
        self.print_summary()
        
        # Exit after tests
        Clock.schedule_once(lambda dt: self.stop(), 1.0)
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result[0] == 'PASS')
        failed = sum(1 for result in self.test_results if result[0] == 'FAIL')
        
        print(f"\nTotal tests: {len(self.test_results)}")
        print(f"Passed: {passed} ✓")
        print(f"Failed: {failed} ✗")
        
        if failed > 0:
            print("\nFailed tests:")
            for status, name in self.test_results:
                if status == 'FAIL':
                    print(f"  ✗ {name}")
        
        print("\n" + "=" * 60)
        
        if failed == 0:
            print("✓ ALL TESTS PASSED!")
            print("UI is ready to use.")
        else:
            print("✗ SOME TESTS FAILED")
            print("Please check the errors above.")
        
        print("=" * 60)


if __name__ == '__main__':
    TestColorMixingApp().run()
