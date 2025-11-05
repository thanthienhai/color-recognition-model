#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web server interface cho ứng dụng pha màu trên Raspberry Pi
Chạy khi GUI không khả dụng
"""

from flask import Flask, render_template_string, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Hệ thống pha màu - Web Interface</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .btn { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #45a049; }
        .status { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        input, select { padding: 8px; margin: 5px 0; width: 200px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Hệ thống pha màu tự động</h1>

        <div class="section">
            <h2>📊 Trạng thái hệ thống</h2>
            <div id="status" class="status success">Hệ thống sẵn sàng</div>
        </div>

        <div class="section">
            <h2>🎯 Pha màu từ mẫu</h2>
            <form id="mixForm">
                <label>Tên sản phẩm: <input type="text" id="productName" value="Sản phẩm mẫu"></label><br>
                <label>Thể tích (L): <input type="number" id="volume" value="1" step="0.1"></label><br>
                <button type="button" class="btn" onclick="startMixing()">🚀 Bắt đầu pha màu</button>
            </form>
        </div>

        <div class="section">
            <h2>📋 Lịch sử pha màu</h2>
            <div id="history">Chưa có dữ liệu</div>
        </div>
    </div>

    <script>
        function startMixing() {
            const productName = document.getElementById('productName').value;
            const volume = parseFloat(document.getElementById('volume').value);

            fetch('/api/mix', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    product_name: productName,
                    volume: volume,
                    mixing_formula: {
                        "color_1": 0.3,
                        "color_2": 0.4,
                        "color_3": 0.3
                    }
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('status').innerHTML = '✅ ' + data.message;
                document.getElementById('status').className = 'status success';
                loadHistory();
            })
            .catch(error => {
                document.getElementById('status').innerHTML = '❌ Lỗi: ' + error.message;
                document.getElementById('status').className = 'status error';
            });
        }

        function loadHistory() {
            fetch('/api/history')
            .then(response => response.json())
            .then(data => {
                let html = '<ul>';
                data.forEach(item => {
                    html += `<li>${item.timestamp}: ${item.product_name} - ${item.volume}L</li>`;
                });
                html += '</ul>';
                document.getElementById('history').innerHTML = html;
            });
        }

        // Load history on page load
        loadHistory();
    </script>
</body>
</html>
"""

# In-memory storage for demo
mixing_history = []

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/mix', methods=['POST'])
def mix():
    try:
        data = request.get_json()

        # Simulate mixing process
        mixing_data = {
            "timestamp": datetime.now().isoformat(),
            "product_name": data.get('product_name', 'Unknown'),
            "volume": data.get('volume', 1.0),
            "mixing_formula": data.get('mixing_formula', {})
        }

        # Save to file (simulate)
        save_to_file(mixing_data)

        # Add to history
        mixing_history.append(mixing_data)

        print(f"🎨 Simulated mixing: {mixing_data}")

        return jsonify({
            "success": True,
            "message": f"Đã pha màu {data.get('product_name')} thành công!"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Lỗi: {str(e)}"
        }), 500

@app.route('/api/history')
def get_history():
    return jsonify(mixing_history[-10:])  # Last 10 items

def save_to_file(data):
    """Simulate saving to file"""
    try:
        os.makedirs('mixing_formulas', exist_ok=True)
        filename = f"mixing_{data['product_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join('mixing_formulas', filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"💾 Saved to: {filepath}")
    except Exception as e:
        print(f"❌ Save failed: {e}")

if __name__ == '__main__':
    print("🌐 Starting web server on http://0.0.0.0:5000")
    print("📱 Access from browser: http://raspberry_pi_ip:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
