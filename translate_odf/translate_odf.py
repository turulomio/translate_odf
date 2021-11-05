from argparse import ArgumentParser,  RawTextHelpFormatter
from gettext import translation
from os import path, remove
from shutil import copyfile
from subprocess import run
from pkg_resources import resource_filename
from translate_odf.reusing.file_functions import replace_in_file
import xml.etree.ElementTree as ET

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

def main_xlf():
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
def innercontent(element):
    return (element.text or '') + ''.join(ET.tostring(e, 'unicode').replace("ns0:", "") for e in element)

def main_po():
    parser=ArgumentParser(prog='translate_odf', description=_('Translate ODF files with XLF formats'), epilog=argparse_epilog(), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--from_language', action='store', help=_('Language to translate from. Example codes: es, fr, en, md'), required=True, metavar="CODE")
    parser.add_argument('--to_language', action='store', help=_('Language to translate to. Example codes: es, fr, en, md'), required=True,  metavar="CODE")
    parser.add_argument('--input', action='store', help=_('File to translate'), required=True,  metavar="FILE")
    parser.add_argument('--output', action='store', help=_('Path where translated file is going to be generated. If missing add tranlation code before name extension'), default=None,  metavar="FILE")
    parser.add_argument('--po', action='store', help=_('Catalogue with strings to translate in XLIFF format'), default=None,  metavar="FILE")
    parser.add_argument('--pot', action='append', help=_('Generate pot file'), default=None,  metavar="FILE")
    args=parser.parse_args()

    extension=args.input.split(".")[1:][0]

    if args.output is None:
        args.output=f"{args.input}.{args.to_language}.{extension}"
        
    if args.po is None:
        args.po=f"{args.input}.{args.to_language}.po"
    if args.pot is None:
        args.pot=f"{args.input}.{args.to_language}.pot"

    print(_(f"Translating '{args.input}' from '{args.from_language }' to '{args.to_language}'"))
    print(_(f"  - Output: {args.output}"))
    print(_(f"  - File catalog pot: {args.pot}"))
    print(_(f"  - File catalog po: {args.po}"))
    
    if path.exists(args.po)==False:
        run_check(["msginit", "-i", args.pot,  "-o", args.po])

    original_xlf="original.xlf"
    if path.exists(original_xlf) is True:
        remove(original_xlf)
    run_check(["odf2xliff", args.input, original_xlf])
    
    ##Leemos sources
    mytree = ET.parse(original_xlf)
    myroot = mytree.getroot()
    file_=myroot[0]
    body=file_[0]
    sources=set()
    for e in body:
        sources.add(innercontent(e[0])    )
    
    ##HACEMOS PO
    import polib

    po = polib.POFile()
    po.metadata = {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': 'you@example.com',
        'POT-Creation-Date': '2007-10-18 14:00+0100',
        'PO-Revision-Date': '2007-10-18 14:00+0100',
        'Last-Translator': 'you <you@example.com>',
        'Language-Team': 'English <yourteam@example.com>',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
    }
    for i,  source in enumerate(sources):
        entry = polib.POEntry(
            msgid=source,
            msgstr='', 
            occurrences=[('welcome.py', str(i)),]
        )
        po.append(entry)
    po.save(args.pot)


    
    
    
    
    #run_check(["xliff2po",  original_xlf,  args.pot])
    
    
    
    run_check(["msgmerge","-N", "--no-wrap","-U", args.po, args.pot])
    run_check(["po2xliff",  args.po,  "original_from_po.xlf"])
    import polib

    pofile = polib.pofile(args.po)
    d= {}
    for entry in pofile:
        d[entry.msgid]=entry.msgstr
    print(d)
        
        
    file_=myroot[0]
    print("file", file_)
    print("Tree", mytree)
    print("root", myroot)
    its=mytree.find("body")
    print(its)
    body=file_[0]
    for e in body:
        source=e[0]
        if source.text in d and d[source.text]!="":
            print(".")
            e.set('approved', 'yes')
            target=ET.SubElement(e, "target") 
            target.text=d[source.text]
#            target.set("state","signed-off")
#            target.set("phase-name","approval-1")
    mytree.write("original_from_po.xlf",encoding="UTF-8",xml_declaration=True)

#    
    replace_in_file("original_from_po.xlf", "ns0:", "")
    replace_in_file("original_from_po.xlf", ":ns0", "")

    run_check(["xliff2odf", "-t",  args.input, "-i", "original_from_po.xlf", args.output])
#

