from setuptools import setup, find_packages


setup(name='youclid',
      version='0.1',
      packages=find_packages(),
      install_requires=[],
      package_data={'frontend': ['default.css', 'template.html',
                                 'index.js', 'draw.js']},
      include_package_data=True
      )
