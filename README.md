# Recursive Gang Scheduling Replication Project

## Project Structure

```bash
.
├── data
│   ├── input
│   │   └── parquet
│   └── output
├── figure
├── script
├── src
├── test
└── test_data
```

- `data`: contains the input task sets stored in **Parquet** files within the `input` subdirectory. The output of `eval.py` is stored in the `output` subdirectory as **CSV** files
- `figure`: contains figures generated from the files in `data/output` using `matplotlib`
- `script`: contains Python scripts
	- `eval.py`: Evaluates a task-partition mapping algorithm using the input data in `data/input`
	- `replicate_results.py`: Reads the output evaluation data from `data/output` and generates a table in LaTex format to replicate the results from the original paper
	- `prepare_data.py`: packs the task set input data into a single **Pickle** file for faster batch loading during evaluation
	- `stress_tests.py`: runs the **RPS** algorithm on a failing edge case
	- `compare_priority_policies.py`: Compares different prioritization policies on **RPS** and generates a LaTeX table summarizing schedulabilty results
	- `compute_statistics.py`: Visualizes aggregate metrics computed from evaluation results data by task set utilization or by (number of processors and size of task set)
	- `perform_chi_square.py`: Performs chi-square test to see if the replication deviates too much from the original results
	- `generate_task_sets.py`: Implements the `UUnifast` algorithm used for generating a random task set
	- `generate_eval_data.py`: Produces 320,000 randomly generated task sets. **Warning:** Running this script may produce a lot of files in the `data/` directory
	- `consolidate_eval_data.py`: Shrinks the number of input task set files in `data/` to simplify data loading
- `src`: Contains the implementations of each task-partition mapping algorithms and utility modules with helper methods
## Dependencies

Python packages used

- Numpy
- Matplotlib
- fastparquet
- Pandas

## How to Use

**Warning:** It may take a while (a minute or so) to clone the repository

```bash
git clone https://github.com/anthonybrown0528/recursive-partitioned-scheduling-replication.git

cd recursive-partitioned-scheduling-replication 
```

### To run evaluation scripts

```bash
python script/eval.py --output-dir <OUTPUT_DIR> --output <OUTPUT_FILENAME> --type <ALGORITHM>
```

### To generate figures
**Note:** You can comment or uncomment specific lines in the script to generate figures by desired data attribute
```bash
python script/compute_statistics.py
```

### To run edge case scenarios
```bash
python script/stress_tests.py
```

### To generate replication data
```bash
python script/replicate_results.py
```

### To perform chi-square test on replication data
```bash
python script/perform_chi_square.py
```

## Reference
**This project is an attempt to replicate the following work**

S. Lee, N. Guan and J. Lee, "Recursive Partitioned Scheduling for Real-Time Gang Tasks," 2025 IEEE Real-Time Systems Symposium (RTSS), Boston, MA, USA, 2025, pp. 135-147, doi: 10.1109/RTSS66672.2025.00020. keywords: {Processor scheduling;Instruction sets;Simulation;Interference;Computer architecture;Parallel processing;Real-time systems;Timing;Partitioning algorithms},

```
@INPROCEEDINGS{11315069,
  author={Lee, Seongtae and Guan, Nan and Lee, Jinkyu},
  booktitle={2025 IEEE Real-Time Systems Symposium (RTSS)}, 
  title={Recursive Partitioned Scheduling for Real-Time Gang Tasks}, 
  year={2025},
  volume={},
  number={},
  pages={135-147},
  keywords={Processor scheduling;Instruction sets;Simulation;Interference;Computer architecture;Parallel processing;Real-time systems;Timing;Partitioning algorithms},
  doi={10.1109/RTSS66672.2025.00020}}

```