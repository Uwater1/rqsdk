import os
import csv

def get_mapping(csv_file):
    mapping = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row['code']  # sh.600000
            name = row['code_name']
            mapping[code] = name
    return mapping

h_map = get_mapping('hs300_l.csv')
z_map = get_mapping('zz500-l.csv')

overlap = set(h_map.keys()) & set(z_map.keys())
print(f"Overlap: {overlap}")
print(f"HS300 count: {len(h_map)}")
print(f"ZZ500 count: {len(z_map)}")
