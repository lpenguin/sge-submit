from setuptools import setup

setup(name='sgeparallel',
      version='0.1',
      license='MIT',
      packages=['sgeparallel', 'sgeparallel.cli'],
      zip_safe=False,
      entry_points={
          'console_scripts': [
                'sge-submit=sgeparallel.cli.sge_submit:main',
          ]
      },
      requires=[
          'drmaa',
          'tailer',
      ]
)