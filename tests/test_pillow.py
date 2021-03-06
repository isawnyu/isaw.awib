from io import BytesIO
import logging
from nose.tools import assert_equal, assert_in, assert_not_in
from os import listdir
from os.path import dirname, isfile, join, realpath, splitext
from PIL import Image
from PIL.ImageCms import getOpenProfile, getProfileName


FORMATS = {
    'jpf': 'JPEG2000',
    'jpg': 'JPEG',
    'png': 'PNG',
    'tif': 'TIFF',
    'bmp': 'BMP',
    'gif': 'GIF'
}
WIDTH = 1024
HEIGHT = 721
HAS_PROFILE = [
    'jpg',
    'png',
    'tif'
]
ALT_PROFILE = {
    'cat_drawer_adobe.tif': 'Adobe RGB (1998)'
}


class TestPillow:

    def setUp(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.data_dir = join(dirname(realpath(__file__)), 'data')
        self.file_list = [
            fn for fn in listdir(self.data_dir) if isfile(
                join(self.data_dir, fn))]
        self.images = {}
        self.open_all()

    def tearDown(self):
        pass

    def open_all(self):
        for fn in self.file_list:
            self.logger.debug('filename: "{}"'.format(fn))
            im = Image.open(join(self.data_dir, fn))
            self.images[fn] = im

    def test_format(self):
        for fn, im in self.images.items():
            self.logger.debug('{} is {}'.format(fn, im.format))
            name, extension = splitext(fn)
            assert_equal(im.format, FORMATS[extension[1:]])

    def test_mode(self):
        for fn, im in self.images.items():
            self.logger.debug(
                '{} mode is "{}" ({})'.format(fn, im.mode, type(im.mode)))
            if 'posterized' in fn:
                assert_equal(im.mode, 'P')  # 8-bit pixels, indexed
            else:
                assert_equal(im.mode, 'RGB')

    def test_profiles(self):
        for fn, im in self.images.items():
            self.logger.debug(
                '{} info includes "{}"'.format(fn, im.info.keys()))
            name, extension = splitext(fn)
            if extension[1:] in HAS_PROFILE:
                assert_in('icc_profile', im.info.keys())
                profile = getOpenProfile(BytesIO(im.info['icc_profile']))
                try:
                    expected_profile = ALT_PROFILE[fn]
                except KeyError:
                    expected_profile = (
                        'IEC 61966-2.1 Default RGB colour space - sRGB')
                assert_equal(
                    getProfileName(profile).strip(),
                    expected_profile)
            else:
                assert_not_in('icc_profile', im.info.keys())
