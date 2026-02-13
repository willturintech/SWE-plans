#!/bin/bash

# Directory to scan (default to current directory)
TARGET_DIR="plans"
# Delimiter separating the first word (default is underscore)
DELIM="_"

# 1. Get unique group prefixes (the 'firstword')
groups=$(ls "$TARGET_DIR" | grep "$DELIM" | cut -d"$DELIM" -f1 | sort -u)

# 2. Find the maximum number of files in any single group
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
threshold=20
start=9

# 3. Outer loop: Round-robin selection
for ((i=1; i<=max_count; i++)); do
    echo "--- Selection Round #$i ---"
    
    # 4. Inner loop: Iterate through each group
    for group in $groups; do
        
        # Get all files in this group
        files=($(ls "$TARGET_DIR"/${group}${DELIM}* | sort))
        ((count+=1))
        
        idx=$((i-1))
    
        if [ "$idx" -lt "${#files[@]}" ]; then
            selected_file="${files[$idx]}"
            # Strip path and extension to get the Instance ID (e.g., caddy__caddy-4774)
            filename=$(basename "$selected_file")
            instance_id="${filename%.*}" 
            
            echo "Task: [$count] -> Group: [$group] -> Selected: $instance_id"
            
            # --- EXECUTION LOGIC ---
            if ((count >= start)); then
                
                # 1. Construct Docker Image Name
                # Replaces '__' with '_1776_' to match SWE-bench image naming convention
                image_tag="${instance_id//__/_1776_}" 
                image_name="docker.io/swebench/sweb.eval.x86_64.${image_tag}:latest"
                
                echo "🐳 Pre-pulling image: $image_name"
                if docker pull "$image_name"; then
                    echo "✅ Image pulled successfully."
                else
                    echo "⚠️ Pull failed (or image name mismatch). Letting agent try anyway..."
                fi

                # 2. Run the Agent
                python mini-swe-agent/src/minisweagent/run/benchmarks/swebench_single.py \
                    --subset multilingual \
                    --instance "$instance_id" \
                    --output "executed_plans/eval_1_${instance_id}.traj.json" \
                    --split test \
                    --model gemini/gemini-3-pro-preview \
                    --yolo

                # 3. Memory Cleanup (Critical for VMs)
                echo "🧹 Cleaning up image and containers for $instance_id..."
                
                # Remove the stopped container created by the run
                docker container prune -f > /dev/null 2>&1
                
                # Remove the large image to free disk space
                docker rmi "$image_name" > /dev/null 2>&1
                
                echo "✨ Cleanup complete."
            fi
        fi
        
        # Stop if we hit the global limit
        if ((count >= threshold)); then
            echo "🛑 Threshold of $threshold reached. Stopping."
            break 2
        fi
    done
    echo ""
done