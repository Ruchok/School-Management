import os
import re

with open('school_admin/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('("ADMIN", "PRINCIPLE_ADMIN")', '("ADMIN", "PRINCIPLE_ADMIN", "ACADEMIC_ADMIN")')

with open('school_admin/views.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated school_admin/views.py")
