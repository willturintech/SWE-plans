#!/bin/bash

# Directory to scan (default to current directory)
TARGET_DIR="plans"
# Delimiter separating the first word (default is underscore)
DELIM="_"

# 1. Get unique group prefixes (the 'firstword')
groups=$(ls "$TARGET_DIR" | grep "$DELIM" | cut -d"$DELIM" -f1 | sort -u)

# 2. Find the maximum number of files in any single group to know how many loops to run
max_count=0
for group in $groups; do
    count=$(ls "$TARGET_DIR"/${group}${DELIM}* 2>/dev/null | wc -l)
    if [ "$count" -gt "$max_count" ]; then
        max_count=$count
    fi
done

echo "Found groups: $groups"
echo "Max items in a group: $max_count"
echo "--------------------------------"
count=0
threshold=10
# 3. Outer loop: Iterate through indexes (1st, 2nd, 3rd...)
for ((i=1; i<=max_count; i++)); do
    echo "--- Selection Round #$i ---"
    # 4. Inner loop: Iterate through each group
    for group in $groups; do
        # Get all files in this group as an array
        files=($(ls "$TARGET_DIR"/${group}${DELIM}* | sort))
        ((count+=1))
        # Calculate array index (i-1 because Bash arrays are 0-indexed)
        idx=$((i-1))
    
        # Check if this group has a file at the current index
        if [ "$idx" -lt "${#files[@]}" ]; then
            selected_file="${files[$idx]}"
            selected_file="${selected_file%???}"
            selected_file="$(basename "$selected_file")" # Remove last 3 characters (e.g., .md)
            echo "Group [$group] -> Selected: $selected_file"
            
            # PLACE YOUR LOGIC HERE
            python  mini-swe-agent/src/minisweagent/run/benchmarks/swebench_single.py   --subset multilingual   --instance $selected_file --output 'executed_plans/eval_1_'$selected_file'.traj.json'  --split test --model gemini/gemini-3-pro-preview --yolo
            # e.g., python execute_task.py "$selected_file"
        fi
        if ((count >= threshold)); then
            echo "threshold reached"
            break 2
        fi
    done
    echo ""
done