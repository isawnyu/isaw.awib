from datetime import datetime
from io import BytesIO
import logging
from logging import DEBUG, INFO, CRITICAL
from os.path import abspath, dirname, join, realpath
from PIL import Image, TiffImagePlugin
from PIL.ImageCms import (applyTransform, buildTransform, getOpenProfile,
                          getProfileName, INTENT_PERCEPTUAL, PyCMSError)


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

    def make(self):
        self._standardize_icc()
        return self.master

    def save(self, dest=None):
        if dest is None:
            if self.dest is None:
                raise RuntimeError(
                    'save method called with no destination filename')
            else:
                destination = abspath(self.dest)
        else:
            destination = abspath(dest)
        self.master.DEBUG = True
        self.master.save(destination)

    def _standardize_icc(self, target='ProPhoto'):
        profile_target = self._get_profile_from_file(target)
        profile_target_name = getProfileName(profile_target).strip()
        profile_original = self._get_original_profile()
        profile_original_name = getProfileName(profile_original).strip()
        if profile_original == profile_target:
            self.master = self.original
            self.log(
                'Original ICC profile was already the specified target ({}).'
                ''.format(profile_target_name))
        else:
            try:
                tx = buildTransform(
                    profile_original,
                    profile_target,
                    self.original.mode,
                    'RGB',
                    renderingIntent=INTENT_PERCEPTUAL)
            except PyCMSError as e:
                if str(e) == 'cannot build transform':
                    if self.original.mode == 'P':
                        im = self.original.convert('RGB')
                        tx = buildTransform(
                            profile_original,
                            profile_target,
                            im.mode,
                            'RGB',
                            renderingIntent=INTENT_PERCEPTUAL)
                else:
                    raise
            else:
                im = self.original
            self.master = applyTransform(im, tx, inPlace=False)
            self.log(
                'Original ICC profile ({}) was converted to the standard '
                'target ({}).'
                ''.format(
                    profile_original_name,
                    profile_target_name))

    def _get_profile_from_file(self, profile_name):
        fn = join(
            dirname(realpath(__file__)),
            'icc',
            '{}.icc'.format(profile_name))
        return getOpenProfile(fn)

    def _get_original_profile(self):
        try:
            raw_profile = getOpenProfile(
                BytesIO(self.original.info['icc_profile']))
        except KeyError:
            raw_profile = self._get_profile_from_file(
                'sRGB_IEC61966-2-1_black_scaled')
            self.log(
                'Original image does not have an internal ICC color profile.'
                '{} has been assigned.'
                ''.format(getProfileName(raw_profile).strip()))
        else:
            self.log(
                'Detected internal ICC color profile in original image: {}.'
                ''.format(getProfileName(raw_profile).strip()))
        return raw_profile

