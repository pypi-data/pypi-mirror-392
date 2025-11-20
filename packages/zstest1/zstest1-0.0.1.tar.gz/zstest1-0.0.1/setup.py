from setuptools import setup

setup(
    name="zstest1",
    version="0.0.1",
    author="Security Team",
    author_email="security@company.com",
    description="Defensive package registration to prevent supply chain attacks",
    long_description="This package was registered defensively to prevent malicious actors from squatting on this name.",
    long_description_content_type="text/plain",
    packages=["zstest1"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Security",
    ],
    python_requires=">=3.6",
)