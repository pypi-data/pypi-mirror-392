from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-toon-rest",
    version="0.1.3",
    author="Sebastian Martin Artaza Saade",
    author_email="martin.artaza@gmail.com",
    description="Django REST Framework renderer for TOON format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/martinartaza/django-toon-rest",
    project_urls={
        "Homepage": "https://github.com/martinartaza/django-toon-rest",
        "Author": "https://www.sebastianartaza.com",
        "Issue Tracker": "https://github.com/martinartaza/django-toon-rest/issues",
    },
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
    ],
    python_requires=">=3.8",
    install_requires=[
        "djangorestframework>=3.0.0",
        "json-toon>=1.0.0",
    ],
)

