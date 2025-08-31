#!/usr/bin/env python3
"""
Sophisticated Admin Interface for managing FAQs with modern design
"""

from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
import sqlite3
import os
import sys
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

def get_db_connection():
    """Get database connection."""
    db_path = "data/faqs.db"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL UNIQUE,
            answer TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'general',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

# Modern HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پنل مدیریت FAQ - زیمر</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@100;200;300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Vazir', Tahoma, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            direction: rtl;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        
        .header h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 16px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        
        .main-content {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            font-family: 'Vazir', sans-serif;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 5px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }
        
        .search-input {
            width: 100%;
            background: rgba(255, 255, 255, 0.9);
            border: 2px solid rgba(102, 126, 234, 0.2);
            border-radius: 12px;
            padding: 12px 16px;
            font-family: 'Vazir', sans-serif;
            font-size: 1rem;
            margin-bottom: 20px;
        }
        
        .faq-item {
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        
        .faq-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        }
        
        .faq-question {
            font-size: 1.2rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
        }
        
        .faq-answer {
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        
        .flash {
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 12px;
            font-weight: 500;
        }
        
        .flash-success {
            background: linear-gradient(135deg, rgba(67, 233, 123, 0.9) 0%, rgba(56, 249, 215, 0.9) 100%);
            color: white;
        }
        
        .flash-error {
            background: linear-gradient(135deg, rgba(250, 112, 154, 0.9) 0%, rgba(254, 225, 64, 0.9) 100%);
            color: white;
        }
        
        .form-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
        }
        
        .form-modal {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.9) 100%);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            width: 90%;
            max-width: 600px;
        }
        
        .form-input, .form-textarea {
            width: 100%;
            background: rgba(255, 255, 255, 0.9);
            border: 2px solid rgba(102, 126, 234, 0.2);
            border-radius: 12px;
            padding: 12px 16px;
            font-family: 'Vazir', sans-serif;
            margin-bottom: 15px;
        }
        
        .form-textarea {
            height: 120px;
            resize: vertical;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 پنل مدیریت FAQ</h1>
            <p style="text-align: center; color: #666;">مدیریت هوشمند سوالات متداول با رابط کاربری مدرن</p>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash flash-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_faqs }}</div>
                <div>کل سوالات</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.categories|length }}</div>
                <div>دسته‌بندی‌ها</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.category_counts.get('general', 0) }}</div>
                <div>سوالات عمومی</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_faqs - stats.category_counts.get('general', 0) }}</div>
                <div>سوالات تخصصی</div>
            </div>
        </div>
        
        <div class="main-content">
            <div style="margin-bottom: 20px;">
                <button class="btn btn-success" onclick="showAddForm()">➕ افزودن سوال جدید</button>
                <button class="btn" onclick="showImportForm()">📥 وارد کردن از JSON</button>
                <button class="btn" onclick="exportToJSON()">📤 خروجی JSON</button>
                <button class="btn btn-danger" onclick="reloadFromJSON()">🔄 بارگذاری مجدد</button>
            </div>
            
            <input type="text" id="searchInput" class="search-input" placeholder="جستجو در سوالات..." onkeyup="filterFAQs()">
            
            <div id="faqsList">
                {% for faq in faqs %}
                <div class="faq-item" data-question="{{ faq.question.lower() }}" data-answer="{{ faq.answer.lower() }}">
                    <div class="faq-question">{{ faq.question }}</div>
                    <div class="faq-answer">{{ faq.answer }}</div>
                    <div style="color: #888; font-size: 12px; margin-bottom: 15px;">
                        دسته‌بندی: {{ faq.category }} | شناسه: {{ faq.id }} | تاریخ: {{ faq.created_at[:10] }}
                    </div>
                    <div>
                        <button class="btn" onclick="editFAQ({{ faq.id }}, '{{ faq.question|replace("'", "\\'") }}', '{{ faq.answer|replace("'", "\\'") }}', '{{ faq.category }}')">✏️ ویرایش</button>
                        <button class="btn btn-danger" onclick="deleteFAQ({{ faq.id }})">🗑️ حذف</button>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <!-- Add FAQ Form -->
    <div id="addForm" class="form-overlay">
        <div class="form-modal">
            <h3 style="margin-bottom: 20px;">افزودن سوال جدید</h3>
            <form method="POST" action="/add_faq">
                <input type="text" name="question" class="form-input" placeholder="سوال" required>
                <textarea name="answer" class="form-textarea" placeholder="پاسخ" required></textarea>
                <input type="text" name="category" class="form-input" placeholder="دسته‌بندی" value="general">
                <div style="text-align: left;">
                    <button type="button" class="btn" onclick="hideAddForm()">انصراف</button>
                    <button type="submit" class="btn btn-success">ذخیره</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- Edit FAQ Form -->
    <div id="editForm" class="form-overlay">
        <div class="form-modal">
            <h3 style="margin-bottom: 20px;">ویرایش سوال</h3>
            <form id="editFormElement" method="POST">
                <input type="text" id="editQuestion" name="question" class="form-input" required>
                <textarea id="editAnswer" name="answer" class="form-textarea" required></textarea>
                <input type="text" id="editCategory" name="category" class="form-input" required>
                <input type="hidden" id="editId" name="id">
                <div style="text-align: left;">
                    <button type="button" class="btn" onclick="hideEditForm()">انصراف</button>
                    <button type="submit" class="btn btn-success">بروزرسانی</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        function showAddForm() {
            document.getElementById('addForm').style.display = 'block';
        }
        
        function hideAddForm() {
            document.getElementById('addForm').style.display = 'none';
        }
        
        function editFAQ(id, question, answer, category) {
            document.getElementById('editId').value = id;
            document.getElementById('editQuestion').value = question;
            document.getElementById('editAnswer').value = answer;
            document.getElementById('editCategory').value = category;
            document.getElementById('editFormElement').action = '/edit_faq';
            document.getElementById('editForm').style.display = 'block';
        }
        
        function hideEditForm() {
            document.getElementById('editForm').style.display = 'none';
        }
        
        function deleteFAQ(id) {
            if (confirm('آیا از حذف این سوال اطمینان دارید؟')) {
                fetch('/delete_faq/' + id, {method: 'DELETE'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            alert('خطا در حذف سوال');
                        }
                    });
            }
        }
        
        function filterFAQs() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const faqItems = document.querySelectorAll('.faq-item');
            
            faqItems.forEach(item => {
                const question = item.dataset.question;
                const answer = item.dataset.answer;
                
                if (question.includes(searchTerm) || answer.includes(searchTerm)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        }
        
        function exportToJSON() {
            fetch('/export_json')
                .then(response => response.blob())
                .then(blob => {
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'faqs_export.json';
                    a.click();
                    window.URL.revokeObjectURL(url);
                });
        }
        
        function reloadFromJSON() {
            if (confirm('این کار تمام سوالات را از فایل custom_faq.json بارگذاری مجدد می‌کند. ادامه دهید؟')) {
                fetch('/reload_json')
                    .then(() => location.reload())
                    .catch(error => alert('خطا در بارگذاری مجدد: ' + error));
            }
        }
        
        // Close overlays when clicking outside
        document.querySelectorAll('.form-overlay').forEach(overlay => {
            overlay.addEventListener('click', function(e) {
                if (e.target === overlay) {
                    overlay.style.display = 'none';
                }
            });
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main admin page."""
    try:
        conn = get_db_connection()
        
        # Get statistics
        stats = conn.execute("SELECT COUNT(*) as total FROM faqs").fetchone()
        categories = conn.execute("SELECT DISTINCT category FROM faqs WHERE category IS NOT NULL").fetchall()
        
        # Get category counts
        category_counts = {}
        for cat in categories:
            count = conn.execute("SELECT COUNT(*) FROM faqs WHERE category = ?", (cat['category'],)).fetchone()[0]
            category_counts[cat['category']] = count
        
        # Get all FAQs
        faqs = conn.execute("SELECT * FROM faqs ORDER BY created_at DESC").fetchall()
        
        conn.close()
        
        return render_template_string(HTML_TEMPLATE, 
                                    faqs=faqs,
                                    stats={
                                        'total_faqs': stats['total'], 
                                        'categories': [cat['category'] for cat in categories],
                                        'category_counts': category_counts
                                    })
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/add_faq', methods=['POST'])
def add_faq():
    """Add new FAQ."""
    try:
        question = request.form['question'].strip()
        answer = request.form['answer'].strip()
        category = request.form.get('category', 'general').strip()
        
        if not question or not answer:
            flash('سوال و پاسخ الزامی است!', 'error')
            return redirect('/')
        
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO faqs (question, answer, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (question, answer, category, datetime.now().isoformat(), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        
        flash('سوال با موفقیت اضافه شد!', 'success')
    except Exception as e:
        flash(f'خطا در افزودن سوال: {str(e)}', 'error')
    
    return redirect('/')

@app.route('/edit_faq', methods=['POST'])
def edit_faq():
    """Edit existing FAQ."""
    try:
        faq_id = request.form['id']
        question = request.form['question'].strip()
        answer = request.form['answer'].strip()
        category = request.form.get('category', 'general').strip()
        
        if not question or not answer:
            flash('سوال و پاسخ الزامی است!', 'error')
            return redirect('/')
        
        conn = get_db_connection()
        conn.execute(
            "UPDATE faqs SET question = ?, answer = ?, category = ?, updated_at = ? WHERE id = ?",
            (question, answer, category, datetime.now().isoformat(), faq_id)
        )
        conn.commit()
        conn.close()
        
        flash('سوال با موفقیت بروزرسانی شد!', 'success')
    except Exception as e:
        flash(f'خطا در بروزرسانی سوال: {str(e)}', 'error')
    
    return redirect('/')

@app.route('/delete_faq/<int:faq_id>', methods=['DELETE'])
def delete_faq(faq_id):
    """Delete FAQ."""
    try:
        conn = get_db_connection()
        conn.execute("DELETE FROM faqs WHERE id = ?", (faq_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/export_json')
def export_json():
    """Export FAQs to JSON file."""
    try:
        conn = get_db_connection()
        faqs = conn.execute("SELECT question, answer, category FROM faqs").fetchall()
        conn.close()
        
        data = {
            'faqs': [
                {
                    'question': faq['question'],
                    'answer': faq['answer'],
                    'category': faq['category']
                }
                for faq in faqs
            ]
        }
        
        import json
        from flask import Response
        
        return Response(
            json.dumps(data, ensure_ascii=False, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=faqs_export.json'}
        )
    except Exception as e:
        flash(f'خطا در خروجی JSON: {str(e)}', 'error')
        return redirect('/')

@app.route('/reload_json')
def reload_json():
    """Reload FAQs from the custom_faq.json file."""
    try:
        json_path = "data/custom_faq.json"
        if os.path.exists(json_path):
            import json
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            faqs = data.get("faqs", [])
            conn = get_db_connection()
            
            # Clear existing data
            conn.execute("DELETE FROM faqs")
            
            # Insert new data
            count = 0
            for faq in faqs:
                question = str(faq.get("question", "")).strip()
                answer = str(faq.get("answer", "")).strip()
                if question and answer:
                    conn.execute(
                        "INSERT INTO faqs (question, answer, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                        (question, answer, "general", datetime.now().isoformat(), datetime.now().isoformat())
                    )
                    count += 1
            
            conn.commit()
            conn.close()
            
            flash(f'{count} سوال از فایل custom_faq.json بارگذاری شد!', 'success')
        else:
            flash('فایل custom_faq.json یافت نشد!', 'error')
    except Exception as e:
        flash(f'خطا در بارگذاری مجدد: {str(e)}', 'error')
    
    return redirect('/')

if __name__ == '__main__':
    print("🚀 Starting Sophisticated FAQ Admin Interface...")
    print("🎨 Modern design with glass morphism and gradients")
    print("📱 Will try ports: 5000, 5001, 8080, 3001")
    
    import socket
    ports_to_try = [5000, 5001, 8080, 3001]
    
    for port in ports_to_try:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result != 0:  # Port is available
                print(f"✅ Starting on port {port}")
                print(f"🌐 Open your browser and go to: http://localhost:{port}")
                print(f"🎨 Modern admin interface is now running!")
                app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
                break
            else:
                print(f"⚠️ Port {port} is busy, trying next...")
        except Exception as e:
            print(f"⚠️ Could not start on port {port}: {e}")
            continue
    else:
        print("❌ All ports are busy! Please free up a port and try again.")





















