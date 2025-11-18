from setuptools import setup, find_packages

setup(
    name='campo-estatico-mdf_065',  # Nombre que usarán para instalar: pip install campo-estatico-mdf
    version='0.1.0',
    description='Solucionador 2D de la Ecuación de Laplace usando el Método de Diferencias Finitas (MDF) e iteración de Jacobi.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Sebastian Acuña y Jose Luis Zamora',
    author_email='jose20022011@hotmail.es',
    url='https://github.com/Darkenis065/LaplaceSolver', # Opcional, pero recomendado
    packages=find_packages(), # Esto encontrará automáticamente 'campo_estatico_mdf'
    install_requires=[
        'numpy>=1.20',
    ],
    license='GPLv3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', # O la licencia que elijas
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    python_requires='>=3.9',
)
