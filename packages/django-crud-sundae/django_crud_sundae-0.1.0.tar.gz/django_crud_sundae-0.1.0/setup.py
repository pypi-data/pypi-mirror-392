"""
Setup configuration for django-crud-sundae
"""

from setuptools import setup, find_packages
import os


def read_file(filename):
    """Read a file and return its contents."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


setup(
    name='django-crud-sundae',
    version='0.1.0',
    description='A useful view class for creating CRUD views in Django (With Tailwind & HTMX)',
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    author='Leon Harris',
    author_email='',  # Add your email if desired
    url='https://github.com/leonh/django-crud-sundae',
    license='MIT',
    packages=find_packages(exclude=['examples', 'examples.*', 'tests', 'tests.*']),
    include_package_data=True,  # This will include files specified in MANIFEST.in
    python_requires='>=3.8',
    install_requires=[
        'Django>=3.2',
        'django-filter>=2.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    keywords='django crud views htmx tailwind',
    project_urls={
        'Source': 'https://github.com/leonh/django-crud-sundae',
        'Tracker': 'https://github.com/leonh/django-crud-sundae/issues',
    },
)
