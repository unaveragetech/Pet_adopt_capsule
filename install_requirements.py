"""
pipin.py: Automated Dependency Installer with Logging

This script provides an automated solution for installing Python packages listed in a 'requirements.txt' file. 
It utilizes 'pip' to install dependencies and logs both successful installations and errors into a log file, 
allowing for transparent and reliable management of project dependencies.

Features:
---------
1. Automated Dependency Installation:
   - Reads the 'requirements.txt' file and installs packages using 'pip'.
   - Ideal for ensuring all required dependencies are present without manual installation.

2. Progress Logging:
   - Logs the installation process in detail, creating a file called 'install_log.txt'.
   - The log file includes:
     - A start and end timestamp for the installation.
     - A section for successfully installed packages.
     - A section for errors encountered during installation.
   
3. Error Handling:
   - Captures and logs both package-specific errors (e.g., version conflicts or missing packages) 
     and critical errors (e.g., subprocess failures).
   - The script continues execution even after an error, ensuring all events are logged.

4. Transparency and Traceability:
   - The generated log file allows developers to trace exactly which packages were installed successfully 
     and which caused issues. This is particularly useful in production environments where package 
     installation issues must be diagnosed quickly.

5. Flexibility:
   - The function is designed to be easily integrated into any Python script, making it a convenient tool 
     for automating dependency management in various project environments.

Why use this script in production?
-----------------------------------
1. Automated Dependency Management:
   - Streamlines the installation of required packages, minimizing human error and ensuring a consistent environment setup.
   
2. Error Logging and Diagnostics:
   - Captures errors encountered during installation and logs them for easy review, allowing for faster 
     troubleshooting in production environments.

3. Transparency and Accountability:
   - Creates a log file ('install_log.txt') with a clear audit trail of installed packages and errors, 
     ensuring full transparency for package management.

4. Efficient Team Collaboration:
   - Ensures all team members are installing the same set of dependencies, preventing discrepancies 
     caused by missing or incompatible packages.

5. CI/CD Integration:
   - Can be used in continuous integration/continuous deployment (CI/CD) pipelines to automate 
     dependency installation and ensure consistency across environments.

Usage:
------
1. Include this script in your project directory.
2. Make sure you have a 'requirements.txt' file listing the necessary Python packages.
3. Call the 'install_requirements()' function at the start of your script to automatically install dependencies.

Example:
--------
    from pipin import install_requirements
    install_requirements()

    # Continue with the rest of your script here...

Log File Example:
-----------------
The 'install_log.txt' file will look like this:

===== Installation started at 2024-09-22 14:00:00 =====

===== Successful Installation =====
Successfully installed package1
Successfully installed package2

===== Installation Errors =====
Error installing package3: version conflict

===== Installation ended at 2024-09-22 14:03:00 =====

Conclusion:
-----------
By using this script, you ensure that all required dependencies for your project are installed consistently and reliably, with full logging for troubleshooting any issues. This makes the script ideal for production environments where automation, stability, and transparency are key.

"""

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import subprocess
import os
from datetime import datetime
import shutil

def install_requirements(omit_libraries=None, disable_installation=False):
    """
    Installs Python packages listed in 'requirements.txt', with additional options:
    
    - Omits specified libraries if needed.
    - Handles cases where 'pip' is not installed.
    - Optionally disable installation via a function argument.
    
    Args:
        omit_libraries (list, optional): A list of libraries to omit from installation.
        disable_installation (bool, optional): If set to True, skips the installation process.
    """
    log_file = 'install_log.txt'

    # If disable_installation is set to True, skip the entire installation process
    if disable_installation:
        with open(log_file, 'a') as log:
            log.write(f"===== Installation disabled by user at {datetime.now()} =====\n")
        print("Installation is disabled. Skipping the installation process.")
        return

    # Check if pip is installed
    if shutil.which('pip') is None:
        with open(log_file, 'a') as log:
            log.write(f"===== Critical Error: 'pip' is missing! at {datetime.now()} =====\n")
        print("Error: 'pip' is not installed. Please install 'pip' to proceed.")
        return
    
    # Read the requirements.txt file
    try:
        with open('requirements.txt', 'r') as req_file:
            requirements = req_file.readlines()
    except FileNotFoundError:
        with open(log_file, 'a') as log:
            log.write(f"===== Critical Error: 'requirements.txt' not found at {datetime.now()} =====\n")
        print("Error: 'requirements.txt' not found. Ensure the file exists in the project directory.")
        return
    
    # Filter out any libraries the user wants to omit
    if omit_libraries:
        requirements = [req for req in requirements if not any(omit in req for omit in omit_libraries)]

    with open(log_file, 'a') as log:
        log.write(f"\n\n===== Installation started at {datetime.now()} =====\n")

    try:
        # Install the filtered list of requirements
        if requirements:
            # Create a temporary requirements file excluding omitted libraries
            temp_req_file = 'temp_requirements.txt'
            with open(temp_req_file, 'w') as temp_file:
                temp_file.writelines(requirements)

            # Install packages from the temporary requirements file
            result = subprocess.run(['pip', 'install', '-r', temp_req_file], capture_output=True, text=True)
            
            # Log success messages
            with open(log_file, 'a') as log:
                log.write("===== Successful Installation =====\n")
                log.write(result.stdout)
            
            # Check for errors
            if result.returncode != 0:
                with open(log_file, 'a') as log:
                    log.write("===== Installation Errors =====\n")
                    log.write(result.stderr)
                print("Failed to install some packages. Check 'install_log.txt' for details.")
            else:
                print("All packages installed successfully.")
            
            # Clean up the temporary requirements file
            os.remove(temp_req_file)
        else:
            print("No packages to install. All requested libraries were omitted.")

    except subprocess.CalledProcessError as e:
        # Log critical errors (if subprocess itself fails)
        with open(log_file, 'a') as log:
            log.write(f"===== Critical Error: {e} =====\n")
        print(f"Installation failed. Error: {e}")
    
    # Finalizing log
    with open(log_file, 'a') as log:
        log.write(f"===== Installation ended at {datetime.now()} =====\n")


#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
