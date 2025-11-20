#!/usr/bin/env python3
import sys
import os
import subprocess
import platform

IMAGE = "us-south1-docker.pkg.dev/prism-ai-file-storage/prism-ai/prism-ai:latest"
PROJECT = "prism-ai-file-storage"


def find_credentials():
    """
    Return correct ADC credentials path for Linux, macOS, or Windows.
    """
    # Linux + WSL
    linux_path = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")

    # macOS
    mac_path = os.path.expanduser("~/Library/Application Support/gcloud/application_default_credentials.json")

    # Windows
    win_path = os.path.expanduser("~\\AppData\\Roaming\\gcloud\\application_default_credentials.json")

    for path in (linux_path, mac_path, win_path):
        if os.path.exists(path):
            return path

    return None


def detect_platform_args():
    """
    Detect if we need the --platform flag.
    Only required on ARM machines (macOS M1/M2, ARM servers).
    """
    machine = platform.machine().lower()

    if "arm" in machine or "aarch64" in machine:
        return ["--platform", "linux/amd64"]

    return []


def run_prism():
    """Main entry point for the prism CLI."""

    # Detect credentials
    creds = find_credentials()
    if not creds:
        print("❌ Error: No gcloud credentials found.")
        print("Run:")
        print("  gcloud auth application-default login")
        sys.exit(1)

    # Detect platform (ARM → force linux/amd64)
    platform_args = detect_platform_args()

    # Build docker command
    cmd = [
        "docker", "run", "--rm", "-i",
        *platform_args,
        "-v", f"{creds}:/credentials.json:ro",
        "-e", "GOOGLE_APPLICATION_CREDENTIALS=/credentials.json",
        "-e", f"GOOGLE_CLOUD_PROJECT={PROJECT}",
        IMAGE,
    ] + sys.argv[1:]  # forward all CLI args

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running prism: {e}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("❌ Error: Docker is not installed or not in PATH.")
        print("Install Docker: https://docs.docker.com/get-docker/")
        sys.exit(1)


if __name__ == "__main__":
    run_prism()
