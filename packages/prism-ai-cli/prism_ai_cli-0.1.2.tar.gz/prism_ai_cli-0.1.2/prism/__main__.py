#!/usr/bin/env python3
import sys
import os
import subprocess

IMAGE = "us-south1-docker.pkg.dev/prism-ai-file-storage/prism-ai/prism-ai:latest"
PROJECT = "prism-ai-file-storage"

def run_prism():
    """Main entry point for the prism CLI."""
    # Find credentials
    creds = os.path.expanduser("~/.config/gcloud/application_default_credentials.json")
    mac_creds = os.path.expanduser("~/Library/Application Support/gcloud/application_default_credentials.json")
    if not os.path.exists(creds) and os.path.exists(mac_creds):
        creds = mac_creds

    if not os.path.exists(creds):
        print("Error: No gcloud credentials found.")
        print("Run: gcloud auth application-default login")
        sys.exit(1)

    # Platform flag for Apple Silicon
    platform = "--platform linux/amd64" if "arm" in os.uname().machine.lower() else ""

    # Docker run command
    cmd = [
        "docker", "run", "--rm", "-i",
        platform,
        "-v", f"{creds}:/credentials.json:ro",
        "-e", "GOOGLE_APPLICATION_CREDENTIALS=/credentials.json",
        "-e", f"GOOGLE_CLOUD_PROJECT={PROJECT}",
        IMAGE
    ] + sys.argv[1:]  # Pass all args to the container

    # Run and handle output
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running prism: {e}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("Error: Docker is not installed or not in PATH.")
        print("Install Docker: https://docs.docker.com/get-docker/")
        sys.exit(1)

if __name__ == "__main__":
    run_prism()