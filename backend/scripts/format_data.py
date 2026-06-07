import os

script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.dirname(script_dir)) if script_dir.endswith("scripts") else os.path.dirname(script_dir)
raw_path = os.path.join(base_dir, 'data', 'train_FD001.txt')
clean_path = os.path.join(base_dir, 'data', 'train_clean.txt')

if not os.path.exists(raw_path):
    print(f"❌ Error: Raw file missing at {raw_path}")
    exit()

print("🔄 Scrubbing irregular whitespace and trailing data bugs...")
clean_lines = []

with open(raw_path, 'r', encoding='utf-8') as f:
    for line in f:
        # Split by any block of blank space elements, stripping leading/trailing spaces
        tokens = line.strip().split()
        if tokens:  # Skip completely empty rows if they exist
            # Re-join using a strict, unvarying single tab separator
            clean_lines.append("\t".join(tokens))

with open(clean_path, 'w', encoding='utf-8') as f:
    f.write("\n".join(clean_lines) + "\n")

print(f"✨ Success! Perfectly formatted dataset saved to: {clean_path}")