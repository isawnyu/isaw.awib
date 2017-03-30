"""
Make a master image for an existing original
"""

import argparse
import logging
from lxml import etree
import os
from os.path import isfile, isdir, join, realpath, split, splitext
import re
from slugify import slugify
import sys
import traceback
import uuid

DEFAULT_LOG_LEVEL = logging.ERROR
POSITIONAL_ARGUMENTS = [
    ['-l', '--loglevel', 'NOTSET',
        'desired logging level (' +
        'case-insensitive string: DEBUG, INFO, WARNING, or ERROR'],
    ['-v', '--verbose', False, 'verbose output (logging level == INFO)'],
    ['-w', '--veryverbose', False,
        'very verbose output (logging level == DEBUG)'],
    ['-m', '--hostname', 'images.isaw.nyu.edu', 'url hostname'],
    ['-n', '--name', '', 'shortname for image']
]

RX_WHITESPACE = re.compile(r'\s+')


def get_text(tree, xpath):
    return ' '.join(
        etree.tostring(
            tree.xpath(xpath)[0],
            method="text",
            encoding="unicode"
        ).split())


def main(args):
    """
    main function
    """
    # logger = logging.getLogger(sys._getframe().f_code.co_name)
    if args.name != '':
        name = slugify(args.name.lower())
    else:
        pkg_path = realpath(args.pkg_path)
        metapath = join(pkg_path, 'metadata.xml')
        meta = etree.parse(metapath)
        name = get_text(meta, "//iptc_name")
    name = 'https://{}/{}'.format(args.hostname, name)
    guid = uuid.uuid5(uuid.NAMESPACE_URL, name)
    print(guid.urn)


if __name__ == "__main__":
    log_level = DEFAULT_LOG_LEVEL
    log_level_name = logging.getLevelName(log_level)
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    try:
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        for p in POSITIONAL_ARGUMENTS:
            d = {
                'help': p[3]
            }
            if type(p[2]) == bool:
                if p[2] is False:
                    d['action'] = 'store_true'
                    d['default'] = False
                else:
                    d['action'] = 'store_false'
                    d['default'] = True
            else:
                d['default'] = p[2]
            parser.add_argument(
                p[0],
                p[1],
                **d)
        # example positional argument
        # parser.add_argument(
        #     'foo',
        #     metavar='N',
        #     type=str,
        #     nargs='1',
        #     help="foo is better than bar except when it isn't")
        parser.add_argument(
            'pkg_path',
            type=str,
            help='path to image package')
        args = parser.parse_args()
        if args.loglevel is not 'NOTSET':
            args_log_level = re.sub('\s+', '', args.loglevel.strip().upper())
            try:
                log_level = getattr(logging, args_log_level)
            except AttributeError:
                logging.error(
                    "command line option to set log_level failed "
                    "because '%s' is not a valid level name; using %s"
                    % (args_log_level, log_level_name))
        elif args.veryverbose:
            log_level = logging.INFO
        elif args.verbose:
            log_level = logging.WARNING
        log_level_name = logging.getLevelName(log_level)
        logging.basicConfig(level=log_level)
        if log_level != DEFAULT_LOG_LEVEL:
            logging.warning(
                "logging level changed to %s via command line option"
                % log_level_name)
        else:
            logging.info("using default logging level: %s" % log_level_name)
        logging.debug("command line: '%s'" % ' '.join(sys.argv))
        main(args)
        sys.exit(0)
    except KeyboardInterrupt as e:  # Ctrl-C
        raise e
    except SystemExit as e:  # sys.exit()
        raise e
    except Exception as e:
        print("ERROR, UNEXPECTED EXCEPTION")
        print(str(e))
        traceback.print_exc()
        os._exit(1)
