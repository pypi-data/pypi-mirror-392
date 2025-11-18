import re
from setuptools import setup, find_packages


def readme():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()
    
def get_version():
    filepath = 'STLFLib/__init__.py'
    with open(filepath, 'r', encoding='utf-8') as f:
        version_match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]", f.read(), re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError(f"Unable to find __version__ string in {filepath}.")

setup(
    name='stlflib',
    version=get_version(),
    author='caapel',
    author_email='caapel@mail.ru',
    description='Short-Term Forecasting of Regional Electrical Load Based on CatBoost Model',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/caapel/ForecastPowerEnergy',
    packages=find_packages(),
    install_requires=['ephem',
                      'requests',
                      'beautifulsoup4', 
                      'tqdm',
                      'numpy',
                      'pandas',
                      'seaborn',
                      'matplotlib',
                      'catboost',
                      'graphviz',
                      'scikit-learn'
                      ],
    classifiers=[
                'Programming Language :: Python :: 3.10',
                'License :: Other/Proprietary License',
                'Operating System :: OS Independent'
                ],
    license='KSPEU License',
    keywords='STLF',
    project_urls={
                'GitHub': 'https://github.com/caapel/ForecastPowerEnergy'
                },
    python_requires='>=3.10'
    )