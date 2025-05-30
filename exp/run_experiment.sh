#!/bin/bash

TASK_COUNTS=(3 5 8 10)
DEVICE_COUNTS=(3 5 8)
WEIGHTS=("0 0 1" "1 1 1" "2 1 3" "1 5 1")

mkdir -p results
rm -f ./results/*.json

echo "tasks,devices,alpha,beta,gamma,total_cost,status,runtime_sec" > results/summary.csv

for n in "${TASK_COUNTS[@]}"; do
  for m in "${DEVICE_COUNTS[@]}"; do
    for weight in "${WEIGHTS[@]}"; do
      read -r alpha beta gamma <<< "$weight"
      id="n${n}_m${m}_a${alpha}b${beta}g${gamma}"
      
      input_file="./results/input_${id}.json"
      output_file="./results/input_${id}_solution.json"

      echo "Generating instance: $id"
      python -m edge_sched.cli generate --tasks $n --devices $m --output "$input_file" --layered

      echo "Solving instance: $id"
      SECONDS=0
      python -m edge_sched.cli solve "$input_file" --alpha $alpha --beta $beta --gamma $gamma --output "$output_file"
      runtime=$SECONDS

      # Extract solution results
      if [[ -f "$output_file" ]]; then
        total_cost=$(jq '.total_cost // "NA"' "$output_file")
        status=$(jq -r '.status // "FAIL"' "$output_file")
      else
        total_cost="NA"
        status="FAIL"
      fi

      echo "$n,$m,$alpha,$beta,$gamma,$total_cost,$status,$runtime" >> results/summary.csv
    done
  done
done
