from setuptools import setup, find_packages
import os

# Read the README file
readme_file = os.path.join(os.path.dirname(__file__), 'README.md')
long_description = ''
if os.path.exists(readme_file):
    with open(readme_file, 'r', encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='osclient',
    version='0.1.1',
    description='OpenStack client library with simplified authentication',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Toan Nguyen',
    author_email='ntoand@gmail.com',
    url='https://github.com/ntoand/osclient',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'keystoneauth1>=4.0.0',
        'python-novaclient>=17.0.0',
        'python-keystoneclient>=4.0.0',
        'python-cinderclient>=7.0.0',
        'python-neutronclient>=7.0.0',
        'nectarallocationclient>=1.0.0',
        'python-glanceclient>=3.0.0',
        'requests>=2.25.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='openstack cloud client',
)

