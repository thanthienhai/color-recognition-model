# -*- coding: utf-8 -*-
"""
Color Storage Module
Module quản lý lưu trữ màu đã phân tích và pha trộn
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class ColorStorage:
    """Manager for saved colors database"""
    
    def __init__(self, storage_path: str = "../saved_colors.json"):
        """
        Initialize color storage
        
        Args:
            storage_path: Path to JSON file storing colors
        """
        # Get absolute path relative to this file
        self.storage_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            storage_path
        )
        self.colors = []
        self.metadata = {}
        self.load_colors()
    
    def load_colors(self) -> bool:
        """
        Load colors from JSON file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.colors = data.get('colors', [])
                    self.metadata = data.get('metadata', {})
                print(f"✓ Loaded {len(self.colors)} colors from {self.storage_path}")
                return True
            else:
                print(f"✗ Storage file not found: {self.storage_path}")
                return False
        except Exception as e:
            print(f"✗ Error loading colors: {e}")
            return False
    
    def save_colors(self) -> bool:
        """
        Save colors to JSON file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'colors': self.colors,
                'metadata': {
                    'total_colors': len(self.colors),
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'version': '1.0'
                }
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"✓ Saved {len(self.colors)} colors to {self.storage_path}")
            return True
        except Exception as e:
            print(f"✗ Error saving colors: {e}")
            return False
    
    def add_color(self, name: str, rgb: Tuple[int, int, int], 
                  lab: Tuple[float, float, float], dominant_color: str,
                  confidence: float, formula: Dict[str, int],
                  description: str = "") -> str:
        """
        Add a new color to storage
        
        Args:
            name: Color name
            rgb: RGB values (0-255)
            lab: Lab values
            dominant_color: Dominant color name
            confidence: Confidence score (0-1)
            formula: Mixing formula dictionary
            description: Optional description
            
        Returns:
            Color ID
        """
        # Generate color ID
        color_id = f"color_{len(self.colors) + 1:03d}"
        
        # Convert RGB to hex
        hex_color = "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])
        
        # Create color entry
        color_entry = {
            'id': color_id,
            'name': name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'rgb': list(rgb),
            'lab': list(lab),
            'hex': hex_color,
            'dominant_color': dominant_color,
            'confidence': confidence,
            'formula': formula,
            'description': description
        }
        
        self.colors.append(color_entry)
        self.save_colors()
        
        print(f"✓ Added color: {name} ({color_id})")
        return color_id
    
    def get_all_colors(self) -> List[Dict]:
        """Get all saved colors"""
        return self.colors
    
    def get_color_by_id(self, color_id: str) -> Optional[Dict]:
        """Get color by ID"""
        for color in self.colors:
            if color['id'] == color_id:
                return color
        return None
    
    def get_color_by_name(self, name: str) -> Optional[Dict]:
        """Get color by name"""
        for color in self.colors:
            if color['name'] == name:
                return color
        return None
    
    def delete_color(self, color_id: str) -> bool:
        """
        Delete color by ID
        
        Args:
            color_id: Color ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        for i, color in enumerate(self.colors):
            if color['id'] == color_id:
                deleted_name = color['name']
                del self.colors[i]
                self.save_colors()
                print(f"✓ Deleted color: {deleted_name} ({color_id})")
                return True
        return False
    
    def update_color(self, color_id: str, **kwargs) -> bool:
        """
        Update color properties
        
        Args:
            color_id: Color ID to update
            **kwargs: Properties to update
            
        Returns:
            True if updated, False if not found
        """
        for color in self.colors:
            if color['id'] == color_id:
                for key, value in kwargs.items():
                    if key in color:
                        color[key] = value
                self.save_colors()
                print(f"✓ Updated color: {color['name']} ({color_id})")
                return True
        return False
    
    def search_colors(self, query: str) -> List[Dict]:
        """
        Search colors by name or description
        
        Args:
            query: Search query
            
        Returns:
            List of matching colors
        """
        query_lower = query.lower()
        results = []
        
        for color in self.colors:
            if (query_lower in color['name'].lower() or 
                query_lower in color.get('description', '').lower() or
                query_lower in color['dominant_color'].lower()):
                results.append(color)
        
        return results
    
    def get_colors_by_dominant(self, dominant_color: str) -> List[Dict]:
        """
        Get all colors with specific dominant color
        
        Args:
            dominant_color: Dominant color name
            
        Returns:
            List of matching colors
        """
        return [c for c in self.colors if c['dominant_color'] == dominant_color]
    
    def export_color_to_json(self, color_id: str, export_path: str) -> bool:
        """
        Export a single color to separate JSON file
        
        Args:
            color_id: Color ID to export
            export_path: Export file path
            
        Returns:
            True if successful
        """
        color = self.get_color_by_id(color_id)
        if not color:
            return False
        
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(color, f, ensure_ascii=False, indent=2)
            print(f"✓ Exported color to {export_path}")
            return True
        except Exception as e:
            print(f"✗ Error exporting color: {e}")
            return False


# Global instance
color_storage = ColorStorage()
