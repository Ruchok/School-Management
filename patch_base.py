import os
import re

with open('templates/base.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('user.role == "ADMIN" or user.role == "PRINCIPLE_ADMIN"', 'user.role == "ADMIN" or user.role == "PRINCIPLE_ADMIN" or user.role == "ACADEMIC_ADMIN"')

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated base.html")
