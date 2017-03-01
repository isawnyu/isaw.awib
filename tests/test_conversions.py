
from isaw.awib.conversions import make_master
import logging
from os import listdir
from os.path import dirname, isfile, join, realpath
from PIL import Image


def test_pillow_formats():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    data_dir = join(dirname(realpath(__file__)), 'data')
    file_list = [fn for fn in listdir(data_dir) if isfile(join(data_dir, fn))]
    logger.debug('len(file_list): {}'.format(len(file_list)))
    for fn in file_list:
        logger.debug('filename: "{}"'.format(fn))
        im = Image.open(join(data_dir, fn))

