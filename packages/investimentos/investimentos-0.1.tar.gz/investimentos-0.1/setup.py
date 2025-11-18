from setuptools import setup, find_packages

setup(
   name='investimentos',
   version='0.1',
   packages=find_packages(),
   install_requires=[],
   author='Vagner Lopes',
   author_email='vagner.lopes@gmail.com',
   description='Uma biblioteca para cálculos de investimentos.',
   url='https://github.com/lvvlopes/fiap',
   classifiers=[
       'Programming Language :: Python :: 3',
       'License :: OSI Approved :: MIT License',
       'Operating System :: OS Independent',
   ],
   python_requires='>=3.6',
)