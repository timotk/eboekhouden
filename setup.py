from setuptools import setup



def requirements():
    with open('requirements.txt') as f:
        return f.read()


setup(name='eboekhouden',
      version='0.2.0',
      description='eboekhouden.nl from the command line',
      author='Timo',
      license='MIT',
      install_requires=requirements(),
      entry_points={'console_scripts': ['ebh=eboekhouden.cli:cli']},
      packages=['eboekhouden'])
