import os
import shutil
import csv

def get_basic_folders(basic_dir):
    folders = {}
    for item in os.listdir(basic_dir):
        path = os.path.join(basic_dir, item)
        if os.path.isdir(path):
            # Folder name is e.g. 000063.XSHE_中兴通讯
            code_part = item.split('_')[0] # 000063.XSHE
            folders[code_part] = item
    return folders

def convert_filename_to_code(filename):
    # sh_600000.csv -> 600000.XSHG
    # sz_000001.csv -> 000001.XSHE
    base = os.path.splitext(filename)[0]
    prefix, code = base.split('_')
    if prefix == 'sh':
        return f"{code}.XSHG"
    elif prefix == 'sz':
        return f"{code}.XSHE"
    return None

def move_and_update():
    basic_dir = 'basic'
    hs300_dir = 'hs300'
    zz500_dir = 'zz500'
    
    basic_folders = get_basic_folders(basic_dir)
    
    # Process HS300
    if os.path.exists(hs300_dir):
        for f in os.listdir(hs300_dir):
            if f.endswith('.csv'):
                code = convert_filename_to_code(f)
                if code in basic_folders:
                    target_dir = os.path.join(basic_dir, basic_folders[code])
                    src = os.path.join(hs300_dir, f)
                    dst = os.path.join(target_dir, 'price.csv')
                    shutil.move(src, dst)
                    print(f"Moved {f} to {target_dir}/price.csv")
                    
                    # Update introduction.md
                    intro_path = os.path.join(target_dir, 'introduction.md')
                    if os.path.exists(intro_path):
                        with open(intro_path, 'r', encoding='utf-8') as intro_f:
                            content = intro_f.read()
                        if '## 7. 所在指数' not in content:
                            with open(intro_path, 'a', encoding='utf-8') as intro_f:
                                intro_f.write('\n## 7. 所在指数\n- 沪深300\n')
    
    # Process ZZ500
    if os.path.exists(zz500_dir):
        for f in os.listdir(zz500_dir):
            if f.endswith('.csv'):
                code = convert_filename_to_code(f)
                if code in basic_folders:
                    target_dir = os.path.join(basic_dir, basic_folders[code])
                    src = os.path.join(zz500_dir, f)
                    dst = os.path.join(target_dir, 'price.csv')
                    shutil.move(src, dst)
                    print(f"Moved {f} to {target_dir}/price.csv")
                    
                    # Update introduction.md
                    intro_path = os.path.join(target_dir, 'introduction.md')
                    if os.path.exists(intro_path):
                        with open(intro_path, 'r', encoding='utf-8') as intro_f:
                            content = intro_f.read()
                        if '## 7. 所在指数' not in content:
                            with open(intro_path, 'a', encoding='utf-8') as intro_f:
                                intro_f.write('\n## 7. 所在指数\n- 中证500\n')

    # Delete directories
    if os.path.exists(hs300_dir) and not os.listdir(hs300_dir):
        os.rmdir(hs300_dir)
        print("Deleted hs300 directory")
    else:
        # If there are still files (maybe non-csv), don't remove or print warning
        if os.path.exists(hs300_dir):
            print(f"Warning: {hs300_dir} is not empty, not deleting.")

    if os.path.exists(zz500_dir) and not os.listdir(zz500_dir):
        os.rmdir(zz500_dir)
        print("Deleted zz500 directory")
    else:
        if os.path.exists(zz500_dir):
            print(f"Warning: {zz500_dir} is not empty, not deleting.")

if __name__ == "__main__":
    move_and_update()
