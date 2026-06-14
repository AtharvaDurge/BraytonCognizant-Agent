import os

script_dir = os.path.dirname(os.path.abspath(__file__))

def find_project_root(start_dir):
    current = start_dir
    for _ in range(5):  
        if os.path.isdir(os.path.join(current, 'data')):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.dirname(start_dir) if start_dir.endswith("scripts") else start_dir

base_dir = find_project_root(script_dir)
raw_path = os.path.join(base_dir, 'data', 'train_FD001.txt')
clean_path = os.path.join(base_dir, 'data', 'train_clean.txt')

if not os.path.exists(raw_path):
    print(f"❌ Error: Raw file missing at {raw_path}")
    exit()

print("🔄 Scrubbing irregular whitespace and trailing data bugs...")
clean_lines = []

with open(raw_path, 'r', encoding='utf-8') as f:
    for line in f:
        tokens = line.strip().split()
        if tokens:  
            clean_lines.append("\t".join(tokens))

with open(clean_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(clean_lines) + "\n")

print(f"✨ Success! Perfectly formatted dataset saved to: {clean_path}")