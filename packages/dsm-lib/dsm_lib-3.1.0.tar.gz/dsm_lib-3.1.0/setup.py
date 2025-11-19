from setuptools import setup, find_packages

with open("/home/inact1ve/hse_lab/eco/digital_ecomonitoring/test_suite/dsm_folder/requirements.txt") as f:
    required = f.read().splitlines()

setup(
    name="dsm_lib",
    version="3.1.0",
    packages=find_packages(),
    install_requires=required,
    author="Igor Chernitsin",
    description="DSM library for a forecast air pollution"
)