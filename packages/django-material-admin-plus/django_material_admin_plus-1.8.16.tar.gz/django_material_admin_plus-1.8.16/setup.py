import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name="django-material-admin-plus",
    version="1.8.16",
    license='MIT License',
    packages=find_packages(),
    author="Anton Maistrenko",
    include_package_data=True,
    author_email="it2015maistrenko@gmail.com",
    maintainer="ActRecipe Team",
    maintainer_email="actrecipe-dev@actrecipe.com",
    description="Material Design For Django Administration",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/tho-actrecipe/django-material-admin",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
