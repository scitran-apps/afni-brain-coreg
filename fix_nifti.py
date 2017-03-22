'''
This script addresses an issue with some nifti files created by Vistasoft.

By default, Vistasoft nifti files are created with sform_code and qform_code
values of 2 [0], which are interpreted as "aligned to a template" by AFNI code.
Because these files are interpreted as "aligned", they will crash this brain
warp script. fix_nifti.py sets these values to 1 to avoid this issue.

0: https://github.com/vistalab/vistasoft/blob/8298ab/fileFilters/nifti/niftiCreate.m#L172-L173
'''

from __future__ import print_function
import nibabel as nib
import sys
import os
import subprocess


# from https://nifti.nimh.nih.gov/nifti-1/documentation/nifti1fields/nifti1fields_pages/xyzt_units.html
NIFTI_UNITS_MM = 2
NIFTI_UNITS_MICRON = 3
NIFTI_UNITS_SEC = 8
NIFTI_UNITS_RADS = 48


def eprint(*args, **kwargs):
    # print to stderr. copied from http://stackoverflow.com/a/14981125
    print(*args, file=sys.stderr, **kwargs)


if len(sys.argv) != 3:
    print('''
Usage: fix_nifti.py <input_file> <output_file>

Fixes some nifti headers that are incompatible with this afni brain warping
routine. To see more details, see the comments in this script.
''')
    sys.exit(1)

input_file, output_file = sys.argv[1:]

if not os.path.exists(input_file):
    eprint('input file {} does not exist'.format(input_file))
    sys.exit(1)

if os.path.exists(output_file):
    eprint('warning: output file {} exists and will be overwritten'.format(
        output_file))

image = nib.load(input_file)

incorrect_headers = False
if image.header['descrip'] == 'VISTASOFT':
    for key in ['qform_code', 'sform_code']:
        if image.header[key] == 2:
            incorrect_headers = True
            image.header[key] = 1

    if incorrect_headers:
        eprint(
            'warning: native image input headers suggest it might be '
            'mistakenly marked as aligned by vistasoft. going to fix all headers')

        # XXX assert that sform is all 1s and != qform
        # While the pixdim and qform of these images are ok, the sform is incorrect.
        # We will overwrite the sform with the qform.
        aff = image.header.get_qform()
        # force affine and sform to qform so we can reset. Only setting
        # one or the other might not work.
        # see more details here: https://github.com/nipy/nibabel/pull/90
        image.affine[:] = aff
        image.header.set_sform(aff)

    xyzt_units = image.header['xyzt_units']
    if (
        # we are checking here for some known bad units info from the conversion program
        (xyzt_units & 0b111) == NIFTI_UNITS_MICRON and
        (xyzt_units & 0b111000) == NIFTI_UNITS_RADS
    ):
        # clear out lower bits (first 6) and add in the right units info
        image.header['xyzt_units'] = \
            (xyzt_units & 0b11000000) | NIFTI_UNITS_MM | NIFTI_UNITS_SEC

        # when we have bad units, we also fix some issues with TR dimension size
        assert image.header['pixdim'][4] == 1.0, \
            'We expected {} to have pixdim time unit of 1.0, but it had {}'.format(
                input_file,
                image.header['pixdim'][4],
            )
        for _ in range(100):
            eprint('verify TR of 2 for {}'.format(input_file))
        image.header['pixdim'][4] = 2.0

nib.save(image, output_file)

if incorrect_headers:
    # XXX assert that image is currently LPI?
    subprocess.check_call(['3drefit', '-orient', 'LAI', output_file])
