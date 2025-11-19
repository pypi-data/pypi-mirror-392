from setuptools import setup, find_packages

setup(
    name="POP-guotai",  # Package name

# =============================
# DEPRECATION NOTICE
# =============================
# This package is deprecated and will no longer be maintained.
# Please use the new package name: pypop
# =============================
    version="0.3.3",  # Final version before deprecation
    author="Guotai Shen",
    author_email="sgt1796@gmail.com",  
    description="[DEPRECATED] Reusable, mutable, prompt functions for LLMs. Please migrate to the new package: pypop.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/sgt1796/POP",  
    packages=find_packages(),
    include_package_data=True,  # Include non-Python files
    package_data={
        "POP": ["prompts/*.md"],  # Include all markdown files in the prompts directory
    },
    install_requires=[
        "openai>=1.0.0",
        "requests>=2.25.0",
        "python-dotenv",
        "pydantic>=1.10",
        "transformers>=4.30.0",
        "numpy>=1.21",
        "backoff",
        "Pillow>=9.0",
        "google-genai>=0.2.0",  # For Gemini support
    ],
    classifiers=[
        "Development Status :: 7 - Inactive",  # Mark as deprecated
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
