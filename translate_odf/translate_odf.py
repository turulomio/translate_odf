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
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--log', action="store_true",  help="Generates a log", default=False)
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
            
def main_generate_po():
    parser=ArgumentParser(prog='translate_odf', description=_('Generate a po and pot file from ODF'), epilog=argparse_epilog(), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--from_language', action='store', help=_('Language to translate from. Example codes: es, fr, en, md'), required=True, metavar="CODE")
    parser.add_argument('--to_language', action='store', help=_('Language to translate to. Example codes: es, fr, en, md'), required=True,  metavar="CODE")
    parser.add_argument('--input', action='store', help=_('File to translate'), required=True,  metavar="FILE")
    parser.add_argument('--po', action='store', help=_('Catalogue with strings to translate in XLIFF format'), default=None,  metavar="FILE")
    parser.add_argument('--pot', action='store', help=_('Generate pot file'), default=None,  metavar="FILE")
    parser.add_argument('--undetected', action='append', help=_('Undetected strings to apped to translation'), default=[])
    args=parser.parse_args()
    
    command_generate_po(args.from_language, args.to_language, args.input, args.po, args.pot, args.undetected)


def command_generate_po(from_language, to_language, input, po=None, pot=None, undetected_strings=[]):   
    
    def same_entries_to_ocurrences(l):
        l= sorted(l, key=lambda x: (x[1], x[2]))
        r=[]
        for type, number,  position,  text in l:
            r.append((type, f"{number}#{position}"))
        return r
        
        ##########################
        
    if po is None:
        po=f"{input}.{to_language}.po"
    if pot is None:
        pot=f"{input}.{to_language}.pot"
    # Creating pot file
    doc=ODT(input)

    #Paragraph
    entries=[]#List of ("type", numero, posicion) type=Paragraph, numero=numero parrafo y posición orden dentro del parrafo
    set_strings=set()
    enumeration = doc.cursor.Text.createEnumeration()
    for i,  par in enumerate(enumeration):
        position=0
        if  par.supportsService("com.sun.star.text.Paragraph") :
#            for position, element in par.createEnumeration():
#                print(par, dir(element))
                text_=par.getString()
                if text_ !="":
                    entries.append(("Paragraph",  i,  position, text_))
                    set_strings.add(text_)
#                print(par, dir(par))
                for i in doc.document.getTextSections():
                    print (i.getString())
                for i in doc.document.getRedlines():
                    print (i,  dir(i), i.getString())
#        print(text_, par.hasElements(), par.getElementType(), par.getTypes())
    doc.close()
    
    
        
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
    for s in set_strings:
        same_entries=[] #Join seame text entries
        for type, number, position, string_ in entries:
            if string_==s:
                same_entries.append((type, number, position, string_))

        entry = POEntry(
            msgid=s,
            msgstr='', 
            occurrences=same_entries_to_ocurrences(same_entries)
        )
        file_pot.append(entry)
    file_pot.save(pot)
    
    #Merging pot with out po file
    if path.exists(po)==False:
        run_check(["msginit", "-i", pot,  "-o", po])
    run_check(["msgmerge","-N", "--no-wrap","-U", po, pot])
    


def command_main_po(from_language, to_language, input, output=None, po=None, pot=None, pdf=False, undetected_strings=[], fake=None):
    extension=input.split(".")[1:][0]

    if output is None:
        output=f"{input}.{to_language}.{extension}"
    if po is None:
        po=f"{input}.{to_language}.po"
    if pot is None:
        pot=f"{input}.{to_language}.pot"
        
    logfile=f"{output}.log"
    log=open(logfile, "w")


    s=_(f"Translating '{input}' from '{from_language }' to '{to_language}'")
    print(s)
    log.write(s+"\n")
    s=_(f"  - Output: {output}")
    print(s)
    log.write(s+"\n")
    s=_(f"  - File catalog pot: {pot}")
    print(s)
    log.write(s+"\n")
    s=_(f"  - File catalog po: {po}")
    print(s)
    log.write(s+"\n")
    s=_(f"  - Translation log: {logfile}")
    print(s)
    log.write(s+"\n")
    
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
    for e in body:
        if e[0].text is not None:#<source>
            s=innercontent(e[0])
            arr=removeTags(s)
            for t in arr:
                sources.add(t)
                
    for s in undetected_strings:
        sources.add(s)
    sources=list(sources)

    
    
    
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
    
    # Creates a dictionary of translations
    dict_po={}
    file_po = pofile(po)
    for i, entry in enumerate(file_po):
        if fake is True:
            dict_po[entry.msgid]=f"{{{entry.msgid}}}"
        else:
            if entry.msgstr == "":
                dict_po[entry.msgid]=entry.msgid
            else:
                dict_po[entry.msgid]=entry.msgstr
        
    #Converts sources to entries (list of tuples)
    entries=[]
    for source in sources:
        entries.append((source, dict_po[source] ))
    entries=sorted(entries,  key=lambda item: len(item[0]), reverse=True)
    
    
    #Creating our translated output
    log.write ("\n\n==== TRANSLATION LOGS ====\n")
    warns=""
    for i, (find, replace) in enumerate(entries):
        number=doc.findall_and_replace(find,  replace)
        rs=replaced_entries_before(find,  i,  entries)
        s=f"""
* Entry {i}

    Original: {find}

    Translation set {number} times: {replace}
"""
        log.write(s)
        if len(rs)>0:
            warns=warns + s +"    WARNING: This replacement could overwrite before replacements. Perhaps you'll need to overwrite your result later with unogenerator.\n"
            for s in rs:
                warns =warns + f"        - '{s[0]}' ==> '{s[1]}'\n"
                
    if warns!="":
        log.write ("\n\n==== WARNINGS ====\n")
        log.write(warns)
            
    doc.save(output)
    if pdf is True:
        doc.export_pdf(output+".pdf")
    doc.close()
    print(f"{len(sources)} messages found. {len(file_po.translated_entries())} translated. {len(file_po.untranslated_entries())} untranslated.")
    
    log.close()

## Returns if a find entries is contained in any string of list sources replacements
def replaced_entries_before(s,  index,  entries):
    r=[]
    if index==0:
        return r

    for find,  replace in entries[0:index-1]:
        if s in replace:
            r.append((find, replace))
    return r

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
    return r
            
def main_po():
    parser=ArgumentParser(prog='translate_odf', description=_('Translate ODF files with XLF formats'), epilog=argparse_epilog(), formatter_class=RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--log', action="store_true",  help="Generates a log", default=False)
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
    
    command_main_po(args.from_language, args.to_language, args.input, args.output, args.po, args.pot, args.pdf, args.undetected, args.fake)
