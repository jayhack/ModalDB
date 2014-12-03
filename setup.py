from setuptools import setup, find_packages

setup(
		name='ModalDB',
		version='0.1',
		author="Jay Hack",
		author_email="jhack@stanford.edu",
		description="Database for working efficiently with data of multiple modalities",
		packages=find_packages(),
		include_package_data=True,
		install_requires=[
			'numpy',
			'scipy',
			'pandas',
			'matplotlib',
			'pymongo',
			'click',
			'nose',
			'scikit-learn',
			'dill'
		]
)
