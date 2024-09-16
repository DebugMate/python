from setuptools import setup, find_packages

setup(
    name='debugmate',
    version='0.1.5',
    packages=find_packages(include=['debugmate', 'debugmate.*']),
    install_requires=[
        'django',
        'requests',
    ],
)
