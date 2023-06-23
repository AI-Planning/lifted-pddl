import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='lifted-pddl',
      version='1.2.2',
      description='A lightweight framework for parsing PDDL in lifted form.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/AI-Planning/lifted-pddl',
      author='Carlos Núñez Molina',
      author_email='ccaarlos@ugr.es',
      license='MIT',
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
      ],
      keywords='automated_planning PDDL parser',
      install_requires=['tarski'],
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'lifted_pddl=lifted_pddl.__main__:main'
          ],
      }
      )
