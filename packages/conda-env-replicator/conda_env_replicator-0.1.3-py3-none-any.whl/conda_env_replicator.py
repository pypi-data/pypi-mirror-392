#!/usr/bin/env python3
"""
Conda Environment Replicator
A tool to create portable conda environment files that work across OS/glibc updates
by removing overly-specific build strings while preserving CUDA/GPU requirements.
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml


def parse_explicit_file(explicit_path: Path) -> Dict[str, Tuple[str, str]]:
    """
    Parse conda list --explicit output to extract package channels.

    Returns: Dict mapping package_name -> (version, channel)
    """
    package_channels = {}

    with open(explicit_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("#") or line.startswith("@") or not line:
                continue

            # Example: https://conda.anaconda.org/rapidsai/linux-64/ptxcompiler-0.2.0-py39h107f55c_0.tar.bz2
            match = re.search(r"https?://[^/]+/([^/]+)/[^/]+/([^/-]+)-([^-]+)-([^.]+)\.", line)
            if match:
                channel = match.group(1)
                pkg_name = match.group(2)
                version = match.group(3)
                package_channels[pkg_name] = (version, channel)

    return package_channels


def normalize_build_string(build: str) -> str:
    """
    Normalize build strings to preserve CUDA/GPU info with wildcards.

    Examples:
        'py39h107f55c_0' -> '' (removed)
        'cuda11.2_0' -> '*cuda11*'
        'gd367332_cuda11.2_0' -> '*cuda11*'
        'gpu' -> '*gpu*'
    """
    if not build:
        return ""

    # Check for CUDA version pattern (cuda11.2, cuda11, etc.)
    cuda_match = re.search(r"cuda(\d+)(?:\.(\d+))?", build)
    if cuda_match:
        major = cuda_match.group(1)
        return f"*cuda{major}*"

    # Check for gpu keyword
    if "gpu" in build.lower():
        return "*gpu*"

    # Remove all other build strings
    return ""


def parse_yaml_env(yaml_path: Path) -> Dict:
    """Parse conda environment YAML file."""
    with open(yaml_path, "r") as f:
        return yaml.safe_load(f)


def process_dependencies(env_data: Dict, package_channels: Dict[str, Tuple[str, str]]) -> List[str]:
    """
    Process dependencies to add channels and normalize build strings.

    Returns: List of processed dependency strings
    """
    processed = []

    for dep in env_data.get("dependencies", []):
        if isinstance(dep, dict):
            # Skip pip dependencies
            processed.append(dep)
            continue

        # Parse package specification
        # Format can be: package, package=version, package=version=build
        parts = dep.split("=")
        pkg_name = parts[0].strip()

        # Remove channel prefix if present
        if "::" in pkg_name:
            pkg_name = pkg_name.split("::")[1]

        version = parts[1] if len(parts) > 1 else None
        build = parts[2] if len(parts) > 2 else None

        # Get channel from explicit list
        channel = None
        if pkg_name in package_channels:
            _, channel = package_channels[pkg_name]

        # Normalize build string
        normalized_build = normalize_build_string(build) if build else ""

        # Construct new dependency string
        if channel:
            new_dep = f"{channel}::{pkg_name}"
        else:
            new_dep = pkg_name

        if version:
            new_dep += f"={version}"

        if normalized_build:
            new_dep += f"={normalized_build}"

        processed.append(new_dep)

    return processed


def export_env_files(env_name: str) -> Tuple[Path, Path]:
    """
    Export conda environment to YAML and explicit formats.

    Returns: Tuple of (yaml_path, explicit_path)
    """
    temp_dir = Path(tempfile.gettempdir())
    yaml_path = temp_dir / f"{env_name}_export.yml"
    explicit_path = temp_dir / f"{env_name}_explicit.txt"

    # Export YAML
    print(f"Exporting environment '{env_name}' to YAML...")
    result = subprocess.run(
        ["conda", "env", "export", "-n", env_name], capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Error exporting environment: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    with open(yaml_path, "w") as f:
        f.write(result.stdout)

    # Export explicit
    print(f"Exporting environment '{env_name}' to explicit format...")
    result = subprocess.run(
        ["conda", "list", "-n", env_name, "--explicit"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Error listing packages: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    with open(explicit_path, "w") as f:
        f.write(result.stdout)

    print(f"Intermediate files created:")
    print(f"  YAML: {yaml_path}")
    print(f"  Explicit: {explicit_path}")

    return yaml_path, explicit_path


def create_portable_yaml(yaml_path: Path, explicit_path: Path, output_path: Path):
    """Create portable conda environment YAML file."""
    # Parse input files
    env_data = parse_yaml_env(yaml_path)
    package_channels = parse_explicit_file(explicit_path)

    # Process dependencies
    new_dependencies = process_dependencies(env_data, package_channels)

    # Update environment data
    env_data["dependencies"] = new_dependencies

    # Write output
    with open(output_path, "w") as f:
        yaml.dump(env_data, f, default_flow_style=False, sort_keys=False)

    print(f"\nPortable environment file created: {output_path}")
    print(f"Total packages processed: {len(new_dependencies)}")


def main():
    parser = argparse.ArgumentParser(
        description="Create portable conda environment files for OS/glibc upgrades",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process existing YAML and explicit files
  %(prog)s -y env.yml -e explicit.txt -o portable_env.yml
  
  # Export and process an existing environment
  %(prog)s -n myenv -o portable_env.yml
        """,
    )

    # File-based mode
    parser.add_argument("-y", "--yaml", type=Path, help="Input conda environment YAML file")
    parser.add_argument(
        "-e", "--explicit", type=Path, help="Input conda list --explicit output file"
    )

    # Environment-based mode
    parser.add_argument("-n", "--name", help="Name of existing conda environment to export")

    # Output
    parser.add_argument(
        "-o", "--output", type=Path, required=True, help="Output portable YAML file"
    )

    parser.add_argument(
        "--keep-intermediates",
        action="store_true",
        help="Keep intermediate export files (when using -n)",
    )

    args = parser.parse_args()

    # Validate arguments
    if args.name:
        if args.yaml or args.explicit:
            parser.error("Cannot use -n/--name with -y/--yaml or -e/--explicit")
        yaml_path, explicit_path = export_env_files(args.name)
        cleanup_intermediates = not args.keep_intermediates
    elif args.yaml and args.explicit:
        if not args.yaml.exists():
            parser.error(f"YAML file not found: {args.yaml}")
        if not args.explicit.exists():
            parser.error(f"Explicit file not found: {args.explicit}")
        yaml_path = args.yaml
        explicit_path = args.explicit
        cleanup_intermediates = False
    else:
        parser.error("Must provide either -n/--name OR both -y/--yaml and -e/--explicit")

    # Process files
    create_portable_yaml(yaml_path, explicit_path, args.output)

    # Cleanup if needed
    if cleanup_intermediates:
        yaml_path.unlink()
        explicit_path.unlink()
        print(f"\nIntermediate files cleaned up")


if __name__ == "__main__":
    main()
