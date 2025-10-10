#!/usr/bin/env python3
"""
===================================
GATE ROOT Files Merger
===================================

This script merges multiple GATE ROOT output files into a single file using hadd.

USAGE EXAMPLE:
--------------
    python3 merge_root_files.py ./output merged_simulation.root

ARGUMENTS:
    1. input_dir    -> Directory containing ROOT files to merge
    2. output_file  -> Path for the output merged ROOT file

NOTES:
    - Looks for all *.root files in the input directory
    - Uses ROOT's hadd command for merging
    - Overwrites existing output file if -f flag is used
"""

import os
import subprocess
import argparse
import glob

def color(text, c="cyan"):
    """Add color to terminal output."""
    colors = {
        "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
        "blue": "\033[94m", "cyan": "\033[96m", "magenta": "\033[95m",
        "end": "\033[0m"
    }
    return f"{colors.get(c, '')}{text}{colors['end']}"

def print_usage_example():
    """Print a clear usage example when arguments are missing."""
    print(color("\n" + "="*60, "cyan"))
    print(color("GATE ROOT FILES MERGER - USAGE", "cyan"))
    print(color("="*60, "cyan"))
    print("\n" + color("REQUIRED ARGUMENTS:", "yellow"))
    print("  input_dir    Directory containing ROOT files to merge")
    print("  output_file  Name of the output merged ROOT file (with .root extention)")
    print("\n" + color("EXAMPLES:", "green"))
    print("  python3 merge_root_files.py ./output merged_root_file_name.root")
    print("\n" + color("NOTES:", "blue"))
    print("  - Merges all *.root files found in the input directory")
    print("  - Uses ROOT's 'hadd' command for efficient merging")
    print("  - Output file will be overwritten if it already exists")
    print("  - Requires ROOT to be installed and accessible in PATH")

def check_hadd_available():
    """Check if hadd command is available."""
    try:
        subprocess.run(["hadd", "-h"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def merge_root_files(input_dir, output_file):
    """
    Merges all ROOT files in the input directory into a single output file using hadd.
    
    Args:
        input_dir (str): Directory containing ROOT files
        output_file (str): Path for the output merged ROOT file
    """
    # Check if input directory exists
    if not os.path.exists(input_dir):
        print(color(f"ERROR: Input directory does not exist: {input_dir}", "red"))
        return False

    if not os.path.isdir(input_dir):
        print(color(f"ERROR: Input path is not a directory: {input_dir}", "red"))
        return False

    # Get list of root files using glob for better pattern matching
    root_files = glob.glob(os.path.join(input_dir, "*.root"))
    
    if not root_files:
        print(color(f"ERROR: No ROOT files (*.root) found in directory: {input_dir}", "red"))
        print(color("Please check the directory path and ensure ROOT files exist.", "yellow"))
        return False

    # Sort files for consistent ordering
    root_files.sort()

    print(color(f"\nFound {len(root_files)} ROOT files to merge:", "green"))
    for i, file in enumerate(root_files[:5]):  # Show first 5 files
        print(f"  {i+1}. {os.path.basename(file)}")
    if len(root_files) > 5:
        print(f"  ... and {len(root_files) - 5} more files")

    # Check if output directory exists, create if needed
    output_dir = os.path.dirname(output_file) if os.path.dirname(output_file) else "."
    os.makedirs(output_dir, exist_ok=True)

    # Check if output file already exists
    if os.path.exists(output_file):
        print(color(f"Warning: Output file already exists and will be overwritten: {output_file}", "yellow"))

    # Prepare hadd command
    command = ["hadd", "-f", output_file] + root_files

    print(color(f"\nMerging {len(root_files)} files into: {output_file}", "cyan"))
    print(color("This may take a while depending on file sizes...", "blue"))

    try:
        # Run hadd command with progress indication
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Check if output file was created and has reasonable size
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file) / (1024 * 1024)  # Size in MB
                print(color(f"\n✓ Merging completed successfully!", "green"))
                print(color(f"Output file: {output_file} ({file_size:.2f} MB)", "green"))
                return True
            else:
                print(color("ERROR: Merging appeared successful but output file was not created.", "red"))
                return False
        else:
            print(color(f"\n✗ Merging failed with error code {result.returncode}", "red"))
            if result.stderr:
                print(color("Error message:", "red"))
                print(color(result.stderr, "red"))
            return False

    except KeyboardInterrupt:
        print(color("\n✗ Merging interrupted by user.", "yellow"))
        # Clean up partially created output file
        if os.path.exists(output_file):
            os.remove(output_file)
            print(color("Removed partially created output file.", "yellow"))
        return False
    except Exception as e:
        print(color(f"\n✗ Unexpected error during merging: {e}", "red"))
        return False

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        """Override error method to show usage example instead of generic error."""
        if "arguments are required" in message:
            print_usage_example()
            print(color(f"ERROR: {message}", "red"))
            self.exit(2)
        else:
            super().error(message)

def main():
    """Main function with enhanced argument parsing and error handling."""
    parser = CustomArgumentParser(
        description="Merge multiple GATE ROOT output files into a single file using hadd.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./output merged_simulation.root
  %(prog)s ./job_results final_scan.root
  %(prog)s /path/to/sim/data merged_output.root
        """
    )
    
    # Required arguments
    parser.add_argument("input_dir", 
                       help="Directory containing ROOT files to merge")
    parser.add_argument("output_file", 
                       help="Path for the output merged ROOT file (e.g., merged_output.root)")
    
    args = parser.parse_args()

    # Check if hadd is available
    if not check_hadd_available():
        print(color("ERROR: 'hadd' command not found!", "red"))
        print(color("Please ensure ROOT is installed and available in your PATH.", "yellow"))
        print(color("You can install ROOT from: https://root.cern/install/", "blue"))
        return

    print(color("\n================= GATE ROOT Files Merger =================", "cyan"))
    print(f"Input directory:  {args.input_dir}")
    print(f"Output file:      {args.output_file}")
    print(color("============================================================\n", "cyan"))

    # Merge the files
    success = merge_root_files(args.input_dir, args.output_file)
    
    if success:
        print(color("\n" + "="*50, "green"))
        print(color("MERGE COMPLETED SUCCESSFULLY!", "green"))
        print(color("="*50, "green"))
    else:
        print(color("\n" + "="*50, "red"))
        print(color("MERGE FAILED!", "red"))
        print(color("="*50, "red"))
        exit(1)

if __name__ == "__main__":
    main()
