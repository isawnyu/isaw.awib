from datetime import datetime
from io import BytesIO
import logging
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
from os.path import abspath, dirname, join
from PIL import Image
from PIL.ImageCms import getOpenProfile, getProfileName, profileToProfile
import sys


class Historian():

    def __init__(self, logging_threshold=INFO):
        self.history = []
        self.logger = logging.getLogger()
        self.logger.setLevel(logging_threshold)

    def get_history(self):
        return self.history

    def log(self, msg, log_level=DEBUG, data=None):
        self._append_history(msg, log_level, data)

    def _append_history(self, msg, log_level=DEBUG, data=None):
        self.history.append((datetime.now(), msg, data))
        if self.logger.isEnabledFor(log_level):
            self.logger.log(log_level, '{}: {}'.format(type(self), msg))


class MasterMaker(Historian):

    def __init__(self, src, logging_threshold=INFO, dest=None):
        Historian.__init__(self, logging_threshold)
        try:
            self.original = Image.open(src)
        except AttributeError:
            self.original = src
            self.original_filename = 'unknown ({})'.format(
                self.original.format)
            self.log(
                'initiated with image already in RAM ({})'
                ''.format(self.original.format))
        else:
            self.original_filename = src
            self.log(
                'initiated and opened image ({}) from file "{}"'
                ''.format(self.original.format, src))
        self.dest = dest
        self.profiles = {
            'srgb2': getOpenProfile(
                join(
                    dirname(abspath(__file__)),
                    'icc',
                    'sRGB_IEC61966-2-1_black_scaled.icc')),
            'srgb4': getOpenProfile(
                join(
                    dirname(abspath(__file__)),
                    'icc',
                    'sRGB_v4_ICC_preference.icc')),
        }
        self.profiles['original'] = self._original_profile()

    def make(self):
        self._make_mode_rgb()
        # if dest is None:
        #     return self.master

    def _make_mode_rgb(self):
        if self.original.mode == 'RGB':
            self.rgb = self.original
        else:
            self.rgb = self.original.convert('RGB')

    def _original_profile(self, force=False):
        if not force:
            try:
                return self.profiles['original']
            except AttributeError:
                pass
            except KeyError:
                pass
        try:
            raw_profile = getOpenProfile(
                BytesIO(self.original.info['icc_profile']))
        except KeyError:
            raw_profile = self.profiles['srgb2']
            self.log(
                'Original image does not have an internal ICC color profile.'
                '{} has been assigned.'
                ''.format(getProfileName(raw_profile).strip()))
        else:
            self.log(
                'Detected internal ICC color profile in original image: {}.'
                ''.format(getProfileName(raw_profile).strip()))
        return raw_profile


        # original_profile = getOpenProfile(BytesIO(raw_profile))
        # original_profile_name = getProfileName(original_profile).strip()
        # target_profile = getOpenProfile(profile_srgb4)
        # target_profile_name = getProfileName(target_profile).strip()
        # logger.debug(
        #     'attempting to convert from "{}" to "{}"'
        #     ''.format(original_profile_name, target_profile_name))
        # converted_image = profileToProfile(
        #     original_image, original_profile, target_profile)
#
#
