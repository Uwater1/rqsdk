import os
import json
import re

def parse_markdown(content):
    data = {}
    current_section = None
    
    lines = content.split('\n')
    
    # Title parsing
    if lines:
        title_match = re.match(r'^#\s+(.*?):\s+(.*?)\s+\((.*?)\)', lines[0])
        if title_match:
            data['title'] = title_match.group(1).strip()
            data['company_name'] = title_match.group(2).strip()
            data['symbol'] = title_match.group(3).strip()

    i = 1
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        # Section header
        header_match = re.match(r'^##\s+\d+\.\s+(.*)', line)
        if header_match:
            current_section = header_match.group(1).strip()
            data[current_section] = {}
            i += 1
            continue
            
        if current_section:
            # List items with key-value pairs
            kv_match = re.match(r'^-\s+\*\*(.*?)\*\*:\s*(.*)', line)
            if kv_match:
                key = kv_match.group(1).strip()
                value = kv_match.group(2).strip()
                # If we were in a list, but find a KV, we might need to handle it.
                # However, based on observed files, sections are either all KVs or all Lists or all Tables.
                if isinstance(data[current_section], list):
                    # Convert to dict if we find a KV pair in what we thought was a list
                    temp_list = data[current_section]
                    data[current_section] = {"_items": temp_list}
                
                if isinstance(data[current_section], dict):
                    data[current_section][key] = value
            
            # Simple list items (like for "所在指数")
            elif line.startswith('- '):
                item_value = line[2:].strip()
                if not data[current_section]:
                    data[current_section] = []
                
                if isinstance(data[current_section], list):
                    data[current_section].append(item_value)
                elif isinstance(data[current_section], dict):
                    # If it's already a dict (e.g. from previous KV pairs), append to a special key or handle error
                    if 'others' not in data[current_section]:
                        data[current_section]['others'] = []
                    data[current_section]['others'].append(item_value)
            
            # Table parsing
            elif line.startswith('|'):
                # Extract headers
                headers = [h.strip() for h in line.split('|')[1:-1]]
                i += 1
                # Skip separator line
                if i < len(lines) and re.match(r'^\|\s*:?---', lines[i].strip()):
                    i += 1
                
                table_data = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    row_values = [v.strip() for v in lines[i].split('|')[1:-1]]
                    # Pad row_values if it's shorter than headers
                    if len(row_values) < len(headers):
                        row_values.extend([''] * (len(headers) - len(row_values)))
                    row_dict = dict(zip(headers, row_values))
                    table_data.append(row_dict)
                    i += 1
                data[current_section] = table_data
                continue

        i += 1
        
    return data

def convert_recursive(base_dir):
    converted_count = 0
    for root, dirs, files in os.walk(base_dir):
        if 'introduction.md' in files:
            md_path = os.path.join(root, 'introduction.md')
            json_path = os.path.join(root, 'introduction.json')
            
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                parsed_data = parse_markdown(content)
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(parsed_data, f, ensure_ascii=False, indent=2)
                
                converted_count += 1
                if converted_count % 50 == 0:
                    print(f"Processed {converted_count} files...")
            except Exception as e:
                print(f"Error processing {md_path}: {e}")
                
    print(f"Finished! Total converted: {converted_count}")

if __name__ == "__main__":
    base_directory = "/home/hallo/Documents/rqsdk/basic"
    convert_recursive(base_directory)
