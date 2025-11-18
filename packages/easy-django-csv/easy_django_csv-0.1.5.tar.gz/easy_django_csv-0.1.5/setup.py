from setuptools import setup, find_packages

setup(
    name="easy_django_csv",
    version="0.1.5",
    author="Alex Dickens",
    author_email="alex@calmdigital.com",
    description="Simple CSV export for Django",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/alex-dicko/Easy-Django-CSV",
    packages=find_packages(),
    install_requires=[
        "Django>=3.2",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)