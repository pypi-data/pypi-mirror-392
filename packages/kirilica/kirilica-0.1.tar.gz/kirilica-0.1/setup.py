from setuptools import setup, find_packages

def readme():
  with open('README.md', encoding="utf-8") as f:
    return f.read()

setup(
  name='kirilica',
  version='0.1',
  author='Funsy',
  author_email='abramovicegor842@gmail.com',
  description='Поддерживать кириллица дял питон',
  long_description=readme(),
  long_description_content_type='text/markdown',
  packages=find_packages(),
  keywords='кириллица',
  python_requires='>=3.11'
)