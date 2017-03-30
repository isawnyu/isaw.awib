import argparse
import better_exceptions
import colorama
from colorama import Fore, Style
from copy import deepcopy
import csv
from datetime import datetime, timezone
from dateutil import parser as date_parser
from decimal import Decimal, getcontext, ROUND_HALF_EVEN
import json
import logging
from lxml import etree
import os
from os.path import realpath
import pwd
import re
import requests
import sys
import traceback
import io
import chardet
import codecs


colorama.init(autoreset=True)

MODIFIED = []

DEFAULT_LOG_LEVEL = logging.ERROR
OPTIONAL_ARGUMENTS = [
    ['-l', '--loglevel', 'NOTSET',
        'desired logging level (' +
        'case-insensitive string: DEBUG, INFO, WARNING, or ERROR'],
    ['-v', '--verbose', False, 'verbose output (logging level == INFO)'],
    ['-w', '--veryverbose', False,
        'very verbose output (logging level == DEBUG)'],
    ['-g', '--geonames_user', '', 'username for geonames api'],
    ['-p', '--photographer', '',
        'value, registry ID, or copy: for photographer'],
    ['-ch', '--copyright_holder', '', 'value or copy: for copyright holder'],
    ['-dp', '--date_photographed', '', 'value or copy: for date photographed']
]
PEOPLE_REGISTER = {}


class EditBailout(Exception):
    pass


class NoSuchOriginal(Exception):
    pass


