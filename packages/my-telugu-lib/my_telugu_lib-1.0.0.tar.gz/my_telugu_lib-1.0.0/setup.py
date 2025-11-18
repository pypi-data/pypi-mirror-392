from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="my_telugu_lib",
    version="1.0.0",
    description="Complete Telugu Translation & Transliteration Package with Built-in Typing Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/my_telugu_lib",
    packages=find_packages(),
    install_requires=[
        "googletrans==4.0.0rc1",
        "deep-translator",
        "indic-transliteration",
    ],
    entry_points={
        'console_scripts': [
            'telugu-typing=my_telugu_lib.typing_tool:start_typing_tool',
            'telugu-interactive=my_telugu_lib.typing_tool:interactive_typing',
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Localization",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="telugu translation transliteration indic language typing-tool",
)
