#!/usr/bin/env python3
"""
Script to update all HTML templates to use the modern CropMate theme
"""

import os
import re

def update_template(file_path):
    """Update a single template file to use the modern theme"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track changes
    changes_made = []
    
    # 1. Add the modern CSS link if not present
    if 'style.css' not in content:
        # Find the bootstrap-icons link and add our CSS after it
        if 'bootstrap-icons.css' in content:
            content = re.sub(
                r'(<link rel="stylesheet" href="https://cdn\.jsdelivr\.net/npm/bootstrap-icons[^>]+>)',
                r'\1\n    <link rel="stylesheet" href="{{ url_for(\'static\', filename=\'style.css\') }}">',
                content
            )
            changes_made.append("Added modern CSS link")
    
    # 2. Update navbar classes
    if 'navbar-dark bg-dark' in content:
        content = content.replace('navbar-dark bg-dark', 'navbar-dark')
        changes_made.append("Updated navbar classes")
    
    # 3. Add page header structure if not present
    if '<h1>' in content and 'page-header' not in content:
        # Find the first h1 tag and wrap it in page-header
        h1_pattern = r'(<h1[^>]*>.*?</h1>)'
        h1_match = re.search(h1_pattern, content, re.DOTALL)
        if h1_match:
            h1_content = h1_match.group(1)
            # Extract the text content for subtitle
            h1_text = re.sub(r'<[^>]+>', '', h1_content)
            h1_text = re.sub(r'[^\w\s]', '', h1_text).strip()
            
            # Create page header structure
            page_header = f'''    <div class="page-header">
        {h1_content}
        <p class="subtitle">{h1_text} - Get the information you need for better farming decisions</p>
    </div>'''
            
            # Replace the h1 with page header
            content = re.sub(h1_pattern, page_header, content, count=1, flags=re.DOTALL)
            changes_made.append("Added page header structure")
    
    # 4. Update basic styling if present
    old_styles = [
        'body { background: #f5f5f5;',
        'background: #f5f5f5;',
        'background-color: #f5f5f5;',
        'font-family: \'Segoe UI\'',
        'box-shadow: 0 2px 4px rgba(0,0,0,0.1);',
        'border-radius: 15px;',
        'box-shadow: 0 0 20px rgba(0,0,0,0.05);',
        'margin-top: 2rem;',
        'margin-bottom: 2rem;',
        'padding: 2rem;',
        'color: #2c3e50;',
        'text-align: center;',
        'margin-bottom: 2rem;'
    ]
    
    for old_style in old_styles:
        if old_style in content:
            # Remove old inline styles that conflict with our theme
            content = content.replace(old_style, '')
            changes_made.append(f"Removed old style: {old_style[:30]}...")
    
    # 5. Clean up empty style blocks
    content = re.sub(r'<style>\s*</style>', '', content)
    
    # Write back if changes were made
    if changes_made:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Updated {file_path}: {', '.join(changes_made)}")
        return True
    else:
        print(f"⏭️  No changes needed for {file_path}")
        return False

def main():
    """Update all HTML templates in the templates directory"""
    templates_dir = 'templates'
    
    if not os.path.exists(templates_dir):
        print(f"❌ Templates directory '{templates_dir}' not found!")
        return
    
    html_files = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
    
    if not html_files:
        print(f"❌ No HTML files found in '{templates_dir}'!")
        return
    
    print(f"🔄 Updating {len(html_files)} template files...")
    
    updated_count = 0
    for html_file in html_files:
        file_path = os.path.join(templates_dir, html_file)
        if update_template(file_path):
            updated_count += 1
    
    print(f"\n🎉 Update complete! Updated {updated_count}/{len(html_files)} files.")

if __name__ == "__main__":
    main() 