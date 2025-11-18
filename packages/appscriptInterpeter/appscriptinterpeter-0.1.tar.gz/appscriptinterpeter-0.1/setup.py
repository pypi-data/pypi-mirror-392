from setuptools import setup

setup(
    name='appscriptInterpeter',
    version='0.1',
    packages=['appscriptInterpeter'],
    entry_points={
    'console_scripts': [
        'appscript_run = appscriptInterpeter.tools.cmd:run',
    ],
}
    )