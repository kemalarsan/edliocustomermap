import json

# Read the current data.js file
with open('data.js', 'r') as f:
    content = f.read()

# Read the current index.html
with open('index.html', 'r') as f:
    html_content = f.read()

# Find where to insert the data (before the script that uses it)
insert_point = html_content.find('<!-- Customer Data -->')
if insert_point == -1:
    print("Could not find insertion point!")
    exit(1)

# Remove the external script tag for data.js
html_content = html_content.replace('<script src="data.js"></script>', '')

# Insert the data inline
before = html_content[:insert_point]
after = html_content[insert_point:]

new_html = before + '<!-- Customer Data -->\n    <script>\n        ' + content + '\n    </script>' + after

# Write the updated HTML
with open('index.html', 'w') as f:
    f.write(new_html)

print("Successfully inlined customer data into index.html")