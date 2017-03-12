from os.path import basename, splitext

IMAGETYPES = {
    'BMP': {
        'mimetype': 'image/bmp',
        'description': 'Windows or OS/2 Bitmap',
        'write': True,
        'extensions': ['bmp']},
    'EXR': {
        'mimetype': 'image/x-exr',
        'description': 'ILM OpenEXR',
        'write': True,
        'extensions': ['exr']},
    'GIF': {
        'mimetype': 'image/gif',
        'description': 'Graphics Interchange Format',
        'write': True,
        'extensions': ['gif']},
    'HDR': {
        'mimetype': 'image/vnd.radiance',
        'description': 'High Dynamic Range Image',
        'write': True,
        'extensions': ['hdr']},
    'ICO': {
        'mimetype': 'image/vnd.microsoft.icon',
        'description': 'Windows Icon',
        'write': True,
        'extensions': ['ico']},
    'IFF': {
        'mimetype': 'image/x-iff',
        'description': 'IFF Interleaved Bitmap',
        'write': False,
        'extensions': ['iff', 'lbm'],
        'write_extension': 'iff'},
    'J2K': {
        'mimetype': 'image/j2k',
        'description': 'JPEG-2000 codestream',
        'write': True,
        'extensions': ['j2k', 'j2c'],
        'write_extension': 'j2k'},
    'JNG': {
        'mimetype': 'image/x-mng',
        'description': 'JPEG Network Graphics',
        'write': True,
        'extensions': ['jng']},
    'JP2': {
        'mimetype': 'image/jp2',
        'description': 'JPEG-2000 File Format',
        'write': True,
        'extensions': ['jp2']},
    'JPEG': {
        'mimetype': 'image/jpeg',
        'description': 'JPEG - JFIF Compliant',
        'write': True,
        'extensions': ['jpg', 'jif', 'jpeg', 'jpe'],
        'write_extension': 'jpg'},
    'KOALA': {
        'mimetype': 'image/x-koala',
        'description': 'C64 Koala Graphics',
        'write': False,
        'extensions': ['koa']},
    'PBM': {
        'mimetype': 'image/freeimage-pnm',
        'description': 'Portable Bitmap (ASCII)',
        'write': True,
        'extensions': ['pbm']},
    'PBMRAW': {
        'mimetype': 'image/freeimage-pnm',
        'description': 'Portable Bitmap (RAW)',
        'write': True,
        'extensions': ['pbm']},
    'PCD': {
        'mimetype': 'image/x-photo-cd',
        'description': 'Kodak PhotoCD',
        'write': False,
        'extensions': ['pcd']},
    'PCX': {
        'mimetype': 'image/x-pcx',
        'description': 'Zsoft Paintbrush',
        'write': False,
        'extensions': ['pcx']},
    'PFM': {
        'mimetype': 'image/x-portable-floatmap',
        'description': 'Portable floatmap',
        'write': True,
        'extensions': ['pfm']},
    'PGM': {
        'mimetype': 'image/freeimage-pnm',
        'description': 'Portable Greymap',
        'write': True,
        'extensions': ['pgm']},
    'PICT': {
        'mimetype': 'image/x-pict',
        'description': 'Macintosh PICT',
        'write': False,
        'extensions': ['pct', 'pict', 'pic'],
        'write_extension': 'pct'},
    'PNG': {
        'mimetype': 'image/png',
        'description': 'Portable Network Graphics',
        'write': True,
        'extensions': ['png']},
    'PPM': {
        'mimetype': 'image/freeimage-pnm',
        'description': 'Portable Pixelmap',
        'write': True,
        'extensions': ['ppm']},
    'PSD': {
        'mimetype': 'image/vnd.adobe.photoshop',
        'description': 'Adobe Photoshop',
        'write': False,
        'extensions': ['psd']},
    'RAS': {
        'mimetype': 'image/x-cmu-raster',
        'description': 'Sun Raster Image',
        'write': False,
        'extensions': ['ras']},
    'RAW': {
        'mimetype': 'image/x-dcraw',
        'description':  'RAW camera image',
        'write': False,
        'extensions': [
            '3fr', 'arw', 'bay', 'bmq', 'cap', 'cine', 'cr2', 'crw', 'cs1',
            'dc2', 'dcr', 'drf', 'dsc', 'dng', 'erf', 'fff', 'ia', 'iiq',
            'k25', 'kc2', 'kdc', 'mdc', 'mef', 'mos', 'mrw', 'nef', 'nrw',
            'orf', 'pef', 'ptx', 'pxn', 'qtk', 'raf', 'raw', 'rdc', 'rw2',
            'rwl', 'rwz', 'sr2', 'srf', 'srw', 'sti']},
    'SGI': {
        'mimetype': 'image/x-sgi',
        'description': 'SGI Image Format',
        'write': False,
        'extensions': ['sgi']},
    'TARGA': {
        'mimetype': 'image/x-tga',
        'description': 'Truevision Targa',
        'write': True,
        'extensions': ['tga', 'targa']},
    'TIFF': {
        'mimetype': 'image/tiff',
        'description': 'Tagged Image File Format',
        'write': True,
        'extensions': ['tif', 'tiff']},
    'WBMP': {
        'mimetype': 'image/vnd.wap.wbmp',
        'description': 'Wireless Bitmap',
        'write': True,
        'extensions': ['wap', 'wbmp', 'wbm']},
    'XBM': {
        'mimetype': 'image/x-xbitmap',
        'description': 'X11 Bitmap Format',
        'write': False,
        'extensions': ['xbm']},
    'XPM': {
        'mimetype': 'image/x-xpixmap',
        'description': 'X11 Pixmap Format',
        'write': True,
        'extensions': ['xpm']}
}

VALID_EXTENSIONS = []
for k, v in IMAGETYPES.items():
    VALID_EXTENSIONS.extend(v['extensions'])
VALID_EXTENSIONS = sorted(list(set(VALID_EXTENSIONS)))


def is_valid_filename(filename):
    name, extension = splitext(basename(filename))
    return extension[1:] in VALID_EXTENSIONS
