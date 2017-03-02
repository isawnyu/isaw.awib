from io import BytesIO
import logging
from os.path import abspath, dirname, join
from PIL import Image
from PIL.ImageCms import getOpenProfile, getProfileName, profileToProfile
import sys


def make_master(
    src,
    dest=None
):
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    profile_srgb2 = join(
        dirname(
            abspath(__file__)), 'icc', 'sRGB_IEC61966-2-1_black_scaled.icc')
    profile_srgb4 = join(
        dirname(abspath(__file__)), 'icc', 'sRGB_v4_ICC_preference.icc')

    logger.debug('type(src): {}'.format(type(src)))
    if type(src) == str:
        original_image = Image.open(src)
    else:
        original_image = src
    # detect and convert/assign profile
    try:
        raw_profile = original_image.info['icc_profile']
    except KeyError:
        raw_profile = getOpenProfile(profile_srgb2).tobytes()
        logger.warning(
            '"{}" does not have an internal ICC color profile.'.format(src))
    else:
        logger.debug('detected internal ICC color profile in "{}"'.format(src))
    original_profile = getOpenProfile(BytesIO(raw_profile))
    original_profile_name = getProfileName(original_profile).strip()
    target_profile = getOpenProfile(profile_srgb4)
    target_profile_name = getProfileName(target_profile).strip()
    logger.debug(
        'attempting to convert from "{}" to "{}"'
        ''.format(original_profile_name, target_profile_name))
    converted_image = profileToProfile(
        original_image, original_profile, target_profile)
    return converted_image
