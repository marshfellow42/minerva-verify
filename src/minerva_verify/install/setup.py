#!/usr/bin/env python3
import subprocess
import shutil
import platform
import sys


def run_cmd(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {command}: {e}")
        sys.exit(1)


def ubuntu_setup():
    print("Detected Ubuntu/Debian. Installing uv...")

    if shutil.which("uv"):
        print("uv already installed.")
        return

    run_cmd("sudo apt-get update")

    # uv is not always in default repos → use official installer
    run_cmd("curl -Ls https://astral.sh/uv/install.sh | sh")


def arch_setup():
    print("Detected Arch Linux. Installing uv...")

    if shutil.which("uv"):
        print("uv already installed.")
        return

    run_cmd("sudo pacman -Syu --noconfirm")
    run_cmd("sudo pacman -S --noconfirm uv")


def fedora_setup():
    print("Detected Fedora. Installing uv...")

    if shutil.which("uv"):
        print("uv already installed.")
        return

    # uv may not be in stable repos → fallback to script
    run_cmd("sudo dnf upgrade -y")
    run_cmd("curl -Ls https://astral.sh/uv/install.sh | sh")


def macos_setup():
    print("Detected macOS. Installing uv...")

    if shutil.which("uv"):
        print("uv already installed.")
        return

    if not shutil.which("brew"):
        print("Homebrew not found. Installing...")
        run_cmd('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')

    run_cmd("brew install uv")


def windows_setup():
    print("Detected Windows. Installing uv...")

    if shutil.which("uv"):
        print("uv already installed.")
        return

    run_cmd(
        'powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"'
    )


def run_os_setup():
    system = platform.system()

    if system == "Linux":
        try:
            distro = platform.freedesktop_os_release().get("ID", "").lower()
        except Exception:
            distro = ""

        match distro:
            case "ubuntu" | "debian":
                ubuntu_setup()
            case "arch":
                arch_setup()
            case "fedora":
                fedora_setup()
            case _:
                print(f"Unsupported Linux distro: {distro}")
                sys.exit(1)

    elif system == "Darwin":
        macos_setup()

    elif system == "Windows":
        windows_setup()

    else:
        print(f"Unsupported OS: {system}")
        sys.exit(1)

    # Final check
    if not shutil.which("uv"):
        print("uv installation failed or not in PATH.")
        sys.exit(1)

    print("uv installed successfully.")
    
    tool_check = subprocess.run(["uv", "tool", "list"], capture_output=True, text=True)
    if "minerva-verify" not in tool_check.stdout:
        try:
            print("Installing minerva-verify via uv...")
            subprocess.run(["uv", "tool", "install", ".", "--force"])
        except FileNotFoundError:
            print("Error: uv is not installed or not found in your PATH.")
            sys.exit(1)


if __name__ == "__main__":
    run_os_setup()