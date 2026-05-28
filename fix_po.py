import re

with open('locale/es/LC_MESSAGES/django.po', 'r', encoding='utf-8') as f:
    content = f.read()

# Split into blocks
blocks = re.split(r'\n(?=msgid )', content)

seen = set()
unique_blocks = []
for block in blocks:
    match = re.search(r'msgid "(.+?)"', block)
    if match:
        msgid = match.group(1)
        if msgid not in seen:
            seen.add(msgid)
            unique_blocks.append(block)
    else:
        unique_blocks.append(block)

with open('locale/es/LC_MESSAGES/django.po', 'w', encoding='utf-8') as f:
    f.write('\n'.join(unique_blocks))

print('Duplicates removed.')
