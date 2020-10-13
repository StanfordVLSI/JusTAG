from setuptools import setup

setup(
    name='justag',
    version='0.0.4.2',
    description='Generating JTAG debug hardware from Markdown files.',
    url='https://github.com/StanfordVLSI/JusTAG',
    author='Stanford University',
    packages=['justag'],
    entry_points = {
        'console_scripts': [
            'justag=justag.JusTAG:main',
            'justag_dir=justag.JusTAG:jtag_directory'
        ]
    },
    install_requires=[
        'mistune',
        'pandas',
        'lxml'
    ],
    include_package_data=True,
    zip_safe=False,
)
