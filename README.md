# isaw.awib: Tools for managing images at ISAW

"isaw" = Institute for the Study of the Ancient World

"awib" = Ancient World Image Bank

## Installation

### Requirements and Setup

```isaw.awib``` has been developed and tested only on OSX 10.11.

#### Languages and Runtime Environments:

(h) indicates items installed with [Homebrew](https://brew.sh/)
(p) indicates items installed with pip

 - [Exiftool](http://www.sno.phy.queensu.ca/~phil/exiftool/) 10.40 or later (h)
 - Java(TM) SE Runtime Environment 1.5 or later
 - OSX 10.11.6
 - Python 3.6.0 (h; a virtual environment is **highly** recommended)

#### Programs:

 - [Jhove](http://jhove.openpreservation.org/) 1.14.6

#### Python Packages:

 - Nose 1.3.7 (p; to run tests)
 - Pillow 4.0.0 (p, but NB [Pillow prerequisites](https://pillow.readthedocs.io/en/4.0.x/installation.html#building-on-macos), which can be installed with h)
 - Pip 9.0.1 (h; installs with Python 3.6.0)

See also ```setup.py['install_requires']```.

#### Environment variables

 - set ```PYTHONPATH``` to point to the ```isaw.awib``` directory
 - set ```JHOVEHOME``` to point to the directory where jhove is installed

## Scripts

All scripts are found in the ```/scripts``` directory. 

## accession.sh

A bash script to accession an original image. It performs the following actions:

 - Create a destination folder with specified name
 - Copy the original image to the destination folder and rename "original" (verify that copy was successful)
 - Use ```make_master.py``` q.v. to create a master tiff version of the original
 - Use exiftool to extract metadata from the original and master and save to XML files
 - Use jhove to save format identification data for the original and master to XML files
 - Use GNU sha512sum to generate and store checksums for each file 


```
$ scripts/accession.sh path/to/image/file path/to/destination/directory
``` 

## make_master.py

Make a master image for an existing original.

```
$ python scripts/make_master.py -h
usage: make_master.py [-h] [-l LOGLEVEL] [-v] [-w] [-x] [-q]
                      original destination

Make a master image for an existing original

positional arguments:
  original              path to original image file
  destination           path to destination

optional arguments:
  -h, --help            show this help message and exit
  -l LOGLEVEL, --loglevel LOGLEVEL
                        desired logging level (case-insensitive string: DEBUG,
                        INFO, WARNING, or ERROR (default: NOTSET)
  -v, --verbose         verbose output (logging level == INFO) (default:
                        False)
  -w, --veryverbose     very verbose output (logging level == DEBUG) (default:
                        False)
  -x, --overwrite       overwite existing destination file (default: False)
  -q, --quiet           suppress all messages to stdout (default: False)
```

## Tests

To make sure everything is working, run the tests:

```
$ nosetests
.......
----------------------------------------------------------------------
Ran 7 tests in 2.006s

OK
```

To see how things work inside, inspecting the tests might be helpful. You can find them in ```isaw/awib/tests```. 



