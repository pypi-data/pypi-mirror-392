from setuptools import setup, find_packages

setup(
    name='ncuhep',
    version='0.1.78',
    author='Kah Seng Phay',
    author_email='phay_ks@icloud.com',
    description='A Python project for NCU High Energy Physics.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/ncuhep',
    packages=find_packages(),
    license='MIT',  # Add this line
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
    install_requires=[
        'opencv-python',
        'numpy',
        "scipy",
        "iminuit",
        "matplotlib",
        "tqdm",
        "numba",
        "pandas",
    ],
)