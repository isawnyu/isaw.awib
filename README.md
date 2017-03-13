# isaw.awib: Tools for managing images at ISAW

"isaw" = Institute for the Study of the Ancient World

"awib" = Ancient World Image Bank

## Installation

### Requirements

See also ```setup.py['install_requires']```.

 - Python 3.6.0
 - Pillow 4.0.0 
 - Nose 1.3.7 (to run tests)

## Scripts

All scripts are found in the ```/scripts``` directory. 

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



