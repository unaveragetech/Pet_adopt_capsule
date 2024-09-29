"""
pipin.py: Automated Dependency Installer with Logging

This script provides an automated solution for installing Python packages listed in a 'requirements.txt' file. 
It utilizes 'pip' to install dependencies and logs both successful installations and errors into a log file.

Features:
---------
1. Automated Dependency Installation
2. Progress Logging
3. Error Handling
4. Transparency and Traceability
5. Flexibility

Usage:
------
1. Include this script in your project directory.
2. Make sure you have a 'requirements.txt' file listing the necessary Python packages.
3. Call the 'install_requirements()' function at the start of your script.

Example:
--------
from pipin import install_requirements
install_requirements()
"""

import subprocess
import os
from datetime import datetime
import shutil

def install_requirements(omit_libraries=None, disable_installation=False):
    """
    Installs Python packages listed in 'requirements.txt', with additional options:
    
    Args:
        omit_libraries (list, optional): A list of libraries to omit from installation.
        disable_installation (bool, optional): If set to True, skips the installation process.
    """
    log_file = 'install_log.txt'

    if disable_installation:
        with open(log_file, 'a') as log:
            log.write(f"===== Installation disabled by user at {datetime.now()} =====\n")
        print("Installation is disabled. Skipping the installation process.")
        return

    if shutil.which('pip') is None:
        with open(log_file, 'a') as log:
            log.write(f"===== Critical Error: 'pip' is missing! at {datetime.now()} =====\n")
        print("Error: 'pip' is not installed. Please install 'pip' to proceed.")
        return
    
    try:
        with open('requirements.txt', 'r') as req_file:
            requirements = req_file.readlines()
    except FileNotFoundError:
        with open(log_file, 'a') as log:
            log.write(f"===== Critical Error: 'requirements.txt' not found at {datetime.now()} =====\n")
        print("Error: 'requirements.txt' not found. Ensure the file exists in the project directory.")
        return
    
    if omit_libraries:
        requirements = [req for req in requirements if not any(omit in req for omit in omit_libraries)]

    with open(log_file, 'a') as log:
        log.write(f"\n\n===== Installation started at {datetime.now()} =====\n")

    try:
        if requirements:
            temp_req_file = 'temp_requirements.txt'
            with open(temp_req_file, 'w') as temp_file:
                temp_file.writelines(requirements)

            result = subprocess.run(['pip', 'install', '-r', temp_req_file], capture_output=True, text=True)
            
            with open(log_file, 'a') as log:
                log.write("===== Successful Installation =====\n")
                log.write(result.stdout)
            
            if result.returncode != 0:
                with open(log_file, 'a') as log:
                    log.write("===== Installation Errors =====\n")
                    log.write(result.stderr)
                print("Failed to install some packages. Check 'install_log.txt' for details.")
            else:
                print("All packages installed successfully.")
            
            os.remove(temp_req_file)
        else:
            print("No packages to install. All requested libraries were omitted.")

    except subprocess.CalledProcessError as e:
        with open(log_file, 'a') as log:
            log.write(f"===== Critical Error: {e} =====\n")
        print(f"Installation failed. Error: {e}")
    
    with open(log_file, 'a') as log:
        log.write(f"===== Installation ended at {datetime.now()} =====\n")
