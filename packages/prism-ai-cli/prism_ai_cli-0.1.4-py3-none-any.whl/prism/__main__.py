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


def is_docker_authenticated():
    config = os.path.expanduser("~/.docker/config.json")
    if not os.path.exists(config):
        return False

    try:
        import json
        with open(config, "r") as f:
            data = json.load(f)
            cred_helpers = data.get("credHelpers", {})
            return "us-south1-docker.pkg.dev" in cred_helpers
    except Exception:
        return False


def ensure_docker_auth():
    if is_docker_authenticated():
        return True

    print("⚠️  Docker is NOT authenticated to Google Artifact Registry.")
    print("    This is required to pull the Prism AI image.")
    print("")
    print("Run this command:")
    print("   gcloud auth configure-docker us-south1-docker.pkg.dev")
    print("")

    # Ask if we should run it
    choice = input("Do you want me to run this for you? (y/N): ").strip().lower()

    if choice == "y":
        try:
            subprocess.run(
                ["gcloud", "auth", "configure-docker", "us-south1-docker.pkg.dev"],
                check=True
            )
            print(" Docker is now authenticated.")
            return True
        except Exception as e:
            print(f" Failed to authenticate Docker: {e}")
            return False

    return False

def run_prism():
    """Main entry point for the prism CLI."""
    
    if not ensure_docker_auth():
        sys.exit(1)
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
