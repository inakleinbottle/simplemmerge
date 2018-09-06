from setuptools import setup




setup(name='simplemmerge',
      author='inakleinbottle',
      author_email='admin@inakleinbottle.com',
      version='0.1.0',
      license='GPL-3.0',
      long_description=open('README.md').read(),
      description='Simple mail merge program that formats a template file with entries from CSV.',
      py_modules=['mmerge'],
      package_data={'' : ['*.txt', '*.ini']}
      entry_points={
        'console_scripts' : ['mmerge = mmerge:main']
      }
      )
