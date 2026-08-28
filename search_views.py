#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

with open(r'c:\Users\Divine\powertracker\backend\tracker\tests.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if ('test_admin_voit_et_ferme_toutes_les_sessions' in line or 
        'test_admin_voit_et_ferme_tous_les_pleins' in line) and i > 0:
        print(f'{i+1}: {line.rstrip()}')
        # Print next 30 lines
        for j in range(1, 30):
            if i+j < len(lines):
                print(f'{i+j+1}: {lines[i+j].rstrip()}')
        print('---')
