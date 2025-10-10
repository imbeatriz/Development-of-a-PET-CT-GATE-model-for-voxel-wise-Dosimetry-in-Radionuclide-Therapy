#!/usr/bin/env python3
"""
====================================
GATE Parallel Job Splitter & Runner
====================================

This script automates splitting a GATE simulation into multiple smaller jobs
and runs them in parallel using Python's multiprocessing.

Each job gets its own time window, unique output names, and separate log files.

USAGE EXAMPLE:
--------------
    python3 gate_parallel_runner.py mySimulation.mac ./output 30 120

ARGUMENTS:
    1. macro_file   -> Path to your main GATE macro (.mac)
    2. output_dir   -> Folder where job macros, logs, and outputs will be saved
    3. time_slice   -> Time slice duration in seconds
    4. total_time   -> Total simulation time in seconds

OPTIONAL FLAGS:
    --num_jobs N        Manually set number of jobs (default = auto)
    --gate_exec PATH    Path to GATE executable (default = "Gate")
"""

import os
import re
import subprocess
import argparse
import math
from multiprocessing import Pool, cpu_count
from datetime import datetime


# -------------------------------------------------------------------------
# Utility Functions
# -------------------------------------------------------------------------
def color(text, c="cyan"):
    colors = {
        "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
        "blue": "\033[94m", "cyan": "\033[96m", "end": "\033[0m"
    }
    return f"{colors.get(c, '')}{text}{colors['end']}"


def print_usage_example():
    """Print a clear usage example when arguments are missing."""
    print(color("\n" + "="*60, "cyan"))
    print(color("GATE PARALLEL JOB RUNNER - USAGE", "cyan"))
    print(color("="*60, "cyan"))
    print("\n" + color("REQUIRED ARGUMENTS:", "yellow"))
    print("  macro_file    Path to your main GATE macro file (.mac)")
    print("  output_dir    Directory for job outputs and logs")  
    print("  time_slice    Time slice duration in seconds (e.g., 30, 10)")
    print("  total_time    Total simulation time in seconds (e.g., 120)")
    print("\n" + color("OPTIONAL ARGUMENTS:", "yellow"))
    print("  --num_jobs N     Number of parallel jobs (default: auto-calculate)")
    print("  --gate_exec PATH Path to GATE executable (default: 'Gate')")
    print("\n" + color("EXAMPLES:", "green"))
    print("  python3 gate_parallel_runner.py my_macro.mac ./output 30 120")
    print("  python3 gate_parallel_runner.py my_macro.mac ./output 30 120 --num_jobs 8")
    print("  python3 gate_parallel_runner.py my_macro.mac ./output 30 120 --gate_exec /usr/local/bin/Gate")
    print("\n" + color("NOTES:", "blue"))
    print("  - Each job runs a portion of the total simulation time")
    print("  - Output files are automatically renamed for each job")
    print("  - Logs are saved in output_dir/logs/")
    print("  - The script auto-calculates optimal job count based on available CPUs")


def calculate_optimal_jobs(total_time, time_slice, available_cpus):
    """Estimate a practical number of jobs to split the total simulation."""
    est_jobs = int(math.ceil(total_time / time_slice))
    return max(1, min(est_jobs, available_cpus * 2))


def run_gate_job(job_tuple):
    job_path, log_file, gate_exec = job_tuple
    print(color(f"Starting job: {job_path}", "blue"))
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    with open(log_file, 'w') as log:
        result = subprocess.run([gate_exec, job_path], stdout=log, stderr=subprocess.STDOUT)
    if result.returncode != 0:
        print(color(f"Job failed: {job_path} (exit {result.returncode}) → Check log: {log_file}", "red"))
    else:
        print(color(f"Completed: {job_path}", "green"))
    return result.returncode


def safe_replace_times_and_outputs(macro_content, start_time, stop_time, time_slice, output_dir, job_index):
    """Safely replaces time and output parameters in the macro file for each job."""
    content = macro_content
    content = re.sub(r"(/gate/application/setTimeStart)\s+[-+]?[0-9]*\.?[0-9]+\s+s",
                     fr"\1 {start_time} s", content)
    content = re.sub(r"(/gate/application/setTimeStop)\s+[-+]?[0-9]*\.?[0-9]+\s+s",
                     fr"\1 {stop_time} s", content)
    content = re.sub(r"(/gate/application/setTimeSlice)\s+[-+]?[0-9]*\.?[0-9]+\s+s",
                     fr"\1 {time_slice} s", content)

    content = re.sub(r"([\t ]*/gate/output/root/setFileName)\s+\S+",
                     fr"\1 {output_dir}/petVereos_job{job_index}", content)
    content = re.sub(r"([\t ]*/gate/output/summary/setFileName)\s+\S+",
                     fr"\1 {output_dir}/digit_summaryVereos_job{job_index}.txt", content)
    content = re.sub(r"([\t ]*/gate/actor/stat/save)\s+\S+",
                     fr"\1 {output_dir}/stats_job{job_index}", content)
    return content


def create_job_files(gate_macro_path, output_dir, total_time, time_slice, num_jobs, gate_executable="Gate"):
    with open(gate_macro_path, 'r') as f:
        macro_content = f.read()

    os.makedirs(output_dir, exist_ok=True)
    log_dir = os.path.join(output_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    time_per_job = total_time / num_jobs
    if time_slice > time_per_job:
        print(color(f"Warning: time_slice ({time_slice}s) > time_per_job ({time_per_job:.2f}s). Adjusting.", "yellow"))
        time_slice = max(0.01, time_per_job / 2.0)

    job_files = []
    for i in range(num_jobs):
        start_time = i * time_per_job
        stop_time = (i + 1) * time_per_job
        modified_content = safe_replace_times_and_outputs(macro_content, start_time, stop_time, time_slice, output_dir, i)
        job_file = os.path.join(output_dir, f"job_{i}.mac")
        with open(job_file, 'w') as f:
            f.write(modified_content)
        log_file = os.path.join(log_dir, f"job_{i}.log")
        job_files.append((job_file, log_file, gate_executable))

    print(color(f"\n Created {num_jobs} job files in {output_dir}", "green"))
    print(f"Logs will be saved in: {color(log_dir, 'blue')}")
    print(f"Time per job: {time_per_job:.2f} s | Time slice: {time_slice:.2f} s")
    return job_files


def run_jobs(job_files, suggested_parallel):
    """Prompt user for how many jobs to run in parallel and execute them."""
    user_parallel = input(color(f"\nEnter number of parallel jobs to run [{suggested_parallel}]: ", "cyan")).strip()
    parallel_jobs = suggested_parallel
    if user_parallel.isdigit() and int(user_parallel) > 0:
        parallel_jobs = int(user_parallel)

    print(color(f"\nRunning {len(job_files)} jobs using {parallel_jobs} parallel workers...", "green"))
    start_time = datetime.now()
    with Pool(parallel_jobs) as pool:
        pool.map(run_gate_job, job_files)
    end_time = datetime.now()
    print(color(f"\nAll jobs completed in {end_time - start_time}", "green"))


# -------------------------------------------------------------------------
# Custom Argument Parser
# -------------------------------------------------------------------------
class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        """Override error method to show usage example instead of generic error."""
        if "arguments are required" in message:
            print_usage_example()
            print(color(f"ERROR: {message}", "red"))
            self.exit(2)
        else:
            super().error(message)


# -------------------------------------------------------------------------
# Main Entry
# -------------------------------------------------------------------------
if __name__ == "__main__":
    available_cpus = cpu_count()

    parser = CustomArgumentParser(
        description="Split a GATE macro into multiple smaller jobs and run them in parallel.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s my_macro.mac ./output 30 120
  %(prog)s my_macro.mac ./output 30 120 --num_jobs 8
  %(prog)s my_macro.mac ./output 30 120 --gate_exec /usr/local/bin/Gate
        """
    )
    
    # Required arguments
    parser.add_argument("macro_file", 
                       help="Path to input GATE macro file (.mac)")
    parser.add_argument("output_dir", 
                       help="Output directory for job macros, logs, and simulation results")
    parser.add_argument("time_slice", type=float, 
                       help="Time slice duration in seconds (e.g., 30, 10)")
    parser.add_argument("total_time", type=float, 
                       help="Total simulation time in seconds (e.g., 60, 120, 300)")
    
    # Optional arguments
    parser.add_argument("--num_jobs", type=int, default=-1, 
                       help="Number of jobs to create (default: auto-calculate based on available CPUs)")
    parser.add_argument("--gate_exec", default="Gate", 
                       help="Path to GATE executable (default: 'Gate')")
    
    args = parser.parse_args()

    # Auto-calculate job count if not specified
    if args.num_jobs == -1:
        args.num_jobs = calculate_optimal_jobs(args.total_time, args.time_slice, available_cpus)
        print(color(f"\nAuto-calculated number of jobs: {args.num_jobs}", "yellow"))

    suggested_parallel_jobs = min(args.num_jobs, max(1, int(available_cpus * 0.75)))

    print(color("\n================= GATE Parallel Job Runner =================", "cyan"))
    print(f"Input macro:         {args.macro_file}")
    print(f"Output directory:    {args.output_dir}")
    print(f"Total simulation time: {args.total_time} s")
    print(f"Time slice:          {args.time_slice} s")
    print(f"Number of jobs:      {args.num_jobs}")
    print(f"Available CPUs:      {available_cpus}")
    print(f"Suggested parallel:  {suggested_parallel_jobs}")
    print(color("==============================================================\n", "cyan"))

    if not os.path.exists(args.macro_file):
        print(color(f"ERROR: Macro file not found: {args.macro_file}", "red"))
        exit(1)

    # Create job macros
    job_files = create_job_files(args.macro_file, args.output_dir, args.total_time, 
                               args.time_slice, args.num_jobs, args.gate_exec)

    # Run interactively
    run_jobs(job_files, suggested_parallel_jobs)
