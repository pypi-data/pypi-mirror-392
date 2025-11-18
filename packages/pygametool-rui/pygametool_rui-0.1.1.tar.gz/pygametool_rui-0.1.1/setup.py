from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_desc = f.read()

setup(
    name='pygametool-rui',
    version='0.1.1',
    packages=['PygameTool'],
    package_dir={'PygameTool': '.'},
    include_package_data=True,
    install_requires=[
        'pygame',
    ],
    author='rui he',
    author_email='rhe.guge@gmail.com',
    description='Pygame项目的实用程序包',
    long_description=long_desc,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://example.com',
    python_requires='>=3.10',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
)
