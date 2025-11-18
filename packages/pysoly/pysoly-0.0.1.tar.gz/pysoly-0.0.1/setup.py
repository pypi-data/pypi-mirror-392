from setuptools import setup, find_packages

def readme():
  with open('README.md', 'r') as f:
    return f.read()

setup(
  name='pysoly',
  version='0.0.1',
  author='zxc_send',
  author_email='karimar.goscha@gmail.com',
  description="The program is designed for convenient interaction with a Windows computer display. The following methods are available: click, get_value, get_int (address), ...",
  long_description=readme(),
  long_description_content_type='text/markdown',
  packages=find_packages(),
  install_requires=['numpy>=1.25.0', 'pillow>=10.0.0', 'pymem>=1.9.0', 'pywin32>=305'],
  classifiers=[
    "Programming Language :: Python :: 3.11",
    "License :: OSI Approved :: MIT License",
    "Operating System :: Microsoft :: Windows"
  ],
  keywords='get click ',
  python_requires='>=3.6'
)