from setuptools import setup, find_packages

setup(
        name='grax',
        version='0.1.0',
        description='GRAX transforms geospatial shapefiles into machine-learning-ready graph networks—automating the conversion from raw GIS data to topologically accurate NetworkX graphs for GNNs, CNA, and digital twin applications.',
        long_description=open('README.md').read(),
        long_description_content_type='text/markdown',
        author='Dr. Ahmed Moussa',
        author_email='ahmedyosrihamdy@gmail.com',
        url='https://github.com/real-ahmed-moussa/grax',
        license='MIT',
        packages=find_packages(),
        install_requires=[
                            'numpy',
                            'fiona',
                            'networkx',
                            'shapely',
                        ],
        classifiers=[
                        'Programming Language :: Python :: 3',
                        'License :: OSI Approved :: MIT License',
                        'Operating System :: OS Independent',
                        'Topic :: Scientific/Engineering :: Artificial Intelligence',
                    ],
        python_requires='>=3.7',
)
