from datetime import datetime
from gettext import translation
from pkg_resources import resource_filename

__versiondatetime__ = datetime(2021, 11, 9, 19, 24)
__versiondate__=__versiondatetime__.date()
__version__ = '0.3.0'

try:
    t=translation('translate_odf',resource_filename("translate_odf","locale"))
    _=t.gettext
except:
    _=str

## Function used in argparse_epilog
## @return String
def argparse_epilog():
    s=""
    s=s+_("To translate xlf files you can use Lokalize open source tool, which you can find it in most Linux distributions.")
    s=s+"\n"
    s=s+_("Windows users can download it from https://binary-factory.kde.org/job/Lokalize_Release_win64/")
    s=s+"\n"
    s=s+"\n"
    s=s+ _("Developed by Mariano Muñoz 2020-{}").format(__versiondate__.year)
    
    return s
