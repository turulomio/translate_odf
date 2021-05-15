import argparse
import gettext
from os import path,remove
from shutil import copyfile
import pkg_resources
import subprocess

from translate_odf.version import argparse_epilog

try:
    t=gettext.translation('translate_odf',pkg_resources.resource_filename("translate_odf","locale"))
    _=t.gettext
except:
    _=str

def main():
    parser=argparse.ArgumentParser(prog='translate_odf', description=_('Translate ODF files with XLF formats'), epilog=argparse_epilog(), formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--from', action='store', help=_('Language to translate from. Example codes: es, fr, en, md'), required=True, metavar="CODE")
    parser.add_argument('--to', action='store', help=_('Language to translate to. Example codes: es, fr, en, md'), required=True,  metavar="CODE")
    parser.add_argument('--file_from', action='store', help=_('File to translate'), required=True,  metavar="FILE")
    parser.add_argument('--file_to', action='store', help=_('File where tranlated file is going to be generated. If missing add tranlation code before name extension'), default=None,  metavar="FILE")
    parser.add_argument('--catalogue', action='store', help=_('Catalogue with strings to translate in XLIFF format'), default=None,  metavar="FILE")
    parser.add_argument('--auxiliar', action='append', help=_('Auxiliar catalogues to fast translations. File from other projects to help translation. Can be used several times'), default=[],  metavar="FILE")
    args=parser.parse_args()

    extension=args.file_from.split(".")[1:][0]

    if len(args.auxiliar)>0:
        print (_("Help catalogues are not developed yet"))

    if args.file_to is None:
        args.file_to=f"{args.file_from}.{args.to}.{extension}"
        
    if args.catalogue is None:
        args.catalogue=f"{args.file_from}.{args.to}.xlf"

    print(args.file_to)

    original_xlf="original.xlf"
    temporal_destiny_xlf="temporal_destiny.xlf"
    subprocess.run(["odf2xliff", args.file_from, original_xlf])
    if path.exists(args.catalogue) is True and path.getsize(args.catalogue) > 0:
        subprocess.run(["pomerge", "-t", original_xlf, "-i", args.catalogue, "-o", temporal_destiny_xlf]) #Here was mergeblanks
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
    subprocess.run(["xliff2odf", "-t",  args.file_from, "-i", args.catalogue, args.file_to])

    if path.exists(original_xlf) is True:
        remove(original_xlf)

    if path.exists(temporal_destiny_xlf) is True:
        remove(temporal_destiny_xlf)
