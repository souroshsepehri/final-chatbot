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
app.secret_key = 'your-secret-key-here'  # Change this in production

def seed_database_if_empty():
    """Seed the database with initial FAQs if it's empty."""
    try:
        conn = get_db_connection()
        
        # Check if database is empty
        count = conn.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]
        if count > 0:
            conn.close()
            return
        
        # Load from JSON file - use same relative path as FAQ service
        json_path = "data/custom_faq.json"
        if not os.path.exists(json_path):
            conn.close()
            return
        
        import json
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        faqs = data.get("faqs", [])
        now = datetime.now().isoformat()
        
        for faq in faqs:
            question = str(faq.get("question", "")).strip()
            answer = str(faq.get("answer", "")).strip()
            if question and answer:
                conn.execute(
                    "INSERT INTO faqs (question, answer, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (question, answer, "general", now, now)
                )
        
        conn.commit()
        conn.close()
        print(f"Seeded database with {len(faqs)} FAQs")
        
    except Exception as e:
        print(f"Warning: Failed to seed database: {e}")

@app.route('/health')
def health_check():
    """Health check endpoint."""
    try:
        conn = get_db_connection()
        count = conn.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]
        conn.close()
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'faq_count': count
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# Modern HTML Template with sophisticated design
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پنل مدیریت FAQ - زیمر</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazir:wght@100;200;300;400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
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
        
        /* Header */
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
        
        .header p {
            text-align: center;
            color: #666;
            font-size: 1.1rem;
        }
        
        /* Stats Cards */
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
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
        }
        
        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        
        .stat-label {
            color: #666;
            font-size: 1rem;
            font-weight: 500;
        }
        
        /* Category Tags */
        .category-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin-top: 15px;
        }
        
        .category-tag {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            user-select: none;
        }
        
        .category-tag:hover {
            transform: scale(1.05);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .category-tag.active {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            box-shadow: 0 4px 15px rgba(67, 233, 123, 0.4);
        }
        
        /* Main Content */
        .main-content {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 255, 255, 0.7) 100%);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }
        
        /* Controls */
        .controls {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
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
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            font-size: 0.9rem;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        }
        
        .btn-success {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            box-shadow: 0 4px 15px rgba(67, 233, 123, 0.4);
        }
        
        .btn-success:hover {
            box-shadow: 0 8px 25px rgba(67, 233, 123, 0.6);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            box-shadow: 0 4px 15px rgba(250, 112, 154, 0.4);
        }
        
        .btn-danger:hover {
            box-shadow: 0 8px 25px rgba(250, 112, 154, 0.6);
        }
        
        /* Search and Filter */
        .search-filter {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .search-input {
            flex: 1;
            min-width: 300px;
            background: rgba(255, 255, 255, 0.9);
            border: 2px solid rgba(102, 126, 234, 0.2);
            border-radius: 12px;
            padding: 12px 16px;
            font-family: 'Vazir', sans-serif;
            font-size: 1rem;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }
        
        .search-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .filter-select {
            background: rgba(255, 255, 255, 0.9);
            border: 2px solid rgba(102, 126, 234, 0.2);
            border-radius: 12px;
            padding: 12px 16px;
            font-family: 'Vazir', sans-serif;
            font-size: 1rem;
            min-width: 150px;
            backdrop-filter: blur(5px);
        }
        
        /* FAQ Items */
        .faq-grid {
            display: grid;
            gap: 20px;
        }
        
        .faq-item {
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 16px;
            padding: 25px;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
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
            line-height: 1.5;
        }
        
        .faq-answer {
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        
        .faq-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            font-size: 0.9rem;
            color: #888;
        }
        
        .faq-category {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        .faq-actions {
            display: flex;
            gap: 10px;
        }
        
        /* Forms */
        .form-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            backdrop-filter: blur(5px);
        }
        
        .form-modal {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 255, 255, 0.9) 100%);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 20px;
            padding: 30px;
            width: 90%;
            max-width: 600px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        .form-input, .form-textarea {
            width: 100%;
            background: rgba(255, 255, 255, 0.9);
            border: 2px solid rgba(102, 126, 234, 0.2);
            border-radius: 12px;
            padding: 12px 16px;
            font-family: 'Vazir', sans-serif;
            font-size: 1rem;
            transition: all 0.3s ease;
            backdrop-filter: blur(5px);
        }
        
        .form-input:focus, .form-textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        .form-textarea {
            height: 120px;
            resize: vertical;
        }
        
        /* Flash Messages */
        .flash {
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 12px;
            font-weight: 500;
            backdrop-filter: blur(10px);
        }
        
        .flash-success {
            background: linear-gradient(135deg, rgba(67, 233, 123, 0.9) 0%, rgba(56, 249, 215, 0.9) 100%);
            color: white;
            border: 1px solid rgba(67, 233, 123, 0.3);
        }
        
        .flash-error {
            background: linear-gradient(135deg, rgba(250, 112, 154, 0.9) 0%, rgba(254, 225, 64, 0.9) 100%);
            color: white;
            border: 1px solid rgba(250, 112, 154, 0.3);
        }
        
        /* No Results */
        .no-results {
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }
        
        .no-results h3 {
            font-size: 1.5rem;
            margin-bottom: 10px;
            color: #333;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .controls {
                flex-direction: column;
            }
            
            .search-filter {
                flex-direction: column;
            }
            
            .search-input {
                min-width: auto;
            }
            
            .faq-meta {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }
            
            .faq-actions {
                flex-direction: column;
            }
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Loading */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header fade-in">
            <h1>🎓 پنل مدیریت FAQ</h1>
            <p>مدیریت هوشمند سوالات متداول با رابط کاربری مدرن</p>
        </div>
        
        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash flash-{{ category }} fade-in">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <!-- Stats Grid -->
        <div class="stats-grid fade-in">
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_faqs }}</div>
                <div class="stat-label">کل سوالات</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.categories|length }}</div>
                <div class="stat-label">دسته‌بندی‌ها</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.category_counts.get('general', 0) }}</div>
                <div class="stat-label">سوالات عمومی</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_faqs - stats.category_counts.get('general', 0) }}</div>
                <div class="stat-label">سوالات تخصصی</div>
            </div>
        </div>
        
        <!-- Category Tags -->
        <div class="stat-card fade-in">
            <div class="stat-label" style="margin-bottom: 15px;">دسته‌بندی‌ها</div>
            <div class="category-tags">
                <button class="category-tag" onclick="filterByCategory('')">همه</button>
                {% for category, count in stats.category_counts.items() %}
                <button class="category-tag" onclick="filterByCategory('{{ category }}')" data-category="{{ category }}">
                    {{ category }} ({{ count }})
                </button>
                {% endfor %}
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="main-content fade-in">
            <!-- Controls -->
            <div class="controls">
                <button class="btn btn-success" onclick="showAddForm()">➕ افزودن سوال جدید</button>
                <button class="btn" onclick="showImportForm()">📥 وارد کردن از JSON</button>
                <button class="btn" onclick="exportToJSON()">📤 خروجی JSON</button>
                <button class="btn btn-danger" onclick="reloadFromJSON()">🔄 بارگذاری مجدد</button>
            </div>
            
            <!-- Search and Filter -->
            <div class="search-filter">
                <input type="text" id="searchInput" class="search-input" placeholder="جستجو در سوالات..." onkeyup="filterFAQs()">
                <select id="categoryFilter" class="filter-select" onchange="filterByCategory()">
                    <option value="">همه دسته‌بندی‌ها</option>
                    {% for category in stats.categories %}
                    <option value="{{ category }}">{{ category }}</option>
                    {% endfor %}
                </select>
                <button class="btn" onclick="clearFilters()">پاک کردن فیلترها</button>
            </div>
            
            <!-- No Results Message -->
            <div id="noResults" class="no-results" style="display: none;">
                <h3>🔍 نتیجه‌ای یافت نشد</h3>
                <p>هیچ سوالی با معیارهای جستجوی شما مطابقت ندارد.</p>
            </div>
            
            <!-- FAQs Grid -->
            <div id="faqsGrid" class="faq-grid">
                {% for faq in faqs %}
                <div class="faq-item" data-question="{{ faq.question.lower() }}" data-answer="{{ faq.answer.lower() }}" data-category="{{ faq.category.lower() }}">
                    <div class="faq-question">{{ faq.question }}</div>
                    <div class="faq-answer">{{ faq.answer }}</div>
                    <div class="faq-meta">
                        <div>
                            <span class="faq-category">{{ faq.category }}</span>
                            <span style="margin-right: 15px;">شناسه: {{ faq.id }}</span>
                        </div>
                        <div style="font-size: 0.8rem;">{{ faq.created_at[:10] }}</div>
                    </div>
                    <div class="faq-actions">
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
            <h3 style="margin-bottom: 20px; color: #333;">افزودن سوال جدید</h3>
            <form method="POST" action="/add_faq">
                <div class="form-group">
                    <label class="form-label">سوال:</label>
                    <input type="text" name="question" class="form-input" required>
                </div>
                <div class="form-group">
                    <label class="form-label">پاسخ:</label>
                    <textarea name="answer" class="form-textarea" required></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">دسته‌بندی:</label>
                    <input type="text" name="category" class="form-input" value="general">
                </div>
                <div style="display: flex; gap: 10px; justify-content: flex-end;">
                    <button type="button" class="btn" onclick="hideAddForm()">انصراف</button>
                    <button type="submit" class="btn btn-success">ذخیره</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- Import Form -->
    <div id="importForm" class="form-overlay">
        <div class="form-modal">
            <h3 style="margin-bottom: 20px; color: #333;">وارد کردن از فایل JSON</h3>
            <form method="POST" action="/import_json" enctype="multipart/form-data">
                <div class="form-group">
                    <label class="form-label">فایل JSON:</label>
                    <input type="file" name="jsonFile" accept=".json" class="form-input" required>
                </div>
                <div style="display: flex; gap: 10px; justify-content: flex-end;">
                    <button type="button" class="btn" onclick="hideImportForm()">انصراف</button>
                    <button type="submit" class="btn btn-success">وارد کردن</button>
                </div>
            </form>
        </div>
    </div>
    
    <!-- Edit FAQ Form -->
    <div id="editForm" class="form-overlay">
        <div class="form-modal">
            <h3 style="margin-bottom: 20px; color: #333;">ویرایش سوال</h3>
            <form id="editFormElement" method="POST">
                <div class="form-group">
                    <label class="form-label">سوال:</label>
                    <input type="text" id="editQuestion" name="question" class="form-input" required>
                </div>
                <div class="form-group">
                    <label class="form-label">پاسخ:</label>
                    <textarea id="editAnswer" name="answer" class="form-textarea" required></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">دسته‌بندی:</label>
                    <input type="text" id="editCategory" name="category" class="form-input" required>
                </div>
                <input type="hidden" id="editId" name="id">
                <div style="display: flex; gap: 10px; justify-content: flex-end;">
                    <button type="button" class="btn" onclick="hideEditForm()">انصراف</button>
                    <button type="submit" class="btn btn-success">بروزرسانی</button>
                </div>
            </form>
        </div>
    </div>
    
    <script>
        // Form Management
        function showAddForm() {
            document.getElementById('addForm').style.display = 'block';
        }
        
        function hideAddForm() {
            document.getElementById('addForm').style.display = 'none';
        }
        
        function showImportForm() {
            document.getElementById('importForm').style.display = 'block';
        }
        
        function hideImportForm() {
            document.getElementById('importForm').style.display = 'none';
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
        
        // Close overlays when clicking outside
        document.querySelectorAll('.form-overlay').forEach(overlay => {
            overlay.addEventListener('click', function(e) {
                if (e.target === overlay) {
                    overlay.style.display = 'none';
                }
            });
        });
        
        // FAQ Management
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
        
        // Search and Filter
        function filterFAQs() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const categoryFilter = document.getElementById('categoryFilter').value.toLowerCase();
            const faqItems = document.querySelectorAll('.faq-item');
            
            let visibleCount = 0;
            
            faqItems.forEach(item => {
                const question = item.dataset.question;
                const answer = item.dataset.answer;
                const category = item.dataset.category;
                
                const matchesSearch = question.includes(searchTerm) || answer.includes(searchTerm);
                const matchesCategory = categoryFilter === "" || category === categoryFilter;
                
                if (matchesSearch && matchesCategory) {
                    item.style.display = 'block';
                    visibleCount++;
                } else {
                    item.style.display = 'none';
                }
            });
            
            // Show/hide no results message
            const noResults = document.getElementById('noResults');
            if (visibleCount === 0) {
                noResults.style.display = 'block';
            } else {
                noResults.style.display = 'none';
            }
            
            updateCategoryTags(categoryFilter);
        }
        
        function filterByCategory(category) {
            document.getElementById('categoryFilter').value = category;
            filterFAQs();
        }
        
        function clearFilters() {
            document.getElementById('searchInput').value = '';
            document.getElementById('categoryFilter').value = '';
            filterFAQs();
        }
        
        function updateCategoryTags(selectedCategory) {
            const categoryTags = document.querySelectorAll('.category-tag');
            categoryTags.forEach(tag => {
                tag.classList.remove('active');
                if (tag.dataset.category === selectedCategory) {
                    tag.classList.add('active');
                }
            });
        }
        
        // Export and Import
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
            if (confirm('این کار تمام سوالات را از فایل custom_faq.json بارگذاری مجدد می‌کند و تغییرات انجام شده را از بین می‌برد. ادامه دهید؟')) {
                fetch('/reload_json')
                    .then(response => response.text())
                    .then(() => {
                        location.reload();
                    })
                    .catch(error => {
                        alert('خطا در بارگذاری مجدد: ' + error);
                    });
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            filterFAQs();
        });
    </script>
</body>
</html>
"""

def get_db_connection():
    """Get database connection."""
    # Use the same database path as the FAQ service
    db_path = "data/faqs.db"
    
    # Debug: Show actual paths being used
    abs_db_path = os.path.abspath(db_path)
    print(f"🔍 Admin Interface: Using database at {abs_db_path}")
    print(f"🔍 Admin Interface: Current working directory: {os.getcwd()}")
    
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Ensure the table exists with correct schema
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

# Seed database on startup - now that get_db_connection is defined
seed_database_if_empty()

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
        print(f"Error in index route: {e}")
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

@app.route('/import_json', methods=['POST'])
def import_json():
    """Import FAQs from JSON file."""
    try:
        if 'jsonFile' not in request.files:
            flash('فایلی انتخاب نشده است!', 'error')
            return redirect('/')
        
        file = request.files['jsonFile']
        if file.filename == '':
            flash('فایلی انتخاب نشده است!', 'error')
            return redirect('/')
        
        import json
        data = json.load(file)
        faqs = data.get('faqs', [])
        
        conn = get_db_connection()
        imported = 0
        
        for faq in faqs:
            question = str(faq.get('question', '')).strip()
            answer = str(faq.get('answer', '')).strip()
            if question and answer:
                conn.execute(
                    "INSERT OR REPLACE INTO faqs (question, answer, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (question, answer, 'general', datetime.now().isoformat(), datetime.now().isoformat())
                )
                imported += 1
        
        conn.commit()
        conn.close()
        
        flash(f'{imported} سوال با موفقیت وارد شد!', 'success')
    except Exception as e:
        flash(f'خطا در وارد کردن JSON: {str(e)}', 'error')
    
    return redirect('/')

@app.route('/reload_json')
def reload_json():
    """Reload FAQs from the custom_faq.json file."""
    try:
        from services.faq import FAQService
        faq_service = FAQService()
        count = faq_service.reload_from_json()
        
        if count > 0:
            flash(f'{count} سوال از فایل custom_faq.json با موفقیت بارگذاری شد!', 'success')
        else:
            flash('هیچ سوالی بارگذاری نشد. بررسی کنید که فایل custom_faq.json وجود داشته باشد.', 'warning')
    except Exception as e:
        flash(f'خطا در بارگذاری مجدد: {str(e)}', 'error')
    
    return redirect('/')

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

if __name__ == '__main__':
    print("🚀 Starting Sophisticated FAQ Admin Interface...")
    print("📱 Will try ports: 5000, 5001, 8080, 3001")
    print("🔒 This is an admin interface - keep it secure!")
    print("🏥 Health check will be available at the chosen port")
    
    # Check if port 5000 is available
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 5000))
        sock.close()
        if result == 0:
            print("❌ Port 5000 is already in use!")
            print("💡 Try using a different port or stop the service using port 5000")
            print("💡 Common alternatives: 5001, 8080, 3001")
            sys.exit(1)
        else:
            print("✅ Port 5000 is available")
    except Exception as e:
        print(f"⚠️ Could not check port availability: {e}")
    
    try:
        # Test database connection before starting
        conn = get_db_connection()
        count = conn.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]
        conn.close()
        print(f"✅ Database connected successfully with {count} FAQs")
        
        # Try port 5000 first, then alternatives
        ports_to_try = [5000, 5001, 8080, 3001]
        
        for port in ports_to_try:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                if result != 0:  # Port is available
                    print(f"✅ Starting on port {port}")
                    print(f"🌐 Open your browser and go to: http://localhost:{port}")
                    print(f"🏥 Health check: http://localhost:{port}/health")
                    print(f"🎨 Modern admin interface is now running!")
                    print(f"💡 Press Ctrl+C to stop the interface when you're done")
                    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
                    break
                else:
                    print(f"⚠️ Port {port} is busy, trying next...")
            except Exception as e:
                print(f"⚠️ Could not start on port {port}: {e}")
                continue
        else:
            print("❌ All ports are busy! Please free up a port and try again.")
    except Exception as e:
        print(f"❌ Failed to start admin interface: {e}")
        print("💡 Check if the database file exists and is accessible")
