from io import BytesIO
from isaw.awib.conversions import MasterMaker
import logging
from nose.tools import assert_equal
from os import listdir, mkdir
from os.path import abspath, dirname, isfile, join, realpath, splitext
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
        self.file_list = [f for f in self.file_list if f != '.DS_Store']
        assert_equal(len(self.file_list), 9)
        self.images = {}
        self.open_all()
        try:
            mkdir(join(self.data_dir, 'scratch'))
        except FileExistsError:
            pass

    def tearDown(self):
        rmtree(join(self.data_dir, 'scratch'))

    def open_all(self):
        for fn in self.file_list:
            self.logger.debug('filename: "{}"'.format(fn))
            im = Image.open(join(self.data_dir, fn))
            self.images[fn] = im
        assert_equal(len(self.images), 9)

    def test_make_master_from_image(self):
        MasterMaker(self.images['cat_drawer.tif'])

    def test_make_master_from_file(self):
        MasterMaker(join(self.data_dir, 'cat_drawer.tif'))

    def test_master_maker_icc(self):
        profile_target_path = abspath(join(
            dirname(realpath(__file__)),
            '..',
            'isaw',
            'awib',
            'icc',
            '{}.icc'.format('ProPhoto')))
        profile_target = getOpenProfile(profile_target_path)
        for fn, im in self.images.items():
            maker = MasterMaker(im)
            maker.make()
            master = maker.master
            assert_equal(
                getProfileName(
                    getOpenProfile(BytesIO(master.info['icc_profile']))),
                getProfileName(profile_target))

    def test_master_maker_save(self):
        self.logger.debug('test_master_maker_save')
        profile_target_path = abspath(join(
            dirname(realpath(__file__)),
            '..',
            'isaw',
            'awib',
            'icc',
            '{}.icc'.format('ProPhoto')))
        profile_target = getOpenProfile(profile_target_path)
        i = 0
        for fn, im_in in self.images.items():
            i += 1
            self.logger.debug('input filename: "{}"'.format(fn))
            maker = MasterMaker(im_in, logging_threshold=logging.DEBUG)
            master = maker.make()
            name, extension = splitext(fn)
            fn_out = 'test{}.tif'.format(i)
            self.logger.debug('output filename: "{}"'.format(fn_out))
            path_out = join(self.data_dir, 'scratch', fn_out)
            maker.save(path_out)
            continue

            im_out = Image.open(path_out)
            im_out.load()
            try:
                im_out.fp.close()
            except AttributeError:
                pass
            assert_equal(im_out.format, 'TIFF')
            assert_equal(master.mode, im_out.mode)
            stat_im_out = Stat(im_out)
            stat_master = Stat(master)
            assert_equal(stat_im_out.extrema, stat_master.extrema)
            assert_equal(stat_im_out.count, stat_master.count)
            assert_equal(stat_im_out.sum, stat_master.sum)
            assert_equal(stat_im_out.mean, stat_master.mean)
            assert_equal(stat_im_out.median, stat_master.median)
            assert_equal(stat_im_out.rms, stat_master.rms)
            assert_equal(stat_im_out.var, stat_master.var)
            self.logger.debug('info keys: {}'.format(im_out.info.keys()))
            assert_equal(
                getProfileName(
                    getOpenProfile(BytesIO(master.info['icc_profile']))),
                getProfileName(profile_target))
