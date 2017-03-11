from distutils.core import setup

setup(
  name = 'py_d3',
  packages = ['py_d3'], # this must be the same as the name above
  install_requires=['ipython'],
  py_modules=['py_d3'],
  version = '0.2.5',
  description = 'D3 block magic for Jupyter notebook.',
  author = 'Aleksey Bilogur',
  author_email = 'aleksey@residentmar.io',
  url = 'https://github.com/ResidentMario/py_d3',
  download_url = 'https://github.com/ResidentMario/py_d3/tarball/0.2.5',
  keywords = ['data', 'data visualization', 'data analysis', 'python', 'jupyter', 'ipython', 'd3', 'javascript'],
  classifiers = []
)
