import subprocess
import re
import argparse
import os


def run_valgrind_trace(docker_image, binary):
    """Runs the valgrind trace command inside a Docker container and retrieves the output."""
    command = [
        "docker",
        "run",
        "-it",
        "--rm",
        "-v",
        f"{os.getcwd()}:/temp",
        "--privileged",
        "--cap-add",
        "SYS_ADMIN",
        "--security-opt",
        "seccomp=unconfined",
        "-w",
        "/temp",
        docker_image,
        "valgrind",
        "--tool=lackey",
        "--trace-mem=yes",
        "--log-file=results.txt",
        f"./{binary}",
    ]

    print("Running:", " ".join(command))
    subprocess.run(command, check=True)


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
        "--docker-image",
        type=str,
        required=True,
        help="Docker image to use for running Valgrind",
    )
    parser.add_argument(
        "--binary",
        type=str,
        required=True,
        help="Binary file to execute inside Valgrind",
    )

    args = parser.parse_args()

    run_valgrind_trace(args.docker_image, args.binary)
    parse_trace_file("results.txt", "instruction_trace.txt", "memory_trace.txt")
