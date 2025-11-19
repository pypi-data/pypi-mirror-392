import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mvarcs",
    version="1.0.0",
    author="OllieJC",
    author_email="mvarcs-pypi@olliejc.uk",
    description="Python package for providing the MVA Root Certificates Store",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/markcerts/mvarcs-python",
    project_urls={
        "Bug Tracker": "https://github.com/markcerts/mvarcs-python/issues",
        "MVARCS": "https://github.com/markcerts/mvarcs",
    },
    license="The Unlicense",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: The Unlicense (Unlicense)",
        "Programming Language :: Python :: 3",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords = [
        "BIMI",
        "VMC",
        "CMC",
        "Verification",
        "Trusted",
    ],
    package_dir={"mvarcs": "src"},
    package_data={"mvarcs": ["mvarcs/*.pem"]},
    packages=["mvarcs"],
    python_requires=">=3.6",
)
