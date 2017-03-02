from io import BytesIO
from isaw.awib.conversions import MasterMaker
import logging
from nose.tools import assert_equal
from os import listdir
from os.path import dirname, isfile, join, realpath
from PIL import Image
from PIL.ImageCms import getOpenProfile, getProfileName


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
        maker = MasterMaker(self.images['cat_drawer.tif'])

    def test_make_master_from_file(self):
        maker = MasterMaker(join(self.data_dir, 'cat_drawer.tif'))

    def test_master_maker_modes(self):
        for fn, im in self.images.items():
            maker = MasterMaker(im)
            maker.make()
            rgb = maker.rgb
            assert_equal(rgb.mode, 'RGB')

    def test_master_maker_icc(self):
        for fn, im in self.images.items():
            maker = MasterMaker(im)
            maker.make()
            srgb4 = maker.srgb4
            assert_equal(
                getProfileName(
                    getOpenProfile(
                        BytesIO(srgb4.info['icc_profile']))).strip(),
                'sRGB v4 ICC preference perceptual intent beta')

