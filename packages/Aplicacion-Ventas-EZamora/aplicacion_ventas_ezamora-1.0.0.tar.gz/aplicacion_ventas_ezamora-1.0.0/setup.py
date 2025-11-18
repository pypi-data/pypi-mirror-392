from setuptools import setup, find_packages
setup(      
    name="Aplicacion_Ventas_EZamora",
    version="1.0.0",
    author ="Erick Zamora",
    author_email="ErZamo@gmail.com",
    description='Aplicacion de ventas con manejo de impuestos y descuentos',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/ErZamo/gestor/Aplicacion_Ventas',
    packages= find_packages(),
    install_requires=[],                           # Agrega las dependencias necesarias aquí,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        
    ],
    python_requires='>=3.7'
)

# https://pypi.org/account/register/

# Para crear los archivos de distribución:
# python setup.py sdist bdist_wheel
