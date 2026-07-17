import os
import ast
import sys

def check_syntax(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source, filename=file_path)
        print(f"✅ SYNTAX OK: {file_path}")
        return True
    except SyntaxError as e:
        print(f"❌ SYNTAX ERROR: {file_path} on line {e.lineno}")
        print(f"    Error: {e.msg}")
        print(f"    Line:  {e.text.strip() if e.text else ''}")
        return False
    except Exception as e:
        print(f"⚠️ ERROR READING: {file_path} - {e}")
        return False

def verify_all_files():
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
    failed = False
    checked_count = 0
    
    for root, dirs, files in os.walk(backend_dir):
        # Exclude virtual environments or temporary folders if any
        if 'venv' in root or '.venv' in root or '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                checked_count += 1
                if not check_syntax(file_path):
                    failed = True
                    
    print("\n--------------------------------------------------")
    print(f"Verification Summary: Checked {checked_count} python files.")
    if failed:
        print("❌ Verification FAILED: One or more syntax errors detected.")
        sys.exit(1)
    else:
        print("🎉 Verification PASSED: All python files are syntactically correct!")
        sys.exit(0)

if __name__ == '__main__':
    verify_all_files()
