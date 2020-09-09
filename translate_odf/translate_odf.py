import argparse
import gettext
from os import path
from shutil import copyfile
import pkg_resources
import subprocess
import sys

from translate_odf.version import argparse_epilog,  __version__

try:
    t=gettext.translation('translate_odf',pkg_resources.resource_filename("translate_odf","locale"))
    _=t.gettext
except:
    _=str

def main():
    parser=argparse.ArgumentParser(prog='translate_odf', description=_('Translate ODF files with XLF formats'), epilog=argparse_epilog(), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--from', action='store', help=_('Language to translate from'), required=True)
    parser.add_argument('--to', action='store', help=_('Language to translate from'), required=True)
    parser.add_argument('--file_from', action='store', help=_('Language to translate from'), required=True)
    parser.add_argument('--file_to', action='store', help=_('Language to translate from'), default=None)
    parser.add_argument('--catalogue', action='store', help=_('Language to translate from'), default=None)
    parser.add_argument('--help_catalogue', action='append', help=_('Language to translate from'), default=[])
    args=parser.parse_args()

    extension=args.file_from.split(".")[1:][0]
    
    if args.file_to is None:
        args.file_to=f"{args.file_from}.{args.to}.{extension}"
        
    if args.catalogue is None:
        args.catalogue=f"{args.file_from}.{args.to}.xlf"

    print(args.file_to)

    original_xlf="original.xlf"
    temporal_destiny_xlf=f"temporal_destiny.xlf"
    p=subprocess.run(["odf2xliff", args.file_from, original_xlf])
    if path.exists(args.catalogue) is True and path.getsize(args.catalogue) > 0:
        p=subprocess.run(["pomerge", "-t", original_xlf, "-i", args.catalogue, "-o", temporal_destiny_xlf, "--mergeblanks=no"])
        if path.getsize(temporal_destiny_xlf)>0:
            print("NO COPIO EL MERGE PORQUE ESTA VACIO")
            copyfile(temporal_destiny_xlf, args.catalogue)
    else:
        print("EMPTY FILE")
        copyfile(original_xlf, args.catalogue)
    p=subprocess.run(["xliff2odf", "-t",  args.file_from, "-i", args.catalogue, args.file_to])

