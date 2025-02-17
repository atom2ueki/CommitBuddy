from setuptools import setup, find_packages

setup(
    name='commit-buddy',
    version='0.1.0',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[
        'requests>=2.31.0',
        'PyYAML>=6.0.1',
    ],
    entry_points={
        'console_scripts': [
            'commitbuddy=commit_buddy.main:main',
        ],
    },
    author="@atom2ueki",
    description="CommitBuddy - Your AI-Powered Git Commit Assistant",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/atom2ueki/commitbuddy",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Version Control :: Git',
    ],
    python_requires='>=3.6',
)
