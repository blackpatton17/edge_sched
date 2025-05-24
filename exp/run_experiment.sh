#!/bin/bash

TASK_COUNTS=(5 10 30)
DEVICE_COUNTS=(20 50 100)
WEIGHTS=("0 0 1" "1 3 2" "1 5 1")

mkdir -p results
rm -f ./results/*.json

echo "tasks,devices,alpha,beta,gamma,total_cost,status,runtime_sec" > results/summary.csv

for n in "${TASK_COUNTS[@]}"; do
  for m in "${DEVICE_COUNTS[@]}"; do
    for weight in "${WEIGHTS[@]}"; do
      read -r alpha beta gamma <<< "$weight"
      id="n${n}_m${m}_a${alpha}b${beta}g${gamma}"

      echo "Generating instance: $id"
      python -m edge_sched.cli generate --tasks $n --devices $m --output ./results/input_${id}.json --layered
    done
  done
done

for n in "${TASK_COUNTS[@]}"; do
  for m in "${DEVICE_COUNTS[@]}"; do
    for weight in "${WEIGHTS[@]}"; do
      read -r alpha beta gamma <<< "$weight"
      id="n${n}_m${m}_a${alpha}b${beta}g${gamma}"
      
      echo "Running experiment: $id"
      
      # Measure start time (nanoseconds for higher resolution)
      start_time=$(date +%s.%N)

      python -m edge_sched.cli solve ./results/input_${id}.json --alpha $alpha --beta $beta --gamma $gamma --output ./results/input_${id}_solution.json

      end_time=$(date +%s.%N)
      echo "$end_time - $start_time"
      runtime=$(echo "$end_time - $start_time" | bc)

      solution="./results/input_${id}_solution.json"
      if [[ -f "$solution" ]]; then
        total_cost=$(jq '.total_cost // "NA"' "$solution")
        status=$(jq -r '.status' "$solution")
      else
        total_cost="NA"
        status="FAIL"
      fi

      echo "$n,$m,$alpha,$beta,$gamma,$total_cost,$status,$runtime" >> results/summary.csv
    done
  done
done
