from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-admin-trap",
    version="1.1.0",
    author="Jamil Ahmed",
    author_email="contact@jamilcodes.com",
    description="A completely fake Django admin login page - perfect honeypot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jamil-codes/django-admin-trap",
    packages=find_packages(),
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=[
        "Django>=3.2",
    ],
    include_package_data=True,
    keywords="django admin security honeypot trap fake login",
)
