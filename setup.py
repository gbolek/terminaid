from setuptools import setup, find_packages

setup(
    name="terminaid",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "pyperclip>=1.8.0",
    ],
    entry_points={
        "console_scripts": [
            "terminaid=terminaid.cli:main",
        ],
    },
    author="gbolek",
    author_email="your.email@example.com",
    description="A CLI tool to get terminal commands from natural language queries",
    keywords="cli, terminal, commands, llm, ollama",
    python_requires=">=3.8",
)
