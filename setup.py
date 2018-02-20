from setuptools import setup, find_packages


setup(name='youclid',
      version='0.1',
      python_requires='>=3.6',
      packages=find_packages(),
      install_requires=[],
      package_data={'youclidbackend': ['data/template.html',
                                       'data/default.css',
                                       'data/draw.js',
                                       'data/index.js']},
      include_package_data=True,
      scripts=['bin/youclid']
      )
