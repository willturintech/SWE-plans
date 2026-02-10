import pandas as pd
import os

def rename_task_files(input_csv, group_column='repo', id_column='task_id'):
    """
    Renames files from 'task_N_repo.csv' to '{task_id}.csv'.
    Matches the exact generation logic to ensure the correct row maps to the correct file.
    """
    # 1. Verification
    if not os.path.exists(input_csv):
        print(f"❌ Error: {input_csv} not found.")
        return
       
    df = pd.read_csv(input_csv)
       
    # Check if the ID column exists (Fall back to 'instance_id' if 'task_id' is missing)
    if id_column not in df.columns:
        if 'instance_id' in df.columns:
            print(f"ℹ️ Column '{id_column}' not found. Switching to 'instance_id'.")
            id_column = 'instance_id'
        else:
            print(f"❌ Error: Neither '{id_column}' nor 'instance_id' found in CSV headers.")
            return

    # 2. Re-create the exact grouping logic
    grouped = df.groupby(group_column)
    renamed_count = 0
    missing_count = 0
    
    print(f"📂 Processing {len(grouped)} groups...")

    # 3. Iterate groups exactly as the creation script did
    for group_name, group_data in grouped:
        # CRITICAL: Sort by index to match the original file creation order
        group_data = group_data.sort_index()
        
        a = 0
        for i, (original_index, row) in enumerate(group_data.iterrows()):
            a += 1
            
            # --- A. Reconstruct Old Filename ---
            # Must match: str(group_name).replace("/", "_").replace(" ", "_")
            identity = str(group_name).replace("/", "_").replace(" ", "_")
            old_filename = f"plan_task_{a}_{identity}.md"
            old_filepath = os.path.join("plans", old_filename)
            
            # --- B. Construct New Filename ---
            # Using the task_id from the row
            task_id = str(row[id_column]).strip()
            
            # Sanitize just in case ID has slashes (unlikely for task IDs but good practice)
            safe_task_id = task_id.replace("/", "_") 
            new_filename = f"{safe_task_id}.md"
            new_filepath = os.path.join("plans", new_filename)
            
            # --- C. Execute Rename ---
            if os.path.exists(old_filepath):
                try:
                    os.rename(old_filepath, new_filepath)
                    renamed_count += 1
                except OSError as e:
                    print(f"⚠️ Error renaming {old_filename}: {e}")
            else:
                # This might happen if you deleted some files or changed the CSV
                missing_count += 1
                # print(f"⚠️ Warning: Could not find {old_filename}")

    print("-" * 30)
    print(f"✅ Success! Renamed {renamed_count} files.")
    if missing_count > 0:
        print(f"⚠️ Skipped {missing_count} files (not found).")


from pathlib import Path

def convert_to_md_extension(directory_path: str):
    """
    Renames all files in the given directory to have a .md extension.
    
    Args:
        directory_path (str): The path to the 'plans' directory.
    """
    # 1. Create a Path object for easier manipulation
    path = Path(directory_path)
    
    # Verify directory exists
    if not path.exists() or not path.is_dir():
        print(f"❌ Error: Directory '{directory_path}' not found.")
        return

    renamed_count = 0
    
    print(f"📂 Scanning directory: {directory_path}")

    # 2. Iterate over all files in the directory
    for file_path in path.iterdir():
        # Skip directories, only process files
        if file_path.is_file():
            
            # Skip files that are already .md
            if file_path.suffix == '.md':
                continue
            
            # 3. Construct new filename with .md extension
            new_path = file_path.with_suffix('.md')
            
            try:
                # 4. Rename the file
                file_path.rename(new_path)
                print(f"✅ Renamed: {file_path.name} -> {new_path.name}")
                renamed_count += 1
            except OSError as e:
                print(f"⚠️ Error renaming {file_path.name}: {e}")

    print("-" * 30)
    print(f"🎉 Completed! Converted {renamed_count} files to .md")
'''
# --- Usage Example ---
if __name__ == "__main__":
    # Replace 'plans' with your actual folder path
    convert_to_md_extension("plans")
'''

if __name__ == "__main__":
    # ⚠️ Check: Ensure 'task_id' matches your actual column name (e.g., instance_id)
    rename_task_files("SWE_Bench_Top_Repos.csv", id_column="task_id")