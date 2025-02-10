from setuptools import setup

setup(
    name='commitbuddy',
    version='1.0.0',
    py_modules=['main'],
    entry_points={
        'console_scripts': [
            'commitbuddy=main:main',
        ],
    },
    install_requires=[
        'requests>=2.25.0',
        'PyYAML>=5.1',
    ],
    author="@atom2ueki",
    description="CommitBuddy - Your AI-Powered Git Commit Assistant",
    long_description="""
    CommitBuddy is an AI-powered Git commit message generator that uses Ollama
    to create conventional commit messages based on your staged changes.
    """,
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
