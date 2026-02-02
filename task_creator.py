import pandas as pd
import os

def create_task_files(input_csv, group_column='repo'):
    # 1. Read CSV into DataFrame
    if not os.path.exists(input_csv):
        print(f"Error: {input_csv} not found.")
        return
        
    df = pd.read_csv(input_csv)
    
    # 2. Group by the specified column (e.g., 'language')
    grouped = df.groupby(group_column)
    
    # Create an output directory to keep things tidy
    os.makedirs("tasks", exist_ok=True)
    
    print(f"Processing {len(grouped)} language groups...")

    # 3. Loop over groups
    for group_name, group_data in grouped:
        # Sort by index to ensure group->index order
        group_data = group_data.sort_index()
        
        # Loop over individual rows in the group
        a = 0
        for i, (original_index, row) in enumerate(group_data.iterrows()):
            a += 1
            # Format group identity (sanitize for filename)
            identity = str(group_name).replace("/", "_").replace(" ", "_")
            
            # 4. Generate filename: task_n_group_identity.csv
            filename = f"task_{a}_{identity}.csv"
            filepath = os.path.join("tasks", filename)
            
            # Convert single row series back to DataFrame for saving
            row_df = row.to_frame().T
            
            # Save row as CSV
            row_df.to_csv(filepath, index=False)
            
    print(f"Done! Files saved in 'agent_evals/' directory.")

if __name__ == "__main__":
    create_task_files("Planning Agent Eval - eval_1.csv")