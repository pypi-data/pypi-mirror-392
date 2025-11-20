from setuptools import setup
from statbtrfs import version

setup(
    name='statbtrfs',
    version=version,
    description='Query Btrfs filesystem status',
    long_description=open('README.txt').read(),
    long_description_content_type='text/plain',
    author='Yufei Pan',
    author_email='pan@zopyr.us',
    url='https://github.com/yufei-pan/statbtrfs',
    py_modules=['statbtrfs'],
    entry_points={
        'console_scripts': [
            'statbtrfs=statbtrfs:main',
        ],
    },
    install_requires=[
        'prettytable',
		'multiCMD',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.6',
	license='GPLv3+',
)
