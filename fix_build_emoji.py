#!/usr/bin/env python3
"""Fix emoji encoding issues in build.py"""

import re

file_path = "build.py"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all emojis with ASCII alternatives
replacements = {
    '❌': '[ERROR]',
    '✅': '[OK]',
    '⚙️': '[CONFIG]',
    '⚠️': '[WARNING]',
    '📦': '[PACKAGE]',
    '💾': '[SAVE]',
    '🌐': '[WEB]',
    '🖥️': '[SERVER]',
    '📝': '[INFO]',
    '🔧': '[TOOLS]',
}

for emoji, replacement in replacements.items():
    content = content.replace(emoji, replacement)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed all emoji encoding issues in build.py")
