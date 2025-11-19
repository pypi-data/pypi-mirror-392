import os
import subprocess
import paramiko
import time
import shutil
import gnupg
import base64
import json
from pathlib import Path

# --- Constants ---
# REMOTE_SECURE_DIR is now dynamically determined
JOB_INFO_FILENAME = ".secure_slurm_job_info.json"

def run_secure_workflow(
    host, user, ssh_key_file, input_dir, exec_command, job_script_content, job_name, output_dir, keep_local_temp,
    nodes, ntasks_per_node, time, mem, partition, qos
):
    """
    Executes the full secure workflow.
    """
    local_paths = None # Initialize to None for finally block
    remote_paths = None # Initialize to None for finally block
    ssh_client = None # Initialize to None for finally block
    job_id = None # Initialize job_id for resume logic

    current_input_dir = Path(input_dir)
    job_info_path = _get_job_info_path(current_input_dir)
    job_info = _read_job_info(current_input_dir)
    
    # --- Resume/New Job Logic ---
    if job_info:
        print(f"Found previous job information for input directory '{current_input_dir}'.")
        print(f"  Remote Job Directory: {job_info.get('remote_paths', {}).get('job_dir', 'N/A')}")
        if job_info.get('job_id'):
            print(f"  Slurm Job ID: {job_info.get('job_id')}")
        
        while True:
            choice = input("Do you want to (r)esume, (s)tart a new job, or (e)xit? [r/s/e]: ").lower()
            if choice == 'r':
                local_paths_str = job_info.get('local_paths')
                if local_paths_str:
                    local_paths = {k: Path(v) for k, v in local_paths_str.items()}
                
                remote_paths = job_info.get('remote_paths')
                job_id = job_info.get('job_id')
                print("Resuming previous job...")
                break
            elif choice == 's':
                print("Starting a new job. Deleting previous job info...")
                job_info_path.unlink(missing_ok=True)
                job_info = {} # Reset job_info
                break
            elif choice == 'e':
                print("Exiting.")
                return
            else:
                print("Invalid choice. Please enter 'r', 's', or 'e'.")

    # --- 1. Prepare Local Env (only if starting new or local_paths not loaded) ---
    if not local_paths:
        try:
            local_paths = _prepare_local_env(current_input_dir, job_name)
            # Store local_paths in job_info file for persistence
            _write_job_info(current_input_dir, {'local_paths': {k: str(v) for k, v in local_paths.items()}})
            print("✓ Local environment prepared.")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error during local preparation: {e}")
            return
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return
    else:
        print("✓ Re-using local environment from previous run.")


    # --- 2. Connect and Execute Remote Workflow ---
    try:
        ssh_client = _create_ssh_client(host, user, ssh_key_file)
        with ssh_client as ssh:
            print(f"✓ SSH connection established to {host}.")
            
            # Prepare remote env (only if starting new or remote_paths not loaded)
            if not remote_paths:
                remote_paths = _prepare_remote_env(ssh, job_name)
                # Store remote_paths in job_info file for persistence
                _write_job_info(current_input_dir, {'remote_paths': remote_paths})
                print("✓ Remote environment prepared.")
            else:
                print("✓ Re-using remote environment from previous run.")

            # Check if key file needs re-upload and upload it along with encrypted data
            sftp = ssh.open_sftp()
            key_exists_on_remote = False
            try:
                sftp.stat(remote_paths['key_file'])
                key_exists_on_remote = True
            except FileNotFoundError:
                key_exists_on_remote = False # File not found is expected if it's missing on remote
            finally:
                sftp.close()
            
            if not key_exists_on_remote:
                print("  - Key file missing on remote or new job. Uploading key and encrypted data...")
                _upload_files(ssh, local_paths, remote_paths)
                print("✓ Encrypted data and key uploaded.")
            else:
                sftp = ssh.open_sftp()
                try:
                    sftp.stat(remote_paths['encrypted_zip_file'])
                    encrypted_data_exists_on_remote = True
                except FileNotFoundError:
                    encrypted_data_exists_on_remote = False
                finally:
                    sftp.close()
                if not encrypted_data_exists_on_remote :
                    print("  - Encrypted data missing on remote. Uploading encrypted data...")
                    # Assuming _upload_files also uploads encrypted_zip_file
                    _upload_files(ssh, local_paths, remote_paths)
                    print("✓ Encrypted data uploaded.")
                else:
                    print("✓ Encrypted data already on remote (assuming).")
            
            # Submit job (only if not already submitted)
            if not job_id:
                job_id = _submit_slurm_job(
                    ssh, exec_command, job_script_content, remote_paths, job_name,
                    nodes, ntasks_per_node, time, mem, partition, qos
                )
                _write_job_info(current_input_dir, {'job_id': job_id}) # Store job_id
                print(f"✓ Submitted Slurm job with ID: {job_id}")
            else:
                print(f"✓ Slurm job {job_id} already submitted. Resuming monitoring.")

            _monitor_job(ssh, job_id)
            print("✓ Job completed.")
            
            _download_and_decrypt(ssh, local_paths, remote_paths, Path(output_dir))
            print(f"✓ Results downloaded and decrypted to '{output_dir}'.")

    except paramiko.AuthenticationException:
        print("Authentication failed. Please check your username and SSH key.")
    except paramiko.SSHException as e:
        print(f"SSH connection error: {e}")
    except Exception as e:
        print(f"An error occurred during the remote workflow: {e}")
    finally:
        # --- Clean up local temporary files ---
        if not keep_local_temp and local_paths and local_paths["temp_dir"].exists():
            print("Cleaning up local temporary files...")
            shutil.rmtree(local_paths["temp_dir"])
            print("✓ Local cleanup complete.")
        elif keep_local_temp and local_paths and local_paths["temp_dir"].exists():
            print(f"  - Keeping local temporary directory: {local_paths['temp_dir']}")
        
        # --- Clean up remote job directory on headnode ---
        # Only cleanup if remote_paths was successfully created and a job was attempted/completed
        if ssh_client and remote_paths and remote_paths["job_dir"]:
            # Check if job was successful and results downloaded
            # (assuming successful if _download_and_decrypt didn't raise exception)
            # Or if user explicitly said 's'tart new and job_info removed
            if job_info_path.exists(): # If job info still exists, implies not fully successful yet or user chose 's' and it's a fresh start
                 if not job_info.get('job_id'): # If no job_id stored, implies job never submitted or chose 's'
                     print("Retaining remote job directory for inspection (no job_id recorded).")
                 else: # Job_id recorded, means job was submitted. Delete everything.
                    print("Cleaning up remote job directory on headnode...")
                    _cleanup_remote_job_dir(ssh_client, remote_paths["job_dir"])
                    print("✓ Remote cleanup complete.")
            else: # job_info_path does not exist, mean job fully completed successfully
                print("Cleaning up remote job directory on headnode...")
                _cleanup_remote_job_dir(ssh_client, remote_paths["job_dir"])
                print("✓ Remote cleanup complete.")
        
        # --- Remove job info file on successful completion ---
        # This occurs if the entire run_secure_workflow completes without unhandled errors
        # If job_info_path exists at this point, and job_id was successfully retrieved,
        # it means the job has gone through full lifecycle. Delete the info file.
        # If user chose 's', job_info_path was already unlinked
        if job_info_path.exists() and job_id and not job_info.get('job_id') == job_id : # job_id means it completed, and it's not a resumed entry.
             job_info_path.unlink(missing_ok=True)


def test_ssh_connection(host, user, ssh_key_file):
    """Tests the SSH connection to the remote host."""
    try:
        with _create_ssh_client(host, user, ssh_key_file):
            return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def _get_job_info_path(input_dir: Path) -> Path:
    """Returns the path to the job info file within the input directory."""
    return input_dir / JOB_INFO_FILENAME

def _read_job_info(input_dir: Path) -> dict:
    """Reads job information from the local file."""
    job_info_path = _get_job_info_path(input_dir)
    if job_info_path.exists():
        try:
            with open(job_info_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Corrupted job info file at {job_info_path}. Starting new job.")
            job_info_path.unlink(missing_ok=True) # Delete corrupted file
    return {}

def _write_job_info(input_dir: Path, new_info: dict):
    """Writes or updates job information to the local file."""
    job_info_path = _get_job_info_path(input_dir)
    current_info = _read_job_info(input_dir)
    current_info.update(new_info)
    # Convert Path objects to strings for JSON serialization
    serializable_info = {k: str(v) if isinstance(v, Path) else v for k, v in current_info.items()}
    with open(job_info_path, 'w') as f:
        json.dump(serializable_info, f, indent=4)

def _prepare_local_env(input_dir: Path, job_name: str):
    """
    Creates a local temp dir, generates a key, zips and encrypts the input data.
    Returns a dictionary of important paths.
    """
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    # Create a temporary directory for this job
    temp_dir = Path(f"./.secure_slurm_temp_{job_name}")
    temp_dir.mkdir(exist_ok=True)
    print(f"  - Created local temp directory: {temp_dir}")

    # 1. Generate a secret key file
    key_file = temp_dir / f"{job_name}.key"
    print(f"  - Generating secret key: {key_file}")
    passphrase = base64.b64encode(os.urandom(32)).decode('utf-8')
    with open(key_file, "w") as f:
        f.write(passphrase)
    
    # 2. Compress the input data folder
    zip_file = temp_dir / "input.zip"
    print(f"  - Compressing input data to: {zip_file}")
    subprocess.run(
        ["zip", "-r", str(zip_file.resolve()), "."],
        check=True, capture_output=True, cwd=str(input_dir)
    )

    # 3. Encrypt the zip file
    gpg = gnupg.GPG()
    encrypted_zip_file = temp_dir / "input.zip.gpg"
    print(f"  - Encrypting data to: {encrypted_zip_file}")
    with open(zip_file, 'rb') as f:
        status = gpg.encrypt_file(
            f,
            recipients=None, # Symmetric encryption
            symmetric='AES256',
            passphrase=passphrase,
            output=str(encrypted_zip_file)
        )
    if not status.ok:
        raise Exception(f"GPG encryption failed: {status.stderr}")

    return {
        "temp_dir": temp_dir.resolve(),
        "key_file": key_file.resolve(),
        "passphrase": passphrase, # Passphrase needs to be stored as string
        "encrypted_zip_file": encrypted_zip_file.resolve()
    }


def _create_ssh_client(host, user, ssh_key_file):
    """
    Establishes an SSH connection, resolving host aliases from ~/.ssh/config.
    CLI arguments for user and key file override config settings.
    """
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # --- SSH Config Resolution ---
    ssh_config_file = Path.home() / ".ssh" / "config"
    config = paramiko.SSHConfig()
    if ssh_config_file.exists():
        with open(ssh_config_file) as f:
            config.parse(f)

    host_config = config.lookup(host)
    
    connect_kwargs = {
        'hostname': host_config.get('hostname', host),
        'port': host_config.get('port', 22),
        'username': user or host_config.get('user'),
        'key_filename': ssh_key_file or host_config.get('identityfile', [None])[0]
    }

    if not connect_kwargs['username']:
        # If user is still not defined, paramiko will use the local username.
        print("  - No user specified, will use local username.")

    if not connect_kwargs['key_filename']:
        raise ValueError(
            "No SSH key file found. Please specify one with --ssh-key-file "
            "or define 'IdentityFile' in your .ssh/config."
        )
    
    if not Path(connect_kwargs['key_filename']).exists():
        raise FileNotFoundError(f"SSH key file not found: {connect_kwargs['key_filename']}")

    print(f"  - Connecting to {connect_kwargs['hostname']}:{connect_kwargs['port']} as {connect_kwargs['username']}")
    print(f"  - Using key: {connect_kwargs['key_filename']}")

    client.connect(**connect_kwargs, timeout=10)
    return client


def _prepare_remote_env(ssh: paramiko.SSHClient, job_name: str):
    """Creates the secure directories on the remote host."""
    # Get remote user's home directory
    stdin, stdout, stderr = ssh.exec_command("echo $HOME")
    remote_home = stdout.read().decode().strip()
    if not remote_home:
        raise Exception(f"Could not determine remote home directory: {stderr.read().decode()}")

    remote_secure_dir = f"{remote_home}/secure"
    remote_job_dir = f"{remote_secure_dir}/{job_name}-{int(time.time())}"
    
    print(f"  - Creating remote directory: {remote_job_dir}")
    stdin, stdout, stderr = ssh.exec_command(
        f"mkdir -p {remote_job_dir} && chmod 700 {remote_secure_dir} {remote_job_dir}"
    )
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        raise Exception(f"Error creating remote directory: {stderr.read().decode()}")

    return {
        "job_dir": remote_job_dir,
        "key_file": f"{remote_job_dir}/{Path(job_name).name}.key",
        "encrypted_zip_file": f"{remote_job_dir}/input.zip.gpg",
        "encrypted_output_file": f"{remote_job_dir}/output.zip.gpg",
        "slurm_script": f"{remote_job_dir}/job.sh",
        "slurm_output_log": f"{remote_job_dir}/slurm-%j.out",
        "slurm_error_log": f"{remote_job_dir}/slurm-%j.err",
        "encrypted_slurm_output_log": f"{remote_job_dir}/slurm-%j.out.gpg",
        "encrypted_slurm_error_log": f"{remote_job_dir}/slurm-%j.err.gpg",
    }


def _upload_files(ssh: paramiko.SSHClient, local_paths: dict, remote_paths: dict):
    """Uploads the key and encrypted data via SFTP."""
    sftp = ssh.open_sftp()
    try:
        # Upload key file
        local_key_file_path = local_paths["key_file"]
        print(f"  - Uploading {local_key_file_path} to {remote_paths['key_file']}")
        sftp.put(str(local_key_file_path), remote_paths["key_file"])
        
        # Set permissions on key file
        print(f"  - Setting permissions for remote key file")
        sftp.chmod(remote_paths["key_file"], 0o600)

        # Upload encrypted data
        local_encrypted_zip_file_path = local_paths["encrypted_zip_file"]
        print(f"  - Uploading {local_encrypted_zip_file_path} to {remote_paths['encrypted_zip_file']}")
        sftp.put(str(local_encrypted_zip_file_path), remote_paths["encrypted_zip_file"])
    finally:
        sftp.close()


def _submit_slurm_job(
    ssh: paramiko.SSHClient, exec_command: str, job_script_content: str, remote_paths: dict, job_name: str,
    nodes: int, ntasks_per_node: int, time_limit: str, mem: str, partition: str, qos: str
):
    """Generates, uploads, and submits the Slurm batch script."""

    # Determine the job body
    job_body = job_script_content if job_script_content else exec_command
    if not job_body:
        raise ValueError("Either exec_command or job_script_content must be provided.")

    sbatch_lines = [
        f"#SBATCH --job-name={job_name}",
        f"#SBATCH --output={remote_paths['slurm_output_log']}",
        f"#SBATCH --error={remote_paths['slurm_error_log']}",
        f"#SBATCH --nodes={nodes or 1}",
        f"#SBATCH --ntasks-per-node={ntasks_per_node or 1}",
        f"#SBATCH --time={time_limit or '01:00:00'}",
    ]

    if mem:
        sbatch_lines.append(f"#SBATCH --mem={mem}")
    if partition:
        sbatch_lines.append(f"#SBATCH --partition={partition}")
    if qos:
        sbatch_lines.append(f"#SBATCH --qos={qos}")

    sbatch_header = "\n".join(sbatch_lines)
    
    slurm_script_content = f"""#!/bin/bash
{sbatch_header}

echo "Starting job on node $SLURM_NODELIST"

# Create a temporary directory on the compute node's local storage
TMPDIR=$(mktemp -d /dev/shm/tmp.{job_name}.XXXXXX)
trap "echo 'Cleaning up temporary directory $TMPDIR'; rm -rf $TMPDIR" EXIT
cd $TMPDIR

echo "Temporary directory: $TMPDIR"
echo "Decrypting data..."
gpg --batch --yes --passphrase-file {remote_paths['key_file']} -o input.zip -d {remote_paths['encrypted_zip_file']}
unzip input.zip
rm input.zip

echo "Running user command..."
# =============================================================================
{job_body}
# =============================================================================
echo "User command finished."

echo "Encrypting results..."
zip -o output.zip -r .
gpg -c --batch --yes --passphrase-file {remote_paths['key_file']} -o {remote_paths['encrypted_output_file']} output.zip

echo "Job finished successfully."
"""
    
    # Upload the script
    sftp = ssh.open_sftp()
    try:
        print(f"  - Uploading Slurm script to {remote_paths['slurm_script']}")
        with sftp.file(remote_paths['slurm_script'], 'w') as f:
            f.write(slurm_script_content)
        sftp.chmod(remote_paths['slurm_script'], 0o755)
    finally:
        sftp.close()

    # Submit the job
    print("  - Submitting job to Slurm...")
    stdin, stdout, stderr = ssh.exec_command(f"sbatch {remote_paths['slurm_script']}")
    exit_status = stdout.channel.recv_exit_status()
    
    stdout_str = stdout.read().decode()
    if exit_status != 0:
        raise Exception(f"Slurm job submission failed: {stderr.read().decode()}")

    # "Submitted batch job 12345" -> "12345"
    try:
        job_id = stdout_str.strip().split()[-1]
        return int(job_id)
    except (ValueError, IndexError):
        raise Exception(f"Could not parse job ID from sbatch output: {stdout_str}")

def _monitor_job(ssh: paramiko.SSHClient, job_id: int):
    """Polls `squeue` until the job is no longer in the queue."""
    print(f"  - Monitoring job {job_id}. This may take a while...")
    while True:
        stdin, stdout, stderr = ssh.exec_command(f"squeue -j {job_id} -h")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            # If squeue fails, assume the job is done (it might have finished quickly)
            print("  - `squeue` command failed, assuming job is complete.")
            break
        
        queue_status = stdout.read().decode().strip()
        if not queue_status:
            # Empty output means the job is no longer in the queue
            print("  - Job no longer in queue.")
            break
        
        print(f"  - Job status: {queue_status.split()[4]}")
        time.sleep(15) # Poll every 15 seconds


def _download_and_decrypt(ssh: paramiko.SSHClient, local_paths: dict, remote_paths: dict, output_dir: Path):
    """Downloads, decrypts, and unzips the results."""
    
    # Create local output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"  - Created output directory: {output_dir}")

    local_encrypted_output = local_paths["temp_dir"] / "output.zip.gpg"
    
    # Download the encrypted output file
    sftp = ssh.open_sftp()
    try:
        print(f"  - Downloading results from {remote_paths['encrypted_output_file']}")
        sftp.get(remote_paths['encrypted_output_file'], str(local_encrypted_output))
    except FileNotFoundError:
        print(f"  - WARNING: Output file not found on remote: {remote_paths['encrypted_output_file']}")
        print(f"  - This can happen if the job failed or produced no output file.")
        print(f"  - Check the Slurm log file for details: {remote_paths['job_dir']}/slurm-*.out")
        return
    finally:
        sftp.close()

    # Decrypt the file
    gpg = gnupg.GPG()
    local_decrypted_zip = local_paths["temp_dir"] / "output.zip"
    print(f"  - Decrypting results to: {local_decrypted_zip}")
    with open(local_encrypted_output, 'rb') as f:
        status = gpg.decrypt_file(
            f,
            passphrase=local_paths['passphrase'],
            output=str(local_decrypted_zip)
        )
    
    if not status.ok:
        raise Exception(f"GPG decryption failed: {status.stderr}")


    # Unzip the results into the final output directory
    print(f"  - Unzipping results to: {output_dir}")
    subprocess.run(
        ["unzip", "-o", str(local_decrypted_zip), "-d", str(output_dir)],
        check=True, capture_output=True
    )

def _cleanup_remote_job_dir(ssh: paramiko.SSHClient, remote_job_dir: str):
    """Removes the remote job directory from the headnode."""
    try:
        stdin, stdout, stderr = ssh.exec_command(f"rm -rf {remote_job_dir}")
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            print(f"  - Warning: Failed to clean up remote directory {remote_job_dir}: {stderr.read().decode()}")
    except Exception as e:
        print(f"  - Warning: Error during remote cleanup of {remote_job_dir}: {e}")
