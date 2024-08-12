# setup.py
from setuptools import setup, find_packages
# Import the version
from aici.version import __version__

setup(
    name="aici",
    version=__version__,
    packages=find_packages(),
    description="A command line interface for ChatGPT",
    long_description=open('README.md').read(),    
    long_description_content_type='text/markdown',    
    url="https://github.com/tkykszk/aici/",
    license="MIT",
    include_package_data=True,
    install_requires=[
        # プロジェクトの依存関係をここに記述
        # 例: 'requests', 'numpy'
        'python-dotenv',
        'openai>1.40.1',
        'pytest',
    ],
    entry_points={
        'console_scripts': [
            'aici=aici.main:main',
        ],        
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',  # Python version
)
