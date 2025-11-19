import argparse
from . import workflow
from pathlib import Path
try:
    from importlib import resources
except ImportError:
    import importlib_resources as resources

def main():
    # --- Default SSH Key ---
    default_ssh_key = Path.home() / ".ssh" / "id_rsa"

    parser = argparse.ArgumentParser(
        description="Secure Slurm Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # --- Global arguments ---
    parser.add_argument("--host", required=True, help="HPC hostname or IP address.")
    parser.add_argument("--user", required=False, help="SSH username (can be omitted if defined in .ssh/config).")
    parser.add_argument(
        "--ssh-key-file",
        default=str(default_ssh_key) if default_ssh_key.exists() else None,
        help=f"Path to your SSH private key file. (default: {default_ssh_key})"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- 'run' command ---
    run_parser = subparsers.add_parser("run", help="Encrypt, upload, run a job, and retrieve results.")
    run_parser.add_argument("--input-dir", required=True, help="Path to the local input data directory.")
    run_parser.add_argument("--job-name", default="secure-job", help="Name for the Slurm job.")
    run_parser.add_argument("--output-dir", default="./slurm-output", help="Local directory to store results.")
    run_parser.add_argument("--keep-local-temp", action="store_true", help="Do not delete the local temporary directory after the workflow completes.")

    # Slurm parameters
    run_parser.add_argument("--nodes", type=int, default=1, help="Number of nodes to request for the job.")
    run_parser.add_argument("--ntasks-per-node", type=int, default=1, help="Number of tasks per node.")
    run_parser.add_argument("--time", default="01:00:00", help="Time limit for the job (e.g., '01:00:00' for 1 hour).")
    run_parser.add_argument("--mem", help="Memory per node (e.g., '4G' for 4 Gigabytes).")
    run_parser.add_argument("--partition", help="Request a specific partition.")
    run_parser.add_argument("--qos", help="Request a quality of service.")

    # Mutually exclusive group for exec_command or script_file
    exec_group = run_parser.add_mutually_exclusive_group(required=True)
    exec_group.add_argument(
        "--exec",
        dest="exec_command",
        help="The command to execute on the compute node (e.g., 'grep sensitive input/patient.txt > processed.txt')."
    )
    exec_group.add_argument(
        "--script-file",
        help="Path to a local script file containing the commands to execute on the compute node."
    )

    # --- 'test-connection' command ---
    test_parser = subparsers.add_parser("test-connection", help="Test the SSH connection using the provided key.")

    # --- 'test-job' command ---
    test_job_parser = subparsers.add_parser("test-job", help="Submit a predefined example job to test the full workflow.")
    test_job_parser.add_argument("--output-dir", default="./slurm-output-test", help="Local directory to store results for the test job. (default: ./slurm-output-test)")
    test_job_parser.add_argument("--keep-local-temp", action="store_true", help="Do not delete the local temporary directory after the workflow completes.")


    args = parser.parse_args()

    if args.command == "run":
        # Read script file content if provided
        job_script_content = None
        if args.script_file:
            try:
                with open(args.script_file, 'r') as f:
                    job_script_content = f.read()
            except FileNotFoundError:
                print(f"Error: Script file not found at '{args.script_file}'.")
                return
            except Exception as e:
                print(f"Error reading script file '{args.script_file}': {e}")
                return

        print(f"Starting secure workflow for user '{args.user}' on host '{args.host}'...")
        workflow.run_secure_workflow(
            host=args.host,
            user=args.user,
            ssh_key_file=args.ssh_key_file,
            input_dir=args.input_dir,
            exec_command=args.exec_command, # This will be None if script_file is used
            job_script_content=job_script_content, # This will be None if exec_command is used
            job_name=args.job_name,
            output_dir=args.output_dir,
            keep_local_temp=args.keep_local_temp,
            nodes=args.nodes,
            ntasks_per_node=args.ntasks_per_node,
            time=args.time,
            mem=args.mem,
            partition=args.partition,
            qos=args.qos
        )
        print("Workflow finished.")
    
    elif args.command == "test-job":
        with resources.as_file(resources.files('secbatch').joinpath('example_input')) as example_input_dir:
            if not example_input_dir.is_dir():
                print(f"Error: Example input directory not found at '{example_input_dir}'.")
                return

            print(f"Starting secure test job workflow for user '{args.user}' on host '{args.host}'...")
            print(f"  - Using example input from: {example_input_dir}")
            
            workflow.run_secure_workflow(
                host=args.host,
                user=args.user,
                ssh_key_file=args.ssh_key_file,
                input_dir=str(example_input_dir),
                exec_command="grep sensitive input/patient.txt > processed.txt",
                job_script_content=None,
                job_name="secure-test-job",
                output_dir=args.output_dir,
                keep_local_temp=args.keep_local_temp,
                nodes=1,
                ntasks_per_node=1,
                time="00:10:00", # 10 minutes should be enough
                mem="1G",
                partition=None,
                qos=None
            )
        print("Test job workflow finished.")

    elif args.command == "test-connection":
        print(f"Testing connection to {args.user}@{args.host}...")
        if workflow.test_ssh_connection(host=args.host, user=args.user, ssh_key_file=args.ssh_key_file):
            print("Connection successful!")
        else:
            print("Connection failed.")


if __name__ == "__main__":
    main()
