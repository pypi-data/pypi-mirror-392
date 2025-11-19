from pathlib import Path

from setuptools import find_packages, setup

README = Path(__file__).parent / "README.md"
long_description = README.read_text(encoding="utf-8")

setup(
    name="jasmin-log-decoder",
    version="1.0.0",
    author="Paata Barabadze",
    author_email="p.barabadze@gmail.com",
    description="Decode Jasmin SMS Gateway messages from logs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pbarabadze/jasmin-log-decoder",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Communications :: Telephony",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "decode-sms=jasmin_sms_decoder.decoder:main",
        ],
    },
    keywords="jasmin sms gateway decode logs",
)
