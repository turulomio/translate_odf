from datetime import datetime

__versiondatetime__ = datetime(2020, 9, 9)
__versiondate__=__versiondatetime__.date()
__version__ = '0.1.0'


try:
    t=translation('translate_odf',resource_filename("translate_odf","locale"))
    _=t.gettext
except:
    _=str

## Function used in argparse_epilog
## @return String
def argparse_epilog():
    return _("Developed by Mariano Muñoz 2020-{}").format(__versiondate__.year)