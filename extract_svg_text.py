import re
import xml.etree.ElementTree as ET

# Read the SVG file
with open("Rental Management System 24 hours.excalidraw.svg", 'r', encoding='utf-8') as f:
    content = f.read()

# Extract all text between > and < tags
text_pattern = r'>([^<]+)<'
all_text = re.findall(text_pattern, content)

# Filter out empty strings and XML declarations
filtered_text = [text.strip() for text in all_text if text.strip() and not text.strip().startswith('<?')]

# Remove duplicates while preserving order
seen = set()
unique_text = []
for text in filtered_text:
    if text not in seen:
        seen.add(text)
        unique_text.append(text)

# Print all extracted text
print("=" * 80)
print("ALL TEXT CONTENT EXTRACTED FROM EXCALIDRAW SVG DIAGRAM")
print("=" * 80)
print()

for i, text in enumerate(unique_text, 1):
    print(f"{i}. {text}")

print()
print(f"\nTotal unique text elements found: {len(unique_text)}")
