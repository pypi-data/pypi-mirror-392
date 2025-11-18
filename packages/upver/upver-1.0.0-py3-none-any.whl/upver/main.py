#!/usr/bin/env python3

import datetime
import argparse
import os
import sys
import re


def read_file(path):
    """Reads a file and returns its content."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    """Writes content to a file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def update_pubspec(text, new_version, new_build):
    """Updates the version in the pubspec.yaml content."""
    return re.sub(
        r"^(version:\s*)(\S+)",
        rf"\g<1>{new_version}+{new_build}",
        text,
        count=1,
        flags=re.MULTILINE,
    )


def update_pbxproj(text, new_short_version, new_build_number=None):
    """Updates MARKETING_VERSION and CURRENT_PROJECT_VERSION in pbxproj content."""
    # Update all instances of MARKETING_VERSION
    text = re.sub(
        r"(MARKETING_VERSION\s*=\s*)[0-9]+\.[0-9]+\.[0-9]+(\s*;)",
        rf"\g<1>{new_short_version}\2",
        text,
    )
    # If a build number is provided, update all instances of CURRENT_PROJECT_VERSION
    if new_build_number is not None:
        text = re.sub(
            r"(CURRENT_PROJECT_VERSION\s*=\s*)\d+(\s*;)",
            rf"\g<1>{new_build_number}\2",
            text,
        )
    return text


def main():

    startTime = datetime.datetime.now()
    parser = argparse.ArgumentParser(description="Update Flutter version number")
    parser.add_argument("-n", "--new-version", help="New version Number to change to (e.g., 1.4.30)", type=str)
    parser.add_argument("-b", "--build", help="Build number (e.g., 273)", type=str)
    args = parser.parse_args()

    pubspec_path = "pubspec.yaml"
    pbxproj_path = "ios/Runner.xcodeproj/project.pbxproj"

    new_version_input: str = None
    new_buld_input: str = None

    if not os.path.isfile(pubspec_path):
        print(f"Error: '{pubspec_path}' not found.", file=sys.stderr)
        print("Please run this script from the root of your Flutter project.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(pbxproj_path):
        print(f"Error: '{pbxproj_path}' not found.", file=sys.stderr)
        print("Please run this script from the root of your Flutter project.", file=sys.stderr)
        sys.exit(1)

    pubspec_content = read_file(pubspec_path)
    match = re.search(r"^(version:\s*)(\S+)", pubspec_content, re.MULTILINE)
    if not match:
        print("Error: Could not find 'version:' in pubspec.yaml", file=sys.stderr)
        sys.exit(1)

    current_version = match.group(2)


    if args.new_version is None:
        print("Please provide a new version number")
        new_version_input = input(f"Enter the new version (current is {current_version.split('+')[0]}): ").strip()

    if args.build is None:
        print("Please provide a build number")
        new_buld_input = input(f"Enter the build number (current is {current_version.split('+')[1]}): ").strip()

    new_pubspec_content = update_pubspec(pubspec_content, new_version_input, new_buld_input)
    write_file(pubspec_path, new_pubspec_content)
    print(f"Updated {pubspec_path}")

    pbxproj_content = read_file(pbxproj_path)
    new_pbxproj_content = update_pbxproj(pbxproj_content, new_version_input, new_buld_input)
    write_file(pbxproj_path, new_pbxproj_content)
    print(f"Updated {pbxproj_path}")

    print("\nUpdate complete. Safe deployments!")


if __name__ == "__main__":
    main()
