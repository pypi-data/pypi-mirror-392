
from setuptools import setup, find_packages

setup(
    name='dabft',
    version='1.0.0',
    author='Jonathan David Harrison Miller.',
    description='DABFT - Dredd: Patent-Pending Anti-Hallucination CLI',
    packages=['dabft'],
    install_requires=['anthropic', 'groq', 'colorama', 'python-dotenv', 'yfinance', 'ccxt', 'plyer'],
    entry_points={'console_scripts': ['abe=dabft.main:main']},
    license='MIT with Patent Notice'
)
