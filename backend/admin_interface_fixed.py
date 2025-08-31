#!/usr/bin/env python3
"""
Fixed Admin Interface for managing FAQs
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify, Response
    print("✅ Flask imported successfully")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")
    print("💡 Please install Flask: pip install flask==3.0.0")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

def get_db_path():
    """Get the correct database path."""
    # Try multiple possible paths
    possible_paths = [
        "data/faqs.db",
        "backend/data/faqs.db", 
        "../data/faqs.db",
        "./data/faqs.db"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ Found database at: {os.path.abspath(path)}")
            return path
    
    # If not found, use the default path and create it
    default_path = "data/faqs.db"
    print(f"⚠️ Database not found, will create at: {os.path.abspath(default_path)}")
    return default_path

def get_db_connection():
    """Get database connection with better error handling."""
    try:
        db_path = get_db_path()
        
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
        
        print(f"✅ Database connected successfully")
        return conn
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise

def seed_database_if_empty():
    """Seed the database with initial FAQs if it's empty."""
    try:
        conn = get_db_connection()
        
        # Check if database is empty
        count = conn.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]
        if count > 0:
            print(f"✅ Database already has {count} FAQs")
            conn.close()
            return
        
        # Try to load from JSON file
        json_paths = [
            "data/custom_faq.json",
            "backend/data/custom_faq.json",
            "../data/custom_faq.json"
        ]
        
        json_data = None
        for json_path in json_paths:
            if os.path.exists(json_path):
                print(f"✅ Found JSON file at: {json_path}")
                try:
                    with open(json_path, "r", encoding="utf-8") as f:
                        json_data = json.load(f)
                    break
                except Exception as e:
                    print(f"⚠️ Failed to read {json_path}: {e}")
                    continue
        
        if not json_data:
            print("⚠️ No JSON file found, creating sample FAQs")
            # Create some sample FAQs
            sample_faqs = [
                {
                    "question": "What is your name?",
                    "answer": "My name is ChatBot, and I'm here to help you!",
                    "category": "general"
                },
                {
                    "question": "How are you?",
                    "answer": "I'm doing well, thank you for asking! How can I assist you today?",
                    "category": "general"
                },
                {
                    "question": "What do you do?",
                    "answer": "I'm an AI assistant designed to help answer your questions and provide information.",
                    "category": "general"
                }
            ]
            json_data = {"faqs": sample_faqs}
        
        faqs = json_data.get("faqs", [])
        now = datetime.now().isoformat()
        
        imported = 0
        for faq in faqs:
            question = str(faq.get("question", "")).strip()
            answer = str(faq.get("answer", "")).strip()
            category = str(faq.get("category", "general")).strip()
            
            if question and answer:
                try:
                    conn.execute(
                        "INSERT INTO faqs (question, answer, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                        (question, answer, category, now, now)
                    )
                    imported += 1
                except sqlite3.IntegrityError:
                    # Question already exists, skip
                    continue
        
        conn.commit()
        conn.close()
        print(f"✅ Seeded database with {imported} FAQs")
        
    except Exception as e:
        print(f"❌ Failed to seed database: {e}")

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
            'faq_count': count,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FAQ Admin Panel</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input[type="text"], textarea, select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        textarea { height: 100px; resize: vertical; }
        .btn { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px; }
        .btn:hover { background-color: #0056b3; }
        .btn-danger { background-color: #dc3545; }
        .btn-danger:hover { background-color: #c82333; }
        .btn-success { background-color: #28a745; }
        .btn-success:hover { background-color: #218838; }
        .faq-item { border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 4px; background: #f9f9f9; }
        .faq-question { font-weight: bold; color: #333; margin-bottom: 10px; }
        .faq-answer { color: #666; margin-bottom: 10px; }
        .faq-actions { margin-top: 10px; }
        .search-box { margin-bottom: 20px; }
        .stats { background: #e9ecef; padding: 15px; border-radius: 4px; margin-bottom: 20px; text-align: center; }
        .flash { padding: 10px; margin: 10px 0; border-radius: 4px; }
        .flash-success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .flash-error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .status-bar { background: #f8f9fa; padding: 10px; border-radius: 4px; margin-bottom: 20px; font-size: 14px; color: #6c757d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 FAQ Admin Panel</h1>
        
        <div class="status-bar">
            <strong>Status:</strong> 
            <span id="dbStatus">Checking...</span> | 
            <span id="faqCount">Loading...</span> |
            <span id="lastUpdate">Last updated: {{ last_update }}</span>
        </div>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash flash-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="stats">
            <h3>📊 Database Statistics</h3>
            <p>Total FAQs: {{ stats.total_faqs }} | Categories: {{ stats.categories|length }}</p>
            <div style="margin-top: 10px; display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;">
                {% for category, count in stats.category_counts.items() %}
                <span style="background: #007bff; color: white; padding: 5px 10px; border-radius: 15px; font-size: 12px; cursor: pointer; transition: all 0.2s; user-select: none;" 
                      onclick="filterByCategoryTag('{{ category }}')" 
                      onmouseover="this.style.background='#0056b3'; this.style.transform='scale(1.05)'"
                      onmouseout="this.style.background='#007bff'; this.style.transform='scale(1)'"
                      title="Click to filter by {{ category }}">
                    {{ category }}: {{ count }}
                </span>
                {% endfor %}
            </div>
        </div>
        
        <!-- Category Filter -->
        <div style="margin-bottom: 20px; display: flex; gap: 10px; align-items: center; background: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef;">
            <label for="categoryFilter" style="margin: 0; font-weight: bold; color: #495057;">Filter by Category:</label>
            <select id="categoryFilter" onchange="filterByCategory()" style="padding: 8px; border: 1px solid #ddd; border-radius: 4px; min-width: 150px; background: white;">
                <option value="">All Categories</option>
                {% for category in stats.categories %}
                <option value="{{ category }}">{{ category }}</option>
                {% endfor %}
            </select>
            <button class="btn" onclick="clearCategoryFilter()" style="background-color: #6c757d;">Clear Filter</button>
            <div id="filterStatus" style="margin-left: auto; font-size: 12px; color: #6c757d;"></div>
        </div>
        
        <div class="search-box">
            <input type="text" id="searchInput" placeholder="Search FAQs..." onkeyup="filterFAQs()" style="width: 100%; padding: 10px; font-size: 16px;">
        </div>
        
        <!-- No FAQs Message -->
        <div id="noFaqsMessage" style="display: none; text-align: center; padding: 40px; color: #6c757d; font-style: italic;">
            <h3>🔍 No FAQs Found</h3>
            <p>No FAQs match your current search criteria or category filter.</p>
            <p>Try adjusting your search terms or category selection.</p>
        </div>
        
        <div style="margin-bottom: 20px;">
            <button class="btn btn-success" onclick="showAddForm()">➕ Add New FAQ</button>
            <button class="btn" onclick="showImportForm()">📥 Import from JSON</button>
            <button class="btn" onclick="exportToJSON()">📤 Export to JSON</button>
            <button class="btn" onclick="reloadFromJSON()">🔄 Reload from custom_faq.json</button>
            <button class="btn" onclick="checkHealth()">🏥 Health Check</button>
        </div>
        
        <!-- Add FAQ Form -->
        <div id="addForm" style="display: none; border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 4px; background: #f8f9fa;">
            <h3>Add New FAQ</h3>
            <form method="POST" action="/add_faq">
                <div class="form-group">
                    <label for="question">Question:</label>
                    <input type="text" id="question" name="question" required>
                </div>
                <div class="form-group">
                    <label for="answer">Answer:</label>
                    <textarea id="answer" name="answer" required></textarea>
                </div>
                <div class="form-group">
                    <label for="category">Category:</label>
                    <input type="text" id="category" name="category" value="general">
                </div>
                <button type="submit" class="btn btn-success">Save FAQ</button>
                <button type="button" class="btn" onclick="hideAddForm()">Cancel</button>
            </form>
        </div>
        
        <!-- Import Form -->
        <div id="importForm" style="display: none; border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 4px; background: #f8f9fa;">
            <h3>Import FAQs from JSON</h3>
            <form method="POST" action="/import_json" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="jsonFile">JSON File:</label>
                    <input type="file" id="jsonFile" name="jsonFile" accept=".json" required>
                </div>
                <button type="submit" class="btn btn-success">Import</button>
                <button type="button" class="btn" onclick="hideImportForm()">Cancel</button>
            </form>
        </div>
        
        <!-- FAQs List -->
        <div id="faqsList">
            {% for faq in faqs %}
            <div class="faq-item" data-question="{{ faq.question.lower() }}" data-answer="{{ faq.answer.lower() }}" data-category="{{ faq.category.lower() }}">
                <div class="faq-question">{{ faq.question }}</div>
                <div class="faq-answer">{{ faq.answer }}</div>
                <div style="color: #888; font-size: 12px;">
                    Category: {{ faq.category }} | Created: {{ faq.created_at }} | ID: {{ faq.id }}
                </div>
                <div class="faq-actions">
                    <button class="btn" onclick="editFAQ({{ faq.id }}, '{{ faq.question|replace("'", "\\'") }}', '{{ faq.answer|replace("'", "\\'") }}', '{{ faq.category }}')">✏️ Edit</button>
                    <button class="btn btn-danger" onclick="deleteFAQ({{ faq.id }})">🗑️ Delete</button>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <!-- Edit Modal -->
        <div id="editModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000;">
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 20px; border-radius: 8px; width: 80%; max-width: 600px;">
                <h3>Edit FAQ</h3>
                <form id="editForm" method="POST">
                    <div class="form-group">
                        <label for="editQuestion">Question:</label>
                        <input type="text" id="editQuestion" name="question" required>
                    </div>
                    <div class="form-group">
                        <label for="editAnswer">Answer:</label>
                        <textarea id="editAnswer" name="answer" required></textarea>
                    </div>
                    <div class="form-group">
                        <label for="editCategory">Category:</label>
                        <input type="text" id="editCategory" name="category" required>
                    </div>
                    <input type="hidden" id="editId" name="id">
                    <button type="submit" class="btn btn-success">Update FAQ</button>
                    <button type="button" class="btn" onclick="hideEditModal()">Cancel</button>
                </form>
            </div>
        </div>
    </div>
    
    <script>
        // Update status on page load
        document.addEventListener('DOMContentLoaded', function() {
            checkHealth();
            highlightSelectedCategory();
        });
        
        function checkHealth() {
            fetch('/health')
                .then(response => response.json())
                .then(data => {
                    const dbStatus = document.getElementById('dbStatus');
                    const faqCount = document.getElementById('faqCount');
                    
                    if (data.status === 'healthy') {
                        dbStatus.textContent = '✅ Connected';
                        dbStatus.style.color = '#28a745';
                        faqCount.textContent = `${data.faq_count} FAQs`;
                    } else {
                        dbStatus.textContent = '❌ Error';
                        dbStatus.style.color = '#dc3545';
                        faqCount.textContent = 'Error';
                    }
                })
                .catch(error => {
                    document.getElementById('dbStatus').textContent = '❌ Offline';
                    document.getElementById('dbStatus').style.color = '#dc3545';
                    document.getElementById('faqCount').textContent = 'Error';
                });
        }
        
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
            document.getElementById('editForm').action = '/edit_faq';
            document.getElementById('editModal').style.display = 'block';
        }
        
        function hideEditModal() {
            document.getElementById('editModal').style.display = 'none';
        }
        
        function deleteFAQ(id) {
            if (confirm('Are you sure you want to delete this FAQ?')) {
                fetch('/delete_faq/' + id, {method: 'DELETE'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            location.reload();
                        } else {
                            alert('Error deleting FAQ: ' + (data.error || 'Unknown error'));
                        }
                    })
                    .catch(error => {
                        alert('Error deleting FAQ: ' + error);
                    });
            }
        }
        
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
            
            // Show/hide no FAQs message
            const noFaqsMessage = document.getElementById('noFaqsMessage');
            if (visibleCount === 0) {
                noFaqsMessage.style.display = 'block';
            } else {
                noFaqsMessage.style.display = 'none';
            }
            
            // Update filter status
            updateFilterStatus(searchTerm, categoryFilter, visibleCount, faqItems.length);
        }
        
        function updateFilterStatus(searchTerm, categoryFilter, visibleCount, totalCount) {
            const filterStatus = document.getElementById('filterStatus');
            let statusText = '';
            
            if (searchTerm || categoryFilter) {
                statusText = `Showing ${visibleCount} of ${totalCount} FAQs`;
                if (categoryFilter) {
                    statusText += ` in "${categoryFilter}" category`;
                }
                if (searchTerm) {
                    statusText += ` matching "${searchTerm}"`;
                }
            } else {
                statusText = `Showing all ${totalCount} FAQs`;
            }
            
            filterStatus.textContent = statusText;
        }
        
        function filterByCategory() {
            filterFAQs();
            highlightSelectedCategory();
        }
        
        function filterByCategoryTag(category) {
            document.getElementById('categoryFilter').value = category;
            filterFAQs();
            highlightSelectedCategory();
        }
        
        function clearCategoryFilter() {
            document.getElementById('categoryFilter').value = "";
            filterFAQs();
            highlightSelectedCategory();
        }
        
        function highlightSelectedCategory() {
            const categoryFilter = document.getElementById('categoryFilter');
            const selectedCategory = categoryFilter.value;
            
            // Reset all category tags to default style
            const categoryTags = document.querySelectorAll('.stats span');
            categoryTags.forEach(tag => {
                tag.style.background = '#007bff';
                tag.style.border = 'none';
            });
            
            // Highlight selected category if any
            if (selectedCategory) {
                categoryTags.forEach(tag => {
                    if (tag.textContent.includes(selectedCategory + ':')) {
                        tag.style.background = '#28a745';
                        tag.style.border = '2px solid #155724';
                    }
                });
            }
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
                })
                .catch(error => {
                    alert('Error exporting JSON: ' + error);
                });
        }
        
        function reloadFromJSON() {
            if (confirm('This will reload all FAQs from custom_faq.json and overwrite any changes made in the interface. Continue?')) {
                fetch('/reload_json')
                    .then(response => response.text())
                    .then(() => {
                        location.reload();
                    })
                    .catch(error => {
                        alert('Error reloading from JSON: ' + error);
                    });
            }
        }
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
                                    },
                                    last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    except Exception as e:
        print(f"❌ Error in index route: {e}")
        return f"Error: {str(e)}", 500

@app.route('/add_faq', methods=['POST'])
def add_faq():
    """Add new FAQ."""
    try:
        question = request.form['question'].strip()
        answer = request.form['answer'].strip()
        category = request.form.get('category', 'general').strip()
        
        if not question or not answer:
            flash('Question and answer are required!', 'error')
            return redirect('/')
        
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO faqs (question, answer, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (question, answer, category, datetime.now().isoformat(), datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        
        flash('FAQ added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('A FAQ with this question already exists!', 'error')
    except Exception as e:
        flash(f'Error adding FAQ: {str(e)}', 'error')
    
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
            flash('Question and answer are required!', 'error')
            return redirect('/')
        
        conn = get_db_connection()
        conn.execute(
            "UPDATE faqs SET question = ?, answer = ?, category = ?, updated_at = ? WHERE id = ?",
            (question, answer, category, datetime.now().isoformat(), faq_id)
        )
        conn.commit()
        conn.close()
        
        flash('FAQ updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating FAQ: {str(e)}', 'error')
    
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
            flash('No file selected!', 'error')
            return redirect('/')
        
        file = request.files['jsonFile']
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect('/')
        
        data = json.load(file)
        faqs = data.get('faqs', [])
        
        conn = get_db_connection()
        imported = 0
        
        for faq in faqs:
            question = str(faq.get('question', '')).strip()
            answer = str(faq.get('answer', '')).strip()
            category = str(faq.get('category', 'general')).strip()
            
            if question and answer:
                try:
                    conn.execute(
                        "INSERT OR REPLACE INTO faqs (question, answer, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                        (question, answer, category, datetime.now().isoformat(), datetime.now().isoformat())
                    )
                    imported += 1
                except sqlite3.IntegrityError:
                    # Question already exists, skip
                    continue
        
        conn.commit()
        conn.close()
        
        flash(f'Successfully imported {imported} FAQs!', 'success')
    except Exception as e:
        flash(f'Error importing JSON: {str(e)}', 'error')
    
    return redirect('/')

@app.route('/reload_json')
def reload_json():
    """Reload FAQs from the custom_faq.json file."""
    try:
        # Try to import from the JSON file directly
        json_paths = [
            "data/custom_faq.json",
            "backend/data/custom_faq.json",
            "../data/custom_faq.json"
        ]
        
        json_data = None
        for json_path in json_paths:
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                break
        
        if not json_data:
            return "No custom_faq.json file found", 404
        
        faqs = json_data.get('faqs', [])
        
        conn = get_db_connection()
        
        # Clear existing FAQs
        conn.execute("DELETE FROM faqs")
        
        # Import new FAQs
        imported = 0
        now = datetime.now().isoformat()
        
        for faq in faqs:
            question = str(faq.get('question', '')).strip()
            answer = str(faq.get('answer', '')).strip()
            category = str(faq.get('category', 'general')).strip()
            
            if question and answer:
                conn.execute(
                    "INSERT INTO faqs (question, answer, category, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (question, answer, category, now, now)
                )
                imported += 1
        
        conn.commit()
        conn.close()
        
        return f"Successfully reloaded {imported} FAQs from custom_faq.json"
        
    except Exception as e:
        return f"Error reloading from JSON: {str(e)}", 500

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
        
        return Response(
            json.dumps(data, ensure_ascii=False, indent=2),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment; filename=faqs_export.json'}
        )
    except Exception as e:
        return f"Error exporting JSON: {str(e)}", 500

if __name__ == '__main__':
    print("🚀 Starting Fixed FAQ Admin Interface...")
    print("🔧 Enhanced error handling and debugging enabled")
    
    # Seed database on startup
    print("🌱 Seeding database...")
    seed_database_if_empty()
    
    # Test database connection
    try:
        conn = get_db_connection()
        count = conn.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]
        conn.close()
        print(f"✅ Database ready with {count} FAQs")
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        sys.exit(1)
    
    # Try to find an available port
    import socket
    
    ports_to_try = [5000, 5001, 8080, 3001, 8000]
    
    for port in ports_to_try:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result != 0:  # Port is available
                print(f"✅ Starting on port {port}")
                print(f"🌐 Open your browser and go to: http://localhost:{port}")
                print(f"🏥 Health check: http://localhost:{port}/health")
                print(f"🔒 This is an admin interface - keep it secure!")
                print(f"💡 Press Ctrl+C to stop the interface when you're done")
                
                try:
                    app.run(debug=False, host='0.0.0.0', port=port, use_reloader=False)
                    break
                except Exception as e:
                    print(f"❌ Failed to start on port {port}: {e}")
                    continue
            else:
                print(f"⚠️ Port {port} is busy, trying next...")
        except Exception as e:
            print(f"⚠️ Could not check port {port}: {e}")
            continue
    else:
        print("❌ All ports are busy! Please free up a port and try again.")
        print("💡 Try stopping other services or use a different port range")
