from argparse import ArgumentParser,  RawTextHelpFormatter
from gettext import translation
from os import path, remove
from polib import POEntry,  POFile, pofile
from shutil import copyfile
from subprocess import run
from pkg_resources import resource_filename
from translate_odf.version import __version__
from unogenerator import ODT
import xml.etree.ElementTree as ET
from logging import info, ERROR, WARNING, INFO, DEBUG, CRITICAL, basicConfig, debug

from translate_odf.version import argparse_epilog

try:
    t=translation('translate_odf', resource_filename("translate_odf","locale"))
    _=t.gettext
except:
    _=str

## Sets debug sustem, needs
## @param args It's the result of a argparse     args=parser.parse_args()        
def addDebugSystem(level):
    logFormat = "%(asctime)s.%(msecs)03d %(levelname)s %(message)s [%(module)s:%(lineno)d]"
    dateFormat='%F %I:%M:%S'

    if level=="DEBUG":#Show detailed information that can help with program diagnosis and troubleshooting. CODE MARKS
        basicConfig(level=DEBUG, format=logFormat, datefmt=dateFormat)
    elif level=="INFO":#Everything is running as expected without any problem. TIME BENCHMARCKS
        basicConfig(level=INFO, format=logFormat, datefmt=dateFormat)
    elif level=="WARNING":#The program continues running, but something unexpected happened, which may lead to some problem down the road. THINGS TO DO
        basicConfig(level=WARNING, format=logFormat, datefmt=dateFormat)
    elif level=="ERROR":#The program fails to perform a certain function due to a bug.  SOMETHING BAD LOGIC
        basicConfig(level=ERROR, format=logFormat, datefmt=dateFormat)
    elif level=="CRITICAL":#The program encounters a serious error and may stop running. ERRORS
        basicConfig(level=CRITICAL, format=logFormat, datefmt=dateFormat)
    info("Debug level set to {}".format(level))

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
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--debug', help="Debug program information", choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"], default="ERROR")
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


def command_main_po(from_language, to_language, input, output=None, po=None, pot=None, pdf=False, undetected_strings=[], fake=None):
    extension=input.split(".")[1:][0]

    if output is None:
        output=f"{input}.{to_language}.{extension}"
    if po is None:
        po=f"{input}.{to_language}.po"
    if pot is None:
        pot=f"{input}.{to_language}.pot"

    print(_(f"Translating '{input}' from '{from_language }' to '{to_language}'"))
    print(_(f"  - Output: {output}"))
    print(_(f"  - File catalog pot: {pot}"))
    print(_(f"  - File catalog po: {po}"))
    
    original_xlf="original.xlf"
    if path.exists(original_xlf) is True:
        remove(original_xlf)
    
    doc=ODT(input)
    
    
    # Creating a list of ordered document strings
    run_check(["odf2xliff", input, original_xlf])
    ##Leemos sources
    mytree = ET.parse(original_xlf)
    myroot = mytree.getroot()
    file_=myroot[0]
    body=file_[0]
    sources=set()
    debug("==== EXTRACTING FROM XLF ====")
    for e in body:
        if e[0].text is not None:#<source>
            s=innercontent(e[0])
            arr=removeTags(s)
            for t in arr:
                sources.add(t)
                
#    # Creating other with uno IGNORABA CAMPOS PERO NO BUSCABA BIEN
#    debug ("ADDING WITH UNOGENERATOR")
#    oText = doc.document.Text
#    ParEnum = oText.createEnumeration()
#    while ParEnum.hasMoreElements():
#        P = ParEnum.nextElement()
#        if P.supportsService("com.sun.star.text.Paragraph"):
#            debug(P.String)
#            if P.String!="":
#                sources.add (P.String)
#        if P.supportsService("com.sun.star.text.TextTable"):
#            cellNames = P.getCellNames
#            for Name in cellNames:
#                Cell = P.getCellByName(Name)
#                if Cell.String!="":
#                    sources.add (Cell.String)
                
    for s in undetected_strings:
        sources.add(s)
    sources=list(sources)
    sources.sort()
    sources= sorted(sources, key = len, reverse=True)
    if path.exists(original_xlf) is True:
        remove(original_xlf)
    
    # Creating pot file
    file_pot = POFile()
    file_pot.metadata = {
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
        entry = POEntry(
            msgid=source,
            msgstr='', 
            occurrences=[('string', str(i)),]
        )
        file_pot.append(entry)
    file_pot.save(pot)
    
    #Merging pot with out po file
    if path.exists(po)==False:
        run_check(["msginit", "-i", pot,  "-o", po])
    run_check(["msgmerge","-N", "--no-wrap","-U", po, pot])
    
    #Creating our translated output
    debug ("==== WRITING TO ODT ====")
    file_po = pofile(po)
    for entry in file_po:
        if fake is True:
            msgstr="Fake"
        else:
            msgstr=entry.msgstr
        if msgstr != "":
            debug(f"'{entry.msgid}' ==> '{msgstr}'")
            doc.findall_and_replace(entry.msgid,  msgstr)
            
    doc.save(output)
    if pdf is True:
        doc.export_pdf(output+".pdf")
    doc.close()
    print(f"{len(sources)} messages found. {len(file_po.translated_entries())} translated. {len(file_po.untranslated_entries())} untranslated.")


# Hola <lkjlklk> Adios
def removeTags(text):
    r=[]
    numopens=0
    string_=""
    for c in text:
        if c=="<":
            if numopens==0:
                if string_!="":
                    r.append(string_)
                string_=""
            numopens=numopens+1
        elif c==">":
            numopens=numopens-1
        else:
            if numopens==0:
                string_=string_+c
    if string_!="":
        r.append(string_)
    debug(f"{text} <==> {str(r)}")
    return r
            
def main_po():
    parser=ArgumentParser(prog='translate_odf', description=_('Translate ODF files with XLF formats'), epilog=argparse_epilog(), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--debug', help="Debug program information", choices=["DEBUG","INFO","WARNING","ERROR","CRITICAL"], default="ERROR")

    parser.add_argument('--from_language', action='store', help=_('Language to translate from. Example codes: es, fr, en, md'), required=True, metavar="CODE")
    parser.add_argument('--to_language', action='store', help=_('Language to translate to. Example codes: es, fr, en, md'), required=True,  metavar="CODE")
    parser.add_argument('--input', action='store', help=_('File to translate'), required=True,  metavar="FILE")
    parser.add_argument('--output', action='store', help=_('Path where translated file is going to be generated. If missing add tranlation code before name extension'), default=None,  metavar="FILE")
    parser.add_argument('--po', action='store', help=_('Catalogue with strings to translate in XLIFF format'), default=None,  metavar="FILE")
    parser.add_argument('--pot', action='store', help=_('Generate pot file'), default=None,  metavar="FILE")
    parser.add_argument('--pdf', action='store_true', help=_('Generate output in pdf too'), default=False)
    parser.add_argument('--undetected', action='append', help=_('Undetected strings to apped to translation'), default=[])
    parser.add_argument('--fake', action='store_true', help=_('Sets fake to all strings'), default=False)
    args=parser.parse_args()
    addDebugSystem(args.debug)
    
    command_main_po(args.from_language, args.to_language, args.input, args.output, args.po, args.pot, args.pdf, args.undetected, args.fake)
