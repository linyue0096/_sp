"""SimpleLang 編譯器安裝配置"""

from setuptools import setup, find_packages

setup(
    name="simple-lang",
    version="1.0.0",
    description="SimpleLang Compiler - 支持多种目标代码生成",
    author="SimpleLang Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        'console_scripts': [
            'simple-lang=simple_lang.compiler:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)