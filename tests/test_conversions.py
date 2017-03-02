from isaw.awib.conversions import make_master
import logging
from nose.tools import assert_equal
from os import listdir
from os.path import dirname, isfile, join, realpath
from PIL import Image


class TestMakeConversions():

    def setUp(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.data_dir = join(dirname(realpath(__file__)), 'data')
        self.file_list = [
            fn for fn in listdir(self.data_dir) if isfile(
                join(self.data_dir, fn))]
        assert_equal(len(self.file_list), 8)
        self.images = {}
        self.open_all()

    def tearDown(self):
        pass

    def open_all(self):
        for fn in self.file_list:
            self.logger.debug('filename: "{}"'.format(fn))
            im = Image.open(join(self.data_dir, fn))
            self.images[fn] = im
        assert_equal(len(self.images), 8)

    def test_make_master_from_image(self):
        make_master(self.images['cat_drawer.tif'])

    def test_make_master_from_file(self):
        make_master(join(self.data_dir, 'cat_drawer.tif'))


