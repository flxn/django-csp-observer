from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='django-csp-observer',
    version='1.0.2',
    description='A Django app that evaluates CSP reports to identify malicious activity.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/flxn/django-csp-observer",
    author='Felix Stein, Ivan Correa',
    author_email='mail@flxn.de',
    packages=['csp_observer'],
    python_requires='>=3.6',
    license='MIT License',
    install_requires=[
        'markdown',
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Framework :: Django :: 3.0",
        "Environment :: Web Environment",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content"
    ],
)
