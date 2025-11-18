from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("ziyo_lang/__init__.py", "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"')
            break
    else:
        version = "1.0.1"

setup(
    name="ziyo-lang",
    version=version,
    author="Yoqubov Javohir",
    author_email="RAKUZENUZ@gmail.com",
    description="Ziyo - O'zbekcha dasturlash tili",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://t.me/UzMaxBoy",
    project_urls={
        "Bug Reports": "https://t.me/UzMaxBoy",
        "Source": "https://t.me/UzMaxBoy",
        "Documentation": "https://t.me/UzMaxBoy",
    },
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
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ziyo-run=ziyo_lang.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)