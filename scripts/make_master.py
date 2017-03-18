"""
Make a master image for an existing original
"""

import argparse
from functools import wraps
from isaw.awib.conversions import MasterMaker
from isaw.awib import image_types
import logging
import os
from os.path import isfile, isdir, join, realpath, split, splitext
import re
import sys
import traceback

DEFAULT_LOG_LEVEL = logging.ERROR
POSITIONAL_ARGUMENTS = [
    ['-l', '--loglevel', 'NOTSET',
        'desired logging level (' +
        'case-insensitive string: DEBUG, INFO, WARNING, or ERROR'],
    ['-v', '--verbose', False, 'verbose output (logging level == INFO)'],
    ['-w', '--veryverbose', False,
        'very verbose output (logging level == DEBUG)'],
    ['-x', '--overwrite', False, 'overwite existing destination file'],
    ['-q', '--quiet', False, 'suppress all messages to stdout']
]


def arglogger(func):
    """
    decorator to log argument calls to functions
    """
    @wraps(func)
    def inner(*args, **kwargs):
        logger = logging.getLogger(func.__name__)
        logger.debug("called with arguments: %s, %s" % (args, kwargs))
        return func(*args, **kwargs)
    return inner


def eprint(msg):
    print('ERROR: {}'.format(msg), file=sys.stderr)


def erexit(msg):
    eprint(msg)
    sys.exit(1)


def make_masters(src, dest, overwrite):
    if isfile(dest):
        erexit('Destination must be a directory if source is a directory')
    file_list = [fn for fn in os.listdir(src) if isfile(join(src, fn))]
    file_list = [fn for fn in file_list if image_types.is_valid_filename(fn)]
    for fn in file_list:
        make_a_master(join(src, fn), dest, overwrite)


def make_a_master(src, dest, overwrite):
    head, tail = split(src)
    name, extension = splitext(tail)
    if isdir(dest):
        outf = join(dest, '{}.tif'.format(name))
    else:
        outf = dest
    if isfile(outf) and not overwrite:
        erexit('Destination file exists: "{}"'.format(outf))
    else:
        logging.warning(
            'Destination file will be overwritten: "{}"'.format(outf))
    head, tail = split(outf)
    name, extension = splitext(tail)
    if extension != '.tif':
        erexit(
            'Destination (output) must be a TIFF file ending in ".tif"')
    m = MasterMaker(src)
    m.make()
    m.save(outf)
    # logging.info('Saved master version of {} as {}'.format(src, outf))


@arglogger
def main(args):
    """
    main function
    """
    # logger = logging.getLogger(sys._getframe().f_code.co_name)
    src = realpath(args.original)
    dest = realpath(args.destination)

    if isdir(src):
        make_masters(src, dest, args.overwrite)
    elif not isfile(src):
        erexit('Original (input) file not found: "{}"'.format(src))
    else:
        make_a_master(src, dest, args.overwrite)

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
            'original',
            type=str,
            help='path to original image file')
        parser.add_argument(
            'destination',
            type=str,
            help=(
                'path to destination (i.e., new master file; must end in .tif'
                ))
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
        elif args.quiet:
            log_level = logging.CRITICAL
        log_level_name = logging.getLevelName(log_level)
        if not args.quiet:
            print('log level is {}'.format(log_level_name))
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
