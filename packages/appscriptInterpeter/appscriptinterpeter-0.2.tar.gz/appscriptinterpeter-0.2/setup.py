from setuptools import setup

setup(
    name='appscriptInterpeter',
    version='0.2',
    packages=['appscriptInterpeter'],
    entry_points={
    'console_scripts': [
        'appscript_run = appscriptInterpeter.cmd:run',
    ],
}
    )