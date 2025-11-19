# SecBatch

A CLI tool to simplify running jobs with encrypted data on a Slurm cluster. This tool automates key generation, data encryption, uploading, Slurm job submission, monitoring, and result retrieval.

## Installation

### Prerequisites

Before installing, you must have the following command-line tools available in your system's PATH:

-   **GnuPG (gpg):** For encryption and decryption.
-   **zip:** For compressing data.

You can typically install these using your system's package manager (e.g., `apt-get`, `brew`, `yum`).

### Installing with `uv`

Once the prerequisites are met, you can install the tool from PyPI using `uv`:

```bash
uv pip install secbatch
```

This will install the tool and make the `secbatch` command available in your environment.

## Usage

After installation, you can use the `secbatch` command directly.

### Full Command Reference

```
secbatch --host <your-host> <command> [options]
```

**Global Arguments:**

-   `--host`: The SSH hostname or an alias from your `~/.ssh/config`.
-   `--user`: (Optional) Your SSH username. Overrides the user in `~/.ssh/config`.
-   `--ssh-key-file`: (Optional) Path to your SSH private key. Overrides the `IdentityFile` in `~/.ssh/config`. Defaults to `~/.ssh/id_rsa`.

**Commands:**

-   `run`: Execute the full secure workflow.
    -   `--input-dir`: The local directory containing your input data.
    -   `--exec`: The command to execute on the compute node.
    -   `--script-file`: Path to a local script file to execute.
    -   `--output-dir`: The local directory for results.
    -   `--job-name`: (Optional) A name for the Slurm job.
    -   ... (and other Slurm parameters like `--nodes`, `--time`, etc.)

-   `test-connection`: Test the SSH connection to the host.

-   `test-job`: Submit a predefined example job to test the full workflow.

### Example: Running a Job

```bash
secbatch --host my-cluster run \
    --input-dir ./my-data \
    --exec 'grep "sensitive" input/patient.txt > processed.txt' \
    --output-dir ./results
```

## For Developers

### Building a Standalone Windows Executable

You can create a standalone `.exe` file for Windows that bundles the Python interpreter and all dependencies. This allows users to run the tool without a local Python installation, although **GnuPG for Windows is still required**.

1.  **Set up the project and install PyInstaller:**
    ```bash
    # Clone the repository
    git clone <repository-url>
    cd secbatch

    # Create a virtual environment and install dependencies
    uv venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
    uv pip install pyinstaller
    ```

2.  **Run PyInstaller:**
    The following command will create a single executable file in the `dist` directory.

    ```bash
    pyinstaller --onefile --name secbatch src/secbatch/main.py
    ```

3.  **Distribute:**
    The resulting `dist/secbatch.exe` can be distributed to Windows users. Remind them to install [Gpg4win](https://www.gpg4win.org/) to provide the required `gpg` dependency.
