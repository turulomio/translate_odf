from setuptools import setup, Command
import site
import os
import platform



## Class to define doc command
class Doc(Command):
    description = "Update translations"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        #es
        os.system("xgettext -L Python --no-wrap --no-location --from-code='UTF-8' -o locale/translate_odf.pot *.py translate_odf/*.py")
        os.system("msgmerge -N --no-wrap -U locale/es.po locale/translate_odf.pot")
        os.system("msgfmt -cv -o translate_odf/locale/es/LC_MESSAGES/translate_odf.mo locale/es.po")

class Procedure(Command):
    description = "Show release procedure"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("""Nueva versión:
  * Cambiar la versión y la fecha en version.py
  * Modificar el Changelog en README
  * python setup.py doc
  * Update locale/*.po
  * python setup.py doc
  * python setup.py install
  * python setup.py doxygen
  * git commit -a -m 'translate_odf-{0}'
  * git push
  * Hacer un nuevo tag en GitHub
  * python setup.py sdist
  * twine upload dist/translate_odf-{0}.tar.gz 
  * python setup.py uninstall
  * Crea un nuevo ebuild de Gentoo con la nueva versión
  * Subelo al repositorio del portage
""".format(__version__))

## Class to define doxygen command
class Doxygen(Command):
    description = "Create/update doxygen documentation in doc/html"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print("Creating Doxygen Documentation")
        os.system("""sed -i -e "41d" doc/Doxyfile""")#Delete line 41
        os.system("""sed -i -e "41iPROJECT_NUMBER         = {}" doc/Doxyfile""".format(__version__))#Insert line 41
        os.system("rm -Rf build")
        os.chdir("doc")
        os.system("doxygen Doxyfile")
        os.system("rsync -avzP -e 'ssh -l turulomio' html/ frs.sourceforge.net:/home/users/t/tu/turulomio/userweb/htdocs/doxygen/translate_odf/ --delete-after")
        os.chdir("..")

## Class to define uninstall command
class Uninstall(Command):
    description = "Uninstall installed files with install"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if platform.system()=="Linux":
            os.system("rm -Rf {}/translate_odf*".format(site.getsitepackages()[0]))
            os.system("rm /usr/bin/translate_odf*")
        else:
            os.system("pip uninstall translate_odf")

########################################################################


## Version of modele captured from version to avoid problems with package dependencies
__version__= None
with open('translate_odf/version.py', encoding='utf-8') as f:
    for line in f.readlines():
        if line.find("__version__ =")!=-1:
            __version__=line.split("'")[1]


setup(name='translate_odf',
     version=__version__,
     description='Command to translate Libreoffice ODF files with odf2xliff',
     long_description='Project web page is in https://github.com/turulomio/translate_odf',
     long_description_content_type='text/markdown',
     classifiers=['Development Status :: 4 - Beta',
                  'Intended Audience :: Developers',
                  'Topic :: Software Development :: Build Tools',
                  'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                  'Programming Language :: Python :: 3',
                 ], 
     keywords='translate odf odt ods odp libreoffice',
     url='https://github.com/turulomio/translate_odf',
     author='Turulomio',
     author_email='turulomio@yahoo.es',
     license='GPL-3',
     packages=['translate_odf'],
     install_requires=['translate-toolkit', 'polib'],
     entry_points = {'console_scripts': [
                                           'translate_odf2xlf=translate_odf.translate_odf:main_xlf',
                                           'translate_odf2po=translate_odf.translate_odf:main_po',
                                           'translate_odf_generatepo=translate_odf.translate_odf:main_generate_po',
                                        ],
                    },
     cmdclass={'doxygen': Doxygen,
               'uninstall':Uninstall, 
               'doc': Doc,
               'procedure': Procedure,
              },
     zip_safe=False,
     include_package_data=True
)
