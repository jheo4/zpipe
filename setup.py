import setuptools

setuptools.setup(
    name="pyzpipe",
    version="0.1.2",
    license='MIT',
    author='Jin Heo',
    author_email='993jin@gmail.com',
    description='Concurrent and parallel pipeline framework using ZMQ',
    long_description=open('README.md').read(),
    url='https://github.com/jheo4/zpipe',
    python_requires=">=3.6",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=['numpy', 'pyzmq', ],
    extras_require={
          "pyopencv": ['opencv-python>=3.4.2', 'opencv-contrib-python>=3.4.2'],
          "vidgear": ['vidgear>=0.1.8'],
          "dev": ["flake8>=3.7.9", "black>=19.10b0", "pytest>=5.4.1"],
          },
)

