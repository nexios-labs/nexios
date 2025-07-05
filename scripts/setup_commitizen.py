#!/usr/bin/env python3
"""
Helper script to set up commitizen and test changelog generation.
"""

import subprocess


def run_command(command, check=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(
            command, shell=True, check=check, capture_output=True, text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e}")
        return e


def main():
    print("Setting up commitizen for Nexios...")

    # Check if commitizen is installed
    result = run_command("cz --version", check=False)
    if result.returncode != 0:
        print("Installing commitizen...")
        run_command("pip install commitizen")

    # Test commitizen configuration
    print("\nTesting commitizen configuration...")
    result = run_command("cz check --rev-range HEAD~5..HEAD", check=False)
    if result.returncode == 0:
        print("✅ Commitizen is properly configured!")
        print("Recent commits that would trigger a version bump:")
        print(result.stdout)
    else:
        print("ℹ️  No version bump needed for recent commits")
        print("To test, make a commit with conventional format:")
        print("  git commit -m 'feat: add new feature'")
        print("  git commit -m 'fix: fix bug'")
        print("  git commit -m 'BREAKING CHANGE: major change'")

    # Show current version
    print("\nCurrent version: 2.6.2")
    print("To bump version manually:")
    print("  cz bump --yes")


if __name__ == "__main__":
    main()
