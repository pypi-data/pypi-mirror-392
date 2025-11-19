from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "A command-line tool to send Telegram notifications when long-running commands complete."

try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    # Fallback requirements if requirements.txt is not available during build
    requirements = [
        "requests>=2.28.0",
        "click>=8.0.0", 
        "colorama>=0.4.4"
    ]

setup(
    name="notifyme-cli",
    version="1.0.1",
    author="Jude Osby",
    description="A command-line tool to send Telegram notifications when long-running commands complete",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/judeosbert/notifyme-cli",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Communications",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "isort>=5.0",
            "mypy>=0.900",
            "pre-commit>=2.15.0",
            "build>=0.8.0",
            "twine>=4.0.0",
        ],
    },
    keywords=["telegram", "notifications", "cli", "command-line", "bot", "alerts"],
    entry_points={
        "console_scripts": [
            "notifyme=notify_me.cli:main",
        ],
    },
)