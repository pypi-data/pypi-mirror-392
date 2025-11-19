from setuptools import setup, find_packages

setup(
    name="pymartian",
    version="1.0.0",
    description="Converts Markdown to Notion Blocks and RichText",
    author="Martian Python Port",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "markdown-it-py>=3.0.0",
        "mdit-py-plugins>=0.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    package_data={
        "martian.notion": ["language_map.json"],
    },
)

