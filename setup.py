'''
The setup.py file is an essential part of packaging and
distributing Python projects. It is used by setuptools
(or disutils in older Python versions) to define the configuration
of your project, such as its metadata, dependencies and more.
'''
from setuptools import find_packages,setup ## find_packages is going to scan through all the folders and wherever there is an __init__.py file it is going to consider that particular folder as a package.
## The parent folder networksecurity will become a package and inside this parent folder there are multiple folders they will also become package.
from typing import List

def get_requirements()->List[str]:
    """
    This function will return list of requirements
    """
    requirement_lst:List[str]=[]
    try:
        with open('requirements.txt','r') as file:
            # Read lines from the file
            lines = file.readlines()
            ## Process each line
            for line in lines:
                requirement = line.strip()
                ## ignore empty lines and -e.
                if requirement and requirement!= '-e.':
                    ## -e. should not be considered in requirements.txt ,remaining all the packages needs to be installed
                    ## we are ignoring -e. and empty lines
                    requirement_lst.append(requirement) ## Appending all the requirements in the requirement list.
    except FileNotFoundError: ## If u are not getting any files its FileNotFoundError
        print("requirements.txt file not found")

    return requirement_lst

## In the above function we are reading the requirements.txt file and returning the requirements list.
print(get_requirements())    ## Run in terminal using python setup.py ----> It will display the list of packages.
## Our main aim here is to setup the metadata

setup(
    name="NetworkSecurity",
    version="0.0.1",
    author="Amritanshu Bhardwaj",
    author_email="amritanshubhardwaj12crosary@gmail.com",
    packages=find_packages(), ## This find_packages() will be responsible for searching all the packages
    install_requires=get_requirements()
)

## In terminal pip install -r requirements.txt
# -e . ---> This will refer to this setup.py file and when it goes to the setup.py file then it is going to execute this entire code
# where it is going to setup the entire python project as a package. It is also going to do one more thing in this requirement_lst it is not going to consider -e .
## that basically means that this -e . is nothing but its just referring to the setup.py file.


## NetworkSecurity naam ka ek folder create hoga this is basically my package which has got created. After the command: pip install -r requirements.txt
# There in the folder u will have PKG_INFO which will contain the above info which u have passed(in the setup).