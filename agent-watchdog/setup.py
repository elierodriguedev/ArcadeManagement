from setuptools import setup, find_packages

setup(
    name='agent-watchdog',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'PyQt5>=5.15.0',
        'requests>=2.25.0',
    ],
    python_requires='>=3.8',
)