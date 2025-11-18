from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent

try:
    README = (HERE / "README.md").read_text()
except FileNotFoundError:
    README = "Python Password Manager"

setup(
    name='2025_assignment2_vaultPasswordManager',
    version='1.0.1',  
    description='Python Password Manager',
    long_description=README,
    long_description_content_type='text/markdown', 
    author='EmacsSoftwares',
    author_email='matteo.broglio3@gmail.com',
    url='https://gitlab.com/mbroglio/2025_assignment2_vaultPasswordManager',
    license='MIT',

    package_dir={'': 'src'},
    packages=find_packages(where='src'),

    install_requires=[
        'pycryptodome==3.20.0',
        'pyperclip',
        'tabulate',
        'passwordgenerator',
        'SQLAlchemy==1.4.41',
        'sqlcipher3==0.5.4'
    ],
    entry_points={
        'console_scripts': [
            'vault = vault.vault:main',
        ],
    },
    classifiers=[
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
    ],
)