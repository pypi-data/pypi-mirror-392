"""
Fakestack - High-Performance Database Generator

Python wrapper for the Go core binary.
Zero dependencies, blazing-fast database generation.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path


def get_binary_path():
    """
    Detect platform and architecture, return path to appropriate Go binary.

    Returns:
        Path: Path to the platform-specific fakestack binary

    Raises:
        RuntimeError: If binary not found for current platform
    """
    # Detect operating system
    system = platform.system().lower()
    system_map = {"linux": "linux", "darwin": "darwin", "windows": "windows"}
    os_name = system_map.get(system, system)

    # Detect architecture
    machine = platform.machine().lower()
    arch_map = {
        "x86_64": "amd64",
        "amd64": "amd64",
        "arm64": "arm64",
        "aarch64": "arm64",
    }
    arch_name = arch_map.get(machine, "amd64")

    # Construct binary name
    binary_name = f"fakestack-{os_name}-{arch_name}"
    if os_name == "windows":
        binary_name += ".exe"

    # Find binary in package
    bin_dir = Path(__file__).parent / "bin"
    binary_path = bin_dir / binary_name

    if not binary_path.exists():
        raise RuntimeError(
            f"Binary not found: {binary_path}\n"
            f"Platform: {os_name}-{arch_name}\n"
            f"Please report this issue at: https://github.com/0xdps/fake-stack/issues"
        )

    return binary_path


def run_fakestack(args=None):
    """
    Execute the Go binary with given arguments.

    Args:
        args (list, optional): Command-line arguments. Defaults to sys.argv[1:].

    Returns:
        int: Exit code from the Go binary (0 = success, non-zero = error)
    """
    if args is None:
        args = sys.argv[1:]

    try:
        binary = get_binary_path()

        # Make binary executable on Unix systems
        if platform.system() != "Windows":
            try:
                os.chmod(binary, 0o755)
            except (OSError, PermissionError):
                # Already executable or no permission - ignore
                pass

        # Execute the Go binary
        result = subprocess.run(
            [str(binary)] + args,
            cwd=os.getcwd(),
            # Stream output directly to console
            stdout=None,
            stderr=None,
        )

        return result.returncode

    except FileNotFoundError as e:
        print(f"Error: Binary not found - {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def fakestack(args=None):
    """
    Main API entry point. Alias for run_fakestack.

    Args:
        args (list, optional): Command-line arguments

    Returns:
        int: Exit code (0 = success)
    """
    return run_fakestack(args)


def main():
    """CLI entry point for fakestack command."""
    exit_code = run_fakestack()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
