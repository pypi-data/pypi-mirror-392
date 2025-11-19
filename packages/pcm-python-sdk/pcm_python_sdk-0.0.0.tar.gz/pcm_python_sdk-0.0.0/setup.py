import os
from distutils.core import setup
setup(
  name='pcm-python-sdk',         # How you named your package folder (MyLib)
  packages=['pcm-python-sdk'],   # Chose the same as "name"
  version='0.0.0',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description='pcm-python-sdk',   # Give a short description about your library
  author='',                   # Type in your name
  author_email='',      # Type in your E-Mail
  url='',   # Provide either the link to your github or to your website
  download_url='',    # I explain this later on
  keywords=['pcm-python-sdk'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
      ],
  classifiers=[
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'Programming Language :: Python :: 3',
  ],
)