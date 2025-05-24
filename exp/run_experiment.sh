#!/bin/bash

TASK_COUNTS=(10 25 50)
# DEVICE_COUNTS=(5 10 25)
DEVICE_COUNTS=(10 20 30)
WEIGHTS=("1 1 1" "1 3 2" "1 5 1")

mkdir -p results
rm -r ./results/*.json

echo "tasks,devices,alpha,beta,gamma,total_cost,status" > results/summary.csv



for n in "${TASK_COUNTS[@]}"; do
  for m in "${DEVICE_COUNTS[@]}"; do
    for weight in "${WEIGHTS[@]}"; do
      read -r alpha beta gamma <<< "$weight"
      id="n${n}_m${m}_a${alpha}b${beta}g${gamma}"
      
      echo "generate experiment: $id"

      # Step 1: Generate input
      python -m edge_sched.cli generate --tasks $n --devices $m --output ./results/input_${id}.json --layered 

      # Step 2: Solve
    #   edge-sched solve input_${id}.json --alpha $alpha --beta $beta --gamma $gamma --output input_${id}_solution.json

    #   # Step 3: Extract result
    #   if [[ -f input_${id}_solution.json ]]; then
    #     total_cost=$(jq '.total_cost // "NA"' input_${id}_solution.json)
    #     status=$(jq -r '.status' input_${id}_solution.json)
    #   else
    #     total_cost="NA"
    #     status="FAIL"
    #   fi

    #   Step 4: Append to CSV
    #   echo "$n,$m,$alpha,$beta,$gamma,$total_cost,$status" >> results/summary.csv
    done
  done
done

# edge-sched solve '/home/zehua/edge_sched/exp/input_n50_m5_a1b1g1.json' --alpha 1 --beta 1 --gamma 1

for n in "${TASK_COUNTS[@]}"; do
  for m in "${DEVICE_COUNTS[@]}"; do
    for weight in "${WEIGHTS[@]}"; do
      read -r alpha beta gamma <<< "$weight"
      id="n${n}_m${m}_a${alpha}b${beta}g${gamma}"
      
      echo "Running experiment: $id"

      # Step 1: Generate input
    #   edge-sched generate --tasks $n --devices $m --output input_${id}.json --layered 

      # Step 2: Solve
      python -m edge_sched.cli solve input_${id}.json --alpha $alpha --beta $beta --gamma $gamma --output input_${id}_solution.json

    #   # Step 3: Extract result
    #   if [[ -f input_${id}_solution.json ]]; then
    #     total_cost=$(jq '.total_cost // "NA"' input_${id}_solution.json)
    #     status=$(jq -r '.status' input_${id}_solution.json)
    #   else
    #     total_cost="NA"
    #     status="FAIL"
    #   fi

    #   Step 4: Append to CSV
    #   echo "$n,$m,$alpha,$beta,$gamma,$total_cost,$status" >> results/summary.csv
    done
  done
done
