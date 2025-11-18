import sys

import click

from ratisbona_utils.boxdrawing import blue_dosbox
from ratisbona_utils.io import errprint


@click.command
def project_starter_cli():
    errprint(blue_dosbox("Project Starter"))
    errprint()
    errprint("Ratisbona Project starter now is simply a template-project with a rename.py script,")
    errprint("that can change the package name and the project name in all files.")
    errprint()
    errprint("Therefore please execute this command:")
    errprint()
    print("git clone git://git.code.sf.net/p/ratisbona-template-project/code <your_new_project_name>")
    errprint()
    errprint()
