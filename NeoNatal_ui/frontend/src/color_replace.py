import os
import re

app_js_path = r"C:\Users\asawa\OneDrive\Desktop\PROTOTYPE\NeoNatal_ui\frontend\src\App.js"
index_css_path = r"C:\Users\asawa\OneDrive\Desktop\PROTOTYPE\NeoNatal_ui\frontend\src\index.css"

color_mapping = {
    # Blue / Primary -> Clinical Blue
    r'#3b82f6': '#0284c7', 
    r'#3B82F6': '#0284c7',
    r'rgba\(59,130,246': 'rgba(2,132,199',
    r'rgba\(59, 130, 246': 'rgba(2, 132, 199',
    
    # Purple -> Deep Blue / Teal
    r'#8b5cf6': '#0369a1',
    r'#8B5CF6': '#0369a1',
    
    # Green / Success
    r'#10b981': '#059669',
    r'#10B981': '#059669',
    r'#f0fdf4': '#ecfdf5',
    r'#86efac': '#6ee7b7',
    r'#15803d': '#047857',
    
    # Red / Critical
    r'#ef4444': '#e11d48',
    r'#EF4444': '#e11d48',
    r'#fef2f2': '#fff1f2',
    r'rgba\(239,68,68': 'rgba(225,29,72',
    r'rgba\(239, 68, 68': 'rgba(225, 29, 72',
    
    # Amber / Warning
    r'#f59e0b': '#d97706',
    r'#F59E0B': '#d97706',
    r'#fffbeb': '#fffbeb',
    r'#f97316': '#ea580c',
    r'#F97316': '#ea580c',
    
    # Cyan / Info
    r'#06b6d4': '#0891b2',
    
    # Pink -> Indigo (Risk Assessment)
    r'#ec4899': '#4f46e5',
    
    # Slate / Text
    r'#0f172a': '#1e293b',
    r'#0F172A': '#1e293b',
    
    # Backgrounds
    r'#f8fafc': '#f1f5f9',
    r'#F8FAFC': '#f1f5f9',
}

def apply_mapping(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    for old, new in color_mapping.items():
        content = re.sub(old, new, content)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Applying color mappings...")
apply_mapping(app_js_path)
apply_mapping(index_css_path)
print("Done!")
