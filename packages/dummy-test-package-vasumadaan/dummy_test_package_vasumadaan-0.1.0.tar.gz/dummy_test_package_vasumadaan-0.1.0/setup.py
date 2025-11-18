from setuptools import setup, find_packages

setup(
    name="dummy-test-package-vasumadaan",
    version="0.1.0",
    author="Vasu Madaan",
    author_email="vasu@example.com",
    description="A dummy package for testing private PyPI index",
    long_description="This is a dummy package created for testing purposes with a private PyPI index.",
    long_description_content_type="text/plain",
    url="https://github.com/yourusername/dummy-package",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # Add any dependencies here if needed
    ],
)
