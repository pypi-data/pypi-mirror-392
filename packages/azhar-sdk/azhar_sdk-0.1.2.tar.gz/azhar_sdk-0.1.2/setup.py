from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="azhar_sdk",
    version="0.1.2",
    author="Quantum Hardware Team",
    author_email="quantum.team@example.com",
    description="SDK for Quantum Computing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/engineering_box_sdk",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        # Add your dependencies here
        # 'numpy>=1.19.0',
    ],
    entry_points={
        'console_scripts': [
            'engbox=engineering_box_sdk.main:main',
        ],
    },
)