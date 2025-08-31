# 🤖 FAQ Admin Interface

This is a web-based admin panel for managing your chatbot's FAQ database without touching any code!

## ✨ Features

- **📝 Add New FAQs** - Add questions and answers through a simple form
- **✏️ Edit Existing FAQs** - Modify questions, answers, and categories
- **🗑️ Delete FAQs** - Remove unwanted or outdated FAQs
- **🔍 Search FAQs** - Find specific FAQs quickly
- **📥 Import from JSON** - Bulk import FAQs from JSON files
- **📤 Export to JSON** - Download your FAQ database as JSON
- **📊 Statistics** - View total FAQ count and categories
- **🏷️ Categories** - Organize FAQs by categories

## 🚀 Quick Start

### 1. Install Flask (if not already installed)
```bash
pip install flask==3.0.0
```

### 2. Start the Admin Interface

**Windows:**
```bash
start_admin.bat
```

**Linux/Mac:**
```bash
chmod +x start_admin.sh
./start_admin.sh
```

**Or manually:**
```bash
python admin_interface.py
```

### 3. Open Your Browser
Go to: **http://localhost:5000**

## 🎯 How to Use

### Adding a New FAQ
1. Click **"➕ Add New FAQ"** button
2. Fill in the question and answer
3. Choose a category (optional)
4. Click **"Save FAQ"**

### Editing an FAQ
1. Click **"✏️ Edit"** button on any FAQ
2. Modify the question, answer, or category
3. Click **"Update FAQ"**

### Deleting an FAQ
1. Click **"🗑️ Delete"** button on any FAQ
2. Confirm the deletion

### Importing FAQs
1. Click **"📥 Import from JSON"** button
2. Select a JSON file with FAQ data
3. Click **"Import"**

### Exporting FAQs
1. Click **"📤 Export to JSON"** button
2. Your FAQ database will download as a JSON file

## 📁 JSON Format

The import/export uses this format:
```json
{
  "faqs": [
    {
      "question": "What do you do?",
      "answer": "ما یک شرکت اتوماسیون هوش مصنوعی هستیم",
      "category": "company"
    }
  ]
}
```

## 🔒 Security Note

⚠️ **Important:** This is an admin interface that gives full access to your FAQ database. Keep it secure:

- Change the secret key in `admin_interface.py`
- Don't expose this interface to the public internet
- Use strong passwords if you add authentication
- Consider adding IP restrictions for production use

## 🛠️ Customization

You can easily customize the admin interface by modifying:
- **Colors and styling** in the CSS section
- **Additional fields** like tags, priority, etc.
- **Authentication** by adding login requirements
- **Export formats** like CSV, Excel, etc.

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"
```bash
pip install flask==3.0.0
```

### "Port already in use"
Change the port in `admin_interface.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### Database connection issues
Make sure the `data/faqs.db` file exists and is accessible.

## 📞 Support

If you have issues with the admin interface:
1. Check the console output for error messages
2. Verify Flask is installed correctly
3. Ensure the database file exists and has proper permissions
4. Check that port 5000 is not being used by another application

---

**Happy FAQ Management! 🎉**

