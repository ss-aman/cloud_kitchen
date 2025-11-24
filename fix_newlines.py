import os

def fix_newlines(directory):
    for root, dirs, files in os.walk(directory):
        if 'venv' in dirs:
            dirs.remove('venv')
        if '.git' in dirs:
            dirs.remove('.git')
            
        for file in files:
            if file.endswith('.py') or file.endswith('.html') or file.endswith('.js') or file.endswith('.css'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                    
                    # Check if file has literal \n and is mostly one line (or very few lines compared to \n count)
                    if '\\n' in content and content.count('\n') < content.count('\\n'):
                        print(f"Fixing {filepath}")
                        new_content = content.replace('\\n', '\n')
                        with open(filepath, 'w') as f:
                            f.write(new_content)
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    fix_newlines('.')
