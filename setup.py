from setuptools import setup

# See http://pypi.python.org/pypi/stdeb for package building instructions
# or else here: https://github.com/astraw/stdeb

setup(name='azulejo',
      version='0.1',
      author='Pedro',
      author_email='pedro@lamehacks.net',
      packages=['azulejo'],
      package_data={
          'azulejo': ['*.json'],
      },
      include_package_data=True,
      scripts=['bin/azulejo'],
      install_requires=['pygobject', 'python-xlib', 'notify2'],
      )
