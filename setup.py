from setuptools import setup

setup(
    name='commitbuddy',
    version='0.1.0',
    py_modules=['main'],
    entry_points={
        'console_scripts': [
            'commitbuddy=main:main',
        ],
    },
    author="Your Name",
    description="CommitBuddy - Your AI-Powered Git Commit Assistant",
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
)