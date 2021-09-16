# setup file to check if there are missing files in our setup.
# only use this when you don't have the packages and when
# you are missing packages listed below.
import sys
import subprocess
import pkg_resources

# check if we have these packages in virtual environment.
# if missing,  install missing packages.
required = {'numpy','pandas','pyodbc', 'csv-diff'} 
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

# implement pip as a subprocess:
subprocess.check_call([sys.executable, '-m', 'pip', 'install',*missing])
    
# note: this will throw an error if all packages are installed, which
# for future reference i might need to get back to try and fix it.            