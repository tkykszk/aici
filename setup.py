# setup.py
from setuptools import setup, find_packages

setup(
    name="aicli",
    version="0.0.1",
    packages=find_packages(),
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
            'aicli=aicli.main:main',
        ],        
    },
)
