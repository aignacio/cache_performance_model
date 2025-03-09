import subprocess
import re
import argparse
import os


def parse_trace_file(input_file, instruction_file, memory_file):
    with open(input_file, "r") as infile, open(
        instruction_file, "w"
    ) as instr_out, open(memory_file, "w") as mem_out:
        for line in infile:
            parts = line.strip().split()
            if len(parts) != 2:
                continue  # Skip lines that do not match expected format

            access_type, address_size = parts
            if "," not in address_size:
                continue  # Skip malformed lines

            address, _ = address_size.split(",")

            if access_type == "I":
                instr_out.write(f"read,{address}\n")
            elif access_type == "S":
                mem_out.write(f"write,{address}\n")
            elif access_type == "L":
                mem_out.write(f"read,{address}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run Valgrind trace in Docker and parse the output."
    )
    parser.add_argument(
        "--results",
        type=str,
        required=False,
        default='results.txt',
        help="Valgrind log",
    )
    parser.add_argument(
        "--instruction",
        type=str,
        required=False,
        default='instruction_trace.txt',
        help="Instruction trace",
    )
    parser.add_argument(
        "--memory",
        type=str,
        required=False,
        default='memory_trace.txt',
        help="Memory trace",
    )

    args = parser.parse_args()
    parse_trace_file(args.results, args.instruction, args.memory)
