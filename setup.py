from setuptools import setup, find_packages

setup(
    name='anli',
    version='0.0.1',
    author='Bo Wen',
    author_email='wenboown@gmail.com',
    description='A package to enable natural language interfacing for applications',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/your_github/anli',
    packages=find_packages(),
    install_requires=[
        # Add here any dependencies your package needs, e.g.,
        # 'spacy>=3.0', 'transformers>=4.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        # Add additional relevant classifiers, e.g.,
        # 'Programming Language :: Python :: 3.8',
        # 'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    # Include any package data here
    package_data={'anli': ['data/*']},
)