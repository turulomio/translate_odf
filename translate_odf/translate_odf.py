import argparse
import gettext
from os import path,remove
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
        p=subprocess.run(["pomerge", "-t", original_xlf, "-i", args.catalogue, "-o", temporal_destiny_xlf]) #Here was mergeblanks
        if path.getsize(temporal_destiny_xlf)>0:
            #copyfile(temporal_destiny_xlf, args.catalogue)
            #With translate-2.5.0 --mergeblanks no gives error 'NoneType' object has no attribute 'strip' and generates and empty temporal_destiny_xlf
            # To simultae --mergeblanks I remove <target></target> from output
            output=""
            f=open(temporal_destiny_xlf,"r")
            for line in f.readlines():
                if line.find("<target></target>")!=-1:
                    continue
                output=output+line
            f.close()

            o=open(args.catalogue,"w")
            o.write(output)
            o.close()
        else:
            print("NO COPIO EL MERGE PORQUE ESTA VACIO")
    else:
        print("Catalogue doesn't exists or is empty. Creating from empty catalogue")
        copyfile(original_xlf, args.catalogue)
    p=subprocess.run(["xliff2odf", "-t",  args.file_from, "-i", args.catalogue, args.file_to])


    remove(original_xlf)
    remove(temporal_destiny_xlf)