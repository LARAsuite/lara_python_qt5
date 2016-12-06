lara
====

LARA - Laboratory Automation Robotic Assistant

lara is a python application for assisting, designing and managing robotic processes, but not limited to this purpose only.

s. http://lara.uni-greifswald.de/

LARA is a free and open source (GPL) process planning and designing tool that offers you the following features:

    - Visually planning and documenting your complete robotic lab automation process
    - Hardware and device/brand independent application
    - python based: high flexibility in the choose of platforms, but lean and with very high speed
    - a simple plugin systems allows to quickly add modules to extend the functionality of the program
    - code generators for many robotics platforms realizable
    - freely available and open source


Installation of lara
____________________


LARA runs with python 2.7
Please install 
python-qt4, singledispatch and pysimplesoap :

    sudo apt-get install python-pip python-qt4
    sudo pip install singledispatch
    sudo pip install pysimplesoap

for the Raspberry SiLA device you need to install GPIO and pysimplesoap
On an Raspberry Pi console please type:

    sudo apt-get install python-pip
    sudo pip install singledispatch
    sudo pip install pysimplesoap
    sudo pip install GPIO
    
There are two ways of installing lara: plain and in a virtual python environment (virtualenv).

The recommended way to install lara is to install it in a virtualenv environment.



Virtualenv - Installation
-------------------------

First install pip_ on your system. 
It is strongly recommended to install virtualenv_ and virtualenvwrapper_ to take the most advantage of pip_.

To install pip_, go to http://www.pip-installer.org/en/latest/installing.html

To install virtualenv_, go to https://pypi.python.org/pypi/virtualenv

To install virtualenvwrapper_, go to http://virtualenvwrapper.readthedocs.org/en/latest/install.html#basic-installation


Plain installation
------------------

Configuration file
-------------------

    * please edit config file (config/lara.config) to fit to your system
    * for development, please copy config file to ~/.config/lara-suite/lara/
    * for production, please copy config file to /etc/lara-suite/lara/

Installation of required packages
---------------------------------

pip install --user requirements.py


Testing all applications
________________________

use this command to run all tests:

     ./lara.py --test
    
Acknowledgements
________________

The LARA developers thank 

    * the python team

References
__________

.. _pip: https://pypi.python.org/pypi/pip
.. _virtualenv: https://pypi.python.org/pypi/virtualenv
.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/
