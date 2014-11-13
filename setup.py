from setuptools import setup, find_packages

setup(
		name='RecipeWatchRelated',
		version='0.0.1',
		author="Jay Hack",
		author_email="jhack@stanford.edu",
		description="Markov Chains applied to Object Clusters",
		packages=find_packages(),
		include_package_data=True,
		install_requires=[
			'numpy',
			'scipy',
			'pandas',
			'scikit-learn',
			'pymongo',
			'dill',
			
		]
)
