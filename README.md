# Translate_ODF project

## About

Frontend of xliff2odf and odf2xliff to translate easily odf documents

## Usage:

### translate_odf2xlf

`translate_odf --from_language es --to_language en --input yourfile.odt`

This will generate an xlf file with the catalog to translate in XLIFF format

Edit it with "lokalize" for example and rerun that command

A file called yourfile.odt.en.odt will be generated in english

;)

Known issues:

- `translate_odf2xlf` doesn't detect all strings and sets a lot of internal and ugly codes, due to odf2xliff command limitations, that's the reason I'm developing `translate_odf2po`


### translate_odf2po

`translate_odf2po --from_language es --to_language en --input yourfile.odt`

This will generate one gettext .pot and one .po files. 

Edit it with "lokalize" for example and rerun that command

A file called `yourfile.odt.en.odt` will be generated in english

;)

You can use --fake to do a simulation of detected strings

If some string is not detected you can use --undetected 

Known issues:

- `translate_odf2po` detects more strings than `translate_odf2xlf` and removes internal codes, buy it doesn't detect strings positions. So it uses a findall_and_replace command. Sometimes you'll need to update your translated files with unogenerator manually.


## Known issues



## Installation

If you use Gentoo, you can find the ebuild in https://github.com/turulomio/myportage/tree/master/app-office/translate_odf

For other Linux and Windows for your python installation

`pip install translate_odf`

## Links

- Doxygen documentation: http://turulomio.users.sourceforge.net/doxygen/translate_odf/
- Pypi web page: https://pypi.org/project/translate_odf/
- Github web page: https://github.com/turulomio/translate_odf/

## Changelog

### 0.3.0
- Added basic support to translate_odf2po.

### 0.2.0

- Removed strange error code, seems it's not necessary anymore
- Improving command arguments 

### 0.1.0 (2020-09-09)

- Basic functionality.
