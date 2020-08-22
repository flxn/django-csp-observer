from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
   name='django-csp-observer',
   version='0.1',
   description='CSP observer app for Django',
   long_description=long_description,
   long_description_content_type="text/markdown",
   url="https://github.com/flxn/django-csp-observer",
   author='Felix Stein',
   author_email='mail@flxn.de',
   packages=['csp_observer'],
   python_requires='>=3.6',
   install_requires=[
        'markdown',
    ],
   classifiers=[
      "Development Status :: 1 - Planning",
      "Programming Language :: Python :: 3",
      "License :: OSI Approved :: MIT License",
      "Operating System :: OS Independent",
      "Framework :: Django :: 3.0",
    ],
)