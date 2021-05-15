from argparse import ArgumentParser,  RawTextHelpFormatter
from gettext import translation
from os import path, remove
from shutil import copyfile
from subprocess import run
from pkg_resources import resource_filename

from translate_odf.version import argparse_epilog

try:
    t=translation('translate_odf', resource_filename("translate_odf","locale"))
    _=t.gettext
except:
    _=str

def run_check(command, shell=False):
    p=run(command, shell=shell, capture_output=True);
    if p.returncode!=0:
        print(f"Error en comando. {command}")
        print("STDOUT:")
        print(p.stdout.decode('utf-8'))
        print("STDERR:")
        print(p.stderr.decode('utf-8'))
        print("Saliendo de la instalación")
        exit(2)

def main():
    parser=ArgumentParser(prog='translate_odf', description=_('Translate ODF files with XLF formats'), epilog=argparse_epilog(), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--from_language', action='store', help=_('Language to translate from. Example codes: es, fr, en, md'), required=True, metavar="CODE")
    parser.add_argument('--to_language', action='store', help=_('Language to translate to. Example codes: es, fr, en, md'), required=True,  metavar="CODE")
    parser.add_argument('--input', action='store', help=_('File to translate'), required=True,  metavar="FILE")
    parser.add_argument('--output', action='store', help=_('Path where translated file is going to be generated. If missing add tranlation code before name extension'), default=None,  metavar="FILE")
    parser.add_argument('--catalogue', action='store', help=_('Catalogue with strings to translate in XLIFF format'), default=None,  metavar="FILE")
    parser.add_argument('--auxiliar', action='append', help=_('Auxiliar catalogues to fast translations. File from other projects to help translation. Can be used several times'), default=[],  metavar="FILE")
    args=parser.parse_args()

    extension=args.input.split(".")[1:][0]

    if len(args.auxiliar)>0:
        print (_("Help catalogues are not developed yet"))

    if args.output is None:
        args.output=f"{args.input}.{args.to_language}.{extension}"
        
    if args.catalogue is None:
        args.catalogue=f"{args.input}.{args.to_language}.xlf"

    print(_(f"Translating '{args.input}' from '{args.from_language }' to '{args.to_language}'"))
    print(_(f"  - Output: {args.output}"))
    print(_(f"  - File to translate: {args.catalogue}"))

    original_xlf="original.xlf"
    temporal_destiny_xlf="temporal_destiny.xlf"
    run_check(["odf2xliff", args.input, original_xlf])
    if path.exists(args.catalogue) is True and path.getsize(args.catalogue) > 0:
        run_check(["pomerge", "-t", original_xlf, "-i", args.catalogue, "-o", temporal_destiny_xlf]) #Here was mergeblanks
    else:
        print(_("Catalogue doesn't exists or is empty. Creating from empty catalogue"))
        copyfile(original_xlf, args.catalogue)
    run_check(["xliff2odf", "-t",  args.input, "-i", args.catalogue, args.output])

    if path.exists(original_xlf) is True:
        remove(original_xlf)

    if path.exists(temporal_destiny_xlf) is True:
        remove(temporal_destiny_xlf)
