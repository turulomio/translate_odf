# Translate_ODF project

## About

Frontend of xliff2odf and odf2xliff to translate easily odf documents

## Usage:

`translate_odf --from es --to en --file_from yourfile.odt`

This will generate an xlf file with the catalog to translate in XLIFF format

Edit it with "lokalize" for example and rerun that command

A file called yourfile.odt.en.odt will be generated in english

;)

## Installation

If you use Gentoo, you can find the ebuild in https://github.com/turulomio/myportage/tree/master/app-office/translate_odf

For other Linux and Windows for your python installation

`pip install translate_odf`

## Links

- Doxygen documentation: http://turulomio.users.sourceforge.net/doxygen/translate_odf/
- Pypi web page: https://pypi.org/project/translate_odf/

## Changelog

### 0.1.0 (2020-09-09)

- Basic functionality.
