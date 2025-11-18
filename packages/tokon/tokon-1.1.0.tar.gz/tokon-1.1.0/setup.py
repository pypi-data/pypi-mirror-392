from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tokon",
    version="1.1.0",
    author="Tokon Format Contributors",
    description="Token-Optimized Serialization Format for AI-Native Applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LavSarkari/tokon",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
          entry_points={
              "console_scripts": [
                  "tokon=tokon.cli:main",
              ],
          },
    include_package_data=True,
    zip_safe=False,
)