def populate_registry(path):
    if path is None:
        return
    rpath = realpath(path)
    # MSExcel uses BOM on UTF-8 CSV, so check for it
    bytes = min(32, os.path.getsize(rpath))
    raw = open(rpath, 'rb').read(bytes)
    if raw.startswith(codecs.BOM_UTF8):
        encoding = 'utf-8-sig'
    else:
        encoding = chardet.detect(raw)['encoding']
    with io.open(rpath, 'r', encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            PEOPLE_REGISTER[row['id']] = {
                k: v for k, v in row.items() if k != 'id' and v != ''}


def set_text(element, value):
    if element.tag.startswith('date-'):
        s = value
        fail = True
        while fail:
            while len(s) < 3:
                print(Fore.RED + '>>>>>>>>>> ERROR: "{}": {}'.format(
                    s, 'Unrecognized datetime format'))
                s = input(Style.RESET_ALL + Fore.BLUE + 'Try again: ')
            try:
                date_val = date_parser.parse(s)
            except ValueError as e:
                print(Fore.RED + '>>>>>>>>>> ERROR: "{}": {}'.format(s, e))
                s = input(Style.RESET_ALL + Fore.BLUE + 'Try again: ')
            else:
                fail = False
        element.text = date_val.isoformat()
    elif type(value) == str:
        element.text = ' '.join(value.split())
    else:
        element.text = str(value)


def do_copy(tree, src_tag, dest_tag):
    context = "//info[@type='isaw']"
    xsrc = '/'.join((context, '{}'.format(src_tag)))
    xdest = '/'.join((context, '{}'.format(dest_tag)))
    try:
        src = tree.xpath(xsrc)[0]
    except IndexError:
        return
    try:
        dest = tree.xpath(xdest)[0]
    except IndexError:
        return
    if len(src) == 0:
        set_text(dest, src.text)
    else:
        for child in src:
            dest.append(deepcopy(child))
    MODIFIED.append(tree.getpath(dest))


def get_suggestion(tag):
    if tag == 'copyright-holder':
        return '[same as photographer]'
    elif tag == 'copyright-date':
        return '[same as photographed-date]'
    elif tag == 'copyright-contact':
        return '[same as photographer]'
    elif tag == 'license':
        return 'cc-by | cc-by-sa'
    elif tag == 'photographed-place':
        return '=gps | =gpsgeonames | {{url}}'
    elif 'place' in tag:
        return '{{url}}'
    else:
        return ''


def dms2dd(dms: str, precision=7):
    """
    convert degrees-minutes-seconds to signed digital degrees
    default precision value of 7: approx 1.1m (i.e., just a bit better than
    handheld GPS)
    """
    rxdms = re.compile(
        '^(?P<degrees>\d+)\s+deg\s+(?P<minutes>\d+)\'\s+(?P<seconds>[\d\.]+)'
        '(\"|\')\s*(?P<hemisphere>.)$')
    m = rxdms.match(dms)
    if m is not None:
        getcontext().prec = precision
        getcontext().rounding = ROUND_HALF_EVEN
        degrees = Decimal(m['degrees'])
        minutes = Decimal(m['minutes'])
        seconds = Decimal(m['seconds'])
        if m['hemisphere'] in ['N', 'E']:
            sign = Decimal(1)
        else:
            sign = Decimal(-1)
        result = (
            degrees + (minutes/Decimal(60)) + (seconds/Decimal(3600))) * sign
        return result
    else:
        return None


def set_with_registry(element, id):
    try:
        p = PEOPLE_REGISTER[id]
    except KeyError:
        return ''
    else:
        for child in element:
            element.remove(child)
        for k, v in p.items():
            tag = k.replace('_', '-')
            e = etree.SubElement(element, tag)
            set_text(e, v)
    return etree.tostring(element, pretty_print=True, encoding="unicode")


def set_with_gps(tree, element):
    srcxp = "//info[@type='original']/gps-data/*"
    src = tree.xpath(srcxp)
    if len(src) == 0:
        print(
            Fore.RED +
            '>>>>>>>>>> ERROR IGNORED: no original gps data found in metadata '
            'file.')
    else:
        rxerror = re.compile('^(?P<value>\d+)(?P<units>.+)$')
        d = {}
        for e in src:
            if e.tag in ['latitude', 'longitude']:
                d[e.tag] = dms2dd(e.text)
            elif e.tag == 'error':
                m = rxerror.match(e.text)
                if m is not None:
                    error = Decimal(m['value'])
                    units = m['units'].strip()
                    if units in ['f', 'ft', 'feet', 'ft.']:
                        error = error * Decimal(0.3048)
                        units = 'm'
                d['error'] = {'value': error, 'units': units}
        if len(d) > 0:
            e_gps = etree.SubElement(element, 'gps')
            e_gps.set('source', 'exif')
            for k, v in d.items():
                e = etree.SubElement(e_gps, k)
                if k == 'error':
                    e.set('units', v['units'])
                    set_text(e, v['value'])
                else:
                    e.set('units', 'signed decimal degrees')
                    set_text(e, v)
            return (
                etree.tostring(
                    element, pretty_print=True, encoding="unicode"),
                d['latitude'],
                d['longitude'])


def set_with_url(element, url):
    if url.startswith('https://pleiades.stoa.org/places/'):
        return set_with_pleiades(element, url)
    elif url.startswith('http://www.geonames.org/'):
        return set_with_geonames(element, url)
    elif url.startswith('http://sws.geonames.org/'):
        return set_with_geonames(element, url)
    else:
        raise NotImplementedError('no support for set with url {}'.format(url))


def parse_geonames_response(element, url, response):
    url_safe = '&'.join([p for p in url.split('&') if 'username' not in p])
    element.set('source', url_safe)
    element.set('vintage', datetime.now(timezone.utc).isoformat())
    try:
        j = response.json()['geonames'][0]
    except KeyError:
        j = response.json()
    s = etree.SubElement(element, 'geonames_id')
    geoid = j['geonameId']
    set_text(s, geoid)
    s = etree.SubElement(element, 'geonames_url')
    set_text(s, 'http://www.geonames.org/{}'.format(geoid))
    name = j['name']
    if name == '':
        name = j['topnymName']
    if name != '':
        if j['fcode'] == 'PPL':
            s = etree.SubElement(element, 'city')
        else:
            s = etree.SubElement(element, 'sublocation')
        set_text(s, j['name'])
    admin = []
    for i in range(5, 0, -1):
        admin.append(j['adminName{}'.format(i)].strip())
    admin = [a for a in admin if a != '']
    admin = ', '.join(admin)
    if admin != '':
        s = etree.SubElement(element, 'state_province')
        set_text(s, admin)
    country = j['countryName']
    if country != '':
        s = etree.SubElement(element, 'country')
        set_text(s, country)
    country = j['countryCode']
    if country != '':
        s = etree.SubElement(element, 'country_code')
        set_text(s, country)
    return etree.tostring(element, pretty_print=True, encoding="unicode")


def set_with_geonames_latlon(element, lat, lon):
    url_parts = [
        'http://api.geonames.org/findNearbyJSON?lat={}'.format(lat),
        'lng={}'.format(lon),
        'username={}'.format(GEONAMES_USER),
        'style=full']
    url_json = '&'.join(url_parts)
    r = requests.get(url_json)
    if r.status_code != 200:
        return
    return parse_geonames_response(element, url_json, r)


def set_with_geonames(tree, element, url):
    if 'place' not in element.tag:
        raise NotImplementedError(
            "can't set {} from GeoNames".format(element.tag))
    rxgeo = re.compile(
        '^https?:\/\/(www|sws)\.geonames\.org\/(?P<geoid>\d+)(|\/|\/.*)$')
    m = rxgeo.match(url)
    if m is None:
        return
    geoid = m.group('geoid')
    url_parts = [
        'http://api.geonames.org/getJSON?geonameId={}'.format(geoid),
        'username={}'.format(GEONAMES_USER),
        'style=full'
        ]
    url_json = '&'.join(url_parts)
    r = requests.get(url_json)
    if r.status_code != 200:
        return
    return parse_geonames_response(element, url_json, r)


def set_with_pleiades(tree, element, url):
    if 'place' not in element.tag:
        raise NotImplementedError(
            "can't set {} from Pleiades".format(element.tag))
    if url.endswith('/json'):
        url_json = url
        url_place = '/'.join(url.split('/')[:-1])
    else:
        url_place = url
        url_json = '{}/json'.format(url)
    r = requests.get(url_json)
    if r.status_code != 200:
        return
    element.set('source', url_json)
    j = r.json()
    modern = False
    title = ''
    for name in j['names']:
        for period in name['attestations']:
            if period['timePeriod'] == 'modern':
                modern = True
                if name['language'] == 'en':
                    if name['attested'] != '':
                        title = name['attested']
                    else:
                        title = name['romanized']
                    break
        if title != '':
            break
    if title == '':
        title = j['title']
    if 'settlement' in j['placeTypes'] and modern:
        s = etree.SubElement(element, 'city_name')
        set_text(s, title)
    else:
        s = etree.SubElement(element, 'sublocation_name')
        set_text(s, title)
    s = etree.SubElement(element, 'url')
    set_text(s, url_place)
    return etree.tostring(element, pretty_print=True, encoding="unicode")


def force_it(tree, element, cmd):
    result = None
    directives = {}
    print(
        '>>>>>>>>>> INPUT OVERRIDE: detected command-line option --{}="{}"'
        ''.format(element.tag.replace('-', '_'), cmd))
    if cmd.startswith('http'):
        result = set_with_url(element, cmd)
        MODIFIED.append(tree.getpath(element))
    elif cmd == 'copy:original':
        path = tree.getpath(element).split('/')
        if 'info[2]' in path:
            path = path[path.index('info[2]')+1:]
        xp = ['//info[@type=\'original\']']
        xp.extend(path)
        xp = '/'.join(xp)
        try:
            orig = tree.xpath(xp)[0]
        except IndexError:
            pass
        else:
            if orig.text is not None:
                set_text(element, orig.text)
                MODIFIED.append(tree.getpath(element))
    elif cmd.startswith('registry:'):
        result = set_with_registry(element, cmd[9:])
        MODIFIED.append(tree.getpath(element))
    elif cmd.startswith('copy:'):
        directives[element.tag] = cmd
    else:
        set_text(element, cmd)
        MODIFIED.append(tree.getpath(element))
    return (result, directives)


def handle_input(tree, element, orig, suggestion, pad):
    directives = {}
    s = input(Fore.BLUE + '{}>>> '.format(pad)).strip()
    print(Style.RESET_ALL, end='')
    result = None
    if s == '' or s == '=c':
        pass  # don't make any changes
    elif s == '=o' and orig is not None:
        print('{}capturing original: "{}"'.format(pad, orig.text))
        set_text(element, orig.text)
        MODIFIED.append(tree.getpath(element))
    elif s == '=e':
        print('{}erasing current value'.format(pad))
        element.text = None
        MODIFIED.append(tree.getpath(element))
    elif s == '=s' and suggestion != '':
        if suggestion.startswith('[same as'):
            where = suggestion[8:-1]
            directives[element.tag] = 'copy:{}'.format(where)
        elif '|' in suggestion:
            options = [sug.strip() for sug in suggestion.split('|')]
            while '|' in suggestion:
                s = input(
                    Style.RESET_ALL + Fore.RED +
                    '>>>>>>>>>> Error: " ": please enter "{}" or nothing >>> '
                    ''.format(s, '" or "'.join(options)))
            else:
                set_text(element, s)
                MODIFIED.append(tree.getpath(element))
        else:
            set_text(element.text, suggestion)
            MODIFIED.append(tree.getpath(element))
    elif s == '=x':
        print('{}exit'.format(pad))
        raise EditBailout('user requested exit')
    elif s == '=gps' and 'place' in element.tag:
        print(
            '{}converting GPS data from exif content in original'.format(pad))
        result, lat, lon = set_with_gps(tree, element)
        MODIFIED.append(tree.getpath(element))
    elif s.startswith('=registry:'):
        result = set_with_registry(element, s[9:])
        MODIFIED.append(tree.getpath(element))
    elif s == '=gpsgeonames' and 'place' in element.tag:
        print(
            '{}converting GPS data from exif content in original'.format(pad))
        result, lat, lon = set_with_gps(tree, element)
        print('{}querying geonames for closest place'.format(pad))
        result = set_with_geonames_latlon(element, lat, lon)
        MODIFIED.append(tree.getpath(element))
    elif s.startswith('http'):
        result = set_with_url(element, s)
        MODIFIED.append(tree.getpath(element))
    elif len(s) > 1 and s[0] == '=':
        directives[element.tag] = 'copy:{}'.format(s[1:])
    else:
        set_text(element, s)
        MODIFIED.append(tree.getpath(element))
    return (result, directives)


def get_val(tree, element, args):
    directives = {}
    path = tree.getpath(element).split('/')
    if 'info[2]' in path:
        path = path[path.index('info[2]')+1:]
    pad = ' '
    for n in range(len(path)):
        pad += '+ '
    print('\n' + Fore.RED + '{}{}'.format(pad, element.tag))
    pad = pad.replace('+', ' ')
    if len(element) > 0:
        attr = element.tag.replace('-', '_')
        if hasattr(args, attr):
            result, d = force_it(tree, element, getattr(args, attr))
        else:
            result = None
            for child in element:
                d = get_val(tree, child, args)
                for k, v in d.items():
                    directives[k] = v
    else:
        # display current value, if any
        if element.text is not None:
            print(Style.DIM + '{}currently: "{}"'.format(pad, element.text))

        # display original value, if any
        xp = ['//info[@type=\'original\']']
        xp.extend(path)
        xp = '/'.join(xp)
        try:
            orig = tree.xpath(xp)[0]
        except IndexError:
            orig = None
        else:
            if orig.text is not None:
                print(Style.DIM + '{}original: "{}"'.format(pad, orig.text))
            else:
                orig = None

        # display suggestion value, if any
        suggestion = get_suggestion(element.tag)
        if len(suggestion) > 0:
            print(Style.DIM + '{}suggestion: {}'.format(pad, suggestion))

        # attempt to populate
        attr = element.tag.replace('-', '_')
        if hasattr(args, attr):
            result, d = force_it(tree, element, getattr(args, attr))
        else:
            result, d = handle_input(tree, element, orig, suggestion, pad)
        for k, v in d.items():
            directives[k] = v
    if result is not None:
        print('{}using: '.format(pad))
        for line in result.split('\n'):
            print('  {}{}'.format(pad, line))
    elif element.tag in directives.keys():
        for tag_name, directive in directives.items():
            print(
                '{}a directive has been set for {}: {}'
                ''.format(pad, tag_name, directive))
    else:
        print('{}using "{}"'.format(pad, element.text))

    return directives


def main(args):
    logger = logging.getLogger(sys._getframe().f_code.co_name)
    populate_registry(args.people_registry)
    meta_path = realpath(args.meta_file)
    lxml_parser = etree.XMLParser(remove_blank_text=True)
    meta = etree.parse(meta_path, lxml_parser)
    isaw_info = meta.xpath("//info[@type='isaw']")[0]
    try:
        directives = get_val(meta, isaw_info, args)
    except EditBailout:
        print('fine, be that way')
    else:
        for dest_tag, directive in directives.items():
            logger.debug(
                'directive for "{}" is "{}"'.format(dest_tag, directive))
        for dest_tag, directive in directives.items():
            cmd, src_tag = directive.split(':')
            if cmd == 'copy':
                do_copy(meta, src_tag, dest_tag)
    change = etree.Element('change')
    e = etree.SubElement(change, 'date')
    e.text = datetime.now(timezone.utc).isoformat()
    e = etree.SubElement(change, 'agent')
    e.text = pwd.getpwuid(os.getuid())[4]
    e = etree.SubElement(change, 'description')
    e.text = (
        'Modified the following fields in the isaw info section: {}.'
        ''.format(
            ', '.join(
                [(x, x.split('/')[-1])[x.startswith('/image-info/info[2]/')]
                    for x in MODIFIED])))
    change_history = meta.xpath('//change-history')[0]
    change_history.insert(0, change)
    os.rename(meta_path, meta_path+".bak")
    with open(meta_path, 'w', encoding="UTF-8") as f:
        f.write(etree.tostring(meta, pretty_print=True, encoding="unicode"))

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        for p in OPTIONAL_ARGUMENTS:
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
            'meta_file',
            type=str,
            help='path to metadata xml file')
        parser.add_argument(
            'people_registry',
            type=str,
            nargs='?',
            help='path to people registry file')
        args = parser.parse_args()
        if args.loglevel is not 'NOTSET':
            args_log_level = re.sub('\s+', '', args.loglevel.strip().upper())
            try:
                log_level = getattr(logging, args_log_level)
            except AttributeError:
                logging.error(
                    "command line option to set log_level failed "
                    "because '%s' is not a valid level name; using %s"
                    % (args_log_level, logging.getLevelName(
                        DEFAULT_LOG_LEVEL)))
                log_level = DEFAULT_LOG_LEVEL
        elif args.veryverbose:
            log_level = logging.DEBUG
        elif args.verbose:
            log_level = logging.INFO
        else:
            log_level = DEFAULT_LOG_LEVEL
        log_level_name = logging.getLevelName(log_level)
        logging.basicConfig(level=log_level)
        if log_level != DEFAULT_LOG_LEVEL:
            logging.warning(
                "logging level changed to %s via command line option"
                % log_level_name)
        else:
            logging.info("using default logging level: %s" % log_level_name)
        logging.debug("command line: '%s'" % ' '.join(sys.argv))
        GEONAMES_USER = args.geonames_user
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
