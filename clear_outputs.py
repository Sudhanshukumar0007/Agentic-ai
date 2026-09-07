import json
import glob
import os

for filepath in glob.glob('raw_files/*.ipynb'):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        
        # Clear outputs for all cells
        for cell in nb.get('cells', []):
            if 'outputs' in cell:
                cell['outputs'] = []
            if 'execution_count' in cell:
                cell['execution_count'] = None
                
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1)
            
        print(f"Cleared outputs for {filepath}")
    except Exception as e:
        print(f"Failed to process {filepath}: {e}")
