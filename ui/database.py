#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database module stub for Color Mixing System
Module cơ sở dữ liệu cho hệ thống pha màu
"""

import sqlite3
import os


class ColorDatabase:
    """Lớp quản lý cơ sở dữ liệu"""
    
    def __init__(self, db_path='color_mixing.db'):
        """Khởi tạo kết nối database"""
        self.db_path = db_path
        self.connection = None
        self.init_database()
    
    def init_database(self):
        """Khởi tạo cấu trúc database"""
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        
        # Bảng hệ màu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS color_systems (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Bảng công thức màu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS color_formulas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                system_id INTEGER,
                color_code TEXT NOT NULL,
                color_name TEXT,
                base_type TEXT,
                price REAL,
                FOREIGN KEY (system_id) REFERENCES color_systems(id)
            )
        ''')
        
        # Bảng chi tiết công thức (các màu gốc)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS formula_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                formula_id INTEGER,
                colorant_code TEXT NOT NULL,
                amount_ml REAL NOT NULL,
                FOREIGN KEY (formula_id) REFERENCES color_formulas(id)
            )
        ''')
        
        # Bảng màu gốc (colorants)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS colorants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL UNIQUE,
                name TEXT,
                max_capacity_ml REAL DEFAULT 1000,
                current_level_ml REAL DEFAULT 1000,
                pulse_per_1ml INTEGER DEFAULT 100,
                pulse_per_01ml INTEGER DEFAULT 10
            )
        ''')
        
        self.connection.commit()
        self._seed_sample_data()
    
    def _seed_sample_data(self):
        """Thêm dữ liệu mẫu"""
        cursor = self.connection.cursor()
        
        # Thêm hệ màu mẫu
        systems = [('RAL',), ('Pantone',), ('NCS',), ('Dulux',)]
        cursor.executemany('INSERT OR IGNORE INTO color_systems (name) VALUES (?)', systems)
        
        # Thêm màu gốc mẫu
        colorants = [
            ('AXX', 'White Tint', 1000, 850, 100, 10),
            ('A', 'Red Oxide', 1000, 650, 100, 10),
            ('B', 'Yellow Oxide', 1000, 450, 100, 10),
            ('C', 'Black', 1000, 920, 100, 10),
            ('D', 'Blue', 1000, 150, 100, 10),
            ('E', 'Green', 1000, 780, 100, 10),
            ('L', 'Magenta', 1000, 550, 100, 10),
            ('R', 'Red', 1000, 880, 100, 10),
            ('Y', 'Yellow', 1000, 50, 100, 10),
            ('K', 'Orange', 1000, 700, 100, 10),
            ('T', 'Brown', 1000, 820, 100, 10),
            ('W', 'Violet', 1000, 950, 100, 10),
            ('N', 'Cyan', 1000, 400, 100, 10),
            ('M', 'Maroon', 1000, 600, 100, 10),
            ('P', 'Pink', 1000, 250, 100, 10),
            ('Q', 'Turquoise', 1000, 900, 100, 10),
        ]
        cursor.executemany('''
            INSERT OR IGNORE INTO colorants 
            (code, name, max_capacity_ml, current_level_ml, pulse_per_1ml, pulse_per_01ml) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', colorants)
        
        self.connection.commit()
    
    def get_color_systems(self):
        """Lấy danh sách hệ màu"""
        cursor = self.connection.cursor()
        cursor.execute('SELECT name FROM color_systems')
        return [row[0] for row in cursor.fetchall()]
    
    def get_color_codes(self, system_name):
        """Lấy danh sách mã màu theo hệ màu"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT cf.color_code 
            FROM color_formulas cf
            JOIN color_systems cs ON cf.system_id = cs.id
            WHERE cs.name = ?
        ''', (system_name,))
        return [row[0] for row in cursor.fetchall()]
    
    def get_formula(self, system_name, color_code):
        """Lấy công thức màu"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT cf.id, cf.color_name, cf.base_type, cf.price
            FROM color_formulas cf
            JOIN color_systems cs ON cf.system_id = cs.id
            WHERE cs.name = ? AND cf.color_code = ?
        ''', (system_name, color_code))
        
        result = cursor.fetchone()
        if not result:
            return None
        
        formula_id, color_name, base_type, price = result
        
        # Lấy chi tiết công thức
        cursor.execute('''
            SELECT colorant_code, amount_ml
            FROM formula_details
            WHERE formula_id = ?
        ''', (formula_id,))
        
        details = cursor.fetchall()
        
        return {
            'color_name': color_name,
            'base_type': base_type,
            'price': price,
            'details': [{'colorant': row[0], 'amount': row[1]} for row in details]
        }
    
    def get_colorant_levels(self):
        """Lấy mức màu hiện tại của tất cả ống"""
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT code, name, max_capacity_ml, current_level_ml
            FROM colorants
            ORDER BY code
        ''')
        
        results = []
        for row in cursor.fetchall():
            code, name, max_cap, current = row
            percent = (current / max_cap * 100) if max_cap > 0 else 0
            results.append({
                'code': code,
                'name': name,
                'level_ml': current,
                'level_percent': percent
            })
        
        return results
    
    def update_colorant_level(self, colorant_code, amount_used):
        """Cập nhật mức màu sau khi sử dụng"""
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE colorants
            SET current_level_ml = current_level_ml - ?
            WHERE code = ?
        ''', (amount_used, colorant_code))
        self.connection.commit()
    
    def close(self):
        """Đóng kết nối database"""
        if self.connection:
            self.connection.close()


# Test
if __name__ == '__main__':
    db = ColorDatabase('test_color_mixing.db')
    
    print("Hệ màu:", db.get_color_systems())
    print("\nMàu gốc:")
    for colorant in db.get_colorant_levels():
        print(f"  {colorant['code']}: {colorant['level_ml']}ml ({colorant['level_percent']:.1f}%)")
    
    db.close()
    
    # Xóa file test
    if os.path.exists('test_color_mixing.db'):
        os.remove('test_color_mixing.db')
