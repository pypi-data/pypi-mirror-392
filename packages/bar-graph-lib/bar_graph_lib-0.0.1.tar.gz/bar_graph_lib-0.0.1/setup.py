from setuptools import setup, find_packages

setup(
    name='bar_graph_lib',
    version='0.0.1',
    description='This is a simple Python package for creating bar graph.',
    long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
    long_description_content_type='text/markdown',
    url='',
    author='Hemanth kumar',
    author_email='x22183744@student.ncirl.ie',
    license='MIT',
    classifiers=[
        'Intended Audience :: Education',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Programming Language :: Python :: 3'
    ],
    keywords='bar_graph_lib',
    packages=find_packages(),
    python_requires=">=3.6",
    license_files=()       # ← ADD THIS LINE
)
