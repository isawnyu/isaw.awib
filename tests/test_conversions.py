from io import BytesIO
from isaw.awib.conversions import MasterMaker
import logging
from nose.tools import assert_equal
from os import listdir, mkdir
from os.path import dirname, isfile, join, realpath, splitext
from PIL import Image, TiffImagePlugin
from PIL.ImageCms import getOpenProfile, getProfileName
from PIL.ImageStat import Stat
from shutil import rmtree


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
        mkdir(join(self.data_dir, 'scratch'))

    def tearDown(self):
        rmtree(join(self.data_dir, 'scratch'))

    def open_all(self):
        for fn in self.file_list:
            self.logger.debug('filename: "{}"'.format(fn))
            im = Image.open(join(self.data_dir, fn))
            self.images[fn] = im
        assert_equal(len(self.images), 8)

    def test_make_master_from_image(self):
        MasterMaker(self.images['cat_drawer.tif'])

    def test_make_master_from_file(self):
        MasterMaker(join(self.data_dir, 'cat_drawer.tif'))

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
            master = maker.master
            assert_equal(
                getProfileName(
                    getOpenProfile(
                        BytesIO(master.info['icc_profile']))).strip(),
                'sRGB v4 ICC preference perceptual intent beta')
            raw_profile = getOpenProfile(
                BytesIO(maker.master_info[TiffImagePlugin.ICCPROFILE]))
            name = getProfileName(raw_profile).strip()
            assert_equal(name, 'sRGB v4 ICC preference perceptual intent beta')

    def test_master_maker_save(self):
        for fn, im in self.images.items():
            maker = MasterMaker(im)
            master = maker.make()
            name, extension = splitext(fn)
            fn_out = '{}.tif'.format(name)
            path_out = join(self.data_dir, 'scratch', fn_out)
            maker.save(path_out)
            with Image.open(path_out) as im:
                assert_equal(im.format, 'TIFF')
                assert_equal(master.mode, im.mode)
                stat_im = Stat(im)
                stat_master = Stat(master)
                assert_equal(stat_im.extrema, stat_master.extrema)
                assert_equal(stat_im.count, stat_master.count)
                assert_equal(stat_im.sum, stat_master.sum)
                assert_equal(stat_im.mean, stat_master.mean)
                assert_equal(stat_im.median, stat_master.median)
                assert_equal(stat_im.rms, stat_master.rms)
                assert_equal(stat_im.var, stat_master.var)

