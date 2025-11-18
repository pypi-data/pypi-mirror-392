# Ratisbona Shellutils

This project comprises a set of small utilities that are intended to be used as usefuls tools in a well equipped 
shell environment.

The following utilities are available as ratisbona_... commands:

calendar:   
      A package that contains ratisbona_gcalendar, a command line interface that can sync git logs to google calendar,
      list calendars, list events, enter events, sync all commit dates of a gitlog into a google-calendar
      or sync the date of files the names of which are to start out by an iso-date to a google-calendar.
  
labeldisks:   
      This modules scans for hard drives and gathers the logical volumes they contain
      and the contents of the mount points if they are mounted.
      It can be used to print out labels for those hard drives, which is very handy, as soon as you have
      docking bays with multiple hard drives in them or as soon as you take your server apart.
  
file_organisation:   
      A Module with helpers to keep your files organized.
      It can apply a set of cleaners to your filenames to make them more readable.
      Files are not changed directly but a script is output that can be reviewed and used to rename the files.

dialogator:   
      A set of tools revolving around the so called dialoge markdown.
      Dialog markdown is simply a markdown format, that is used to record dialogs.
      The only conventions are, that first-level headings are Dates at wich conversations take place and
      second level headings are the names of the speakers.
      
      Utilities exist to convert several dialog formats like:
          - exported whatsapp conversations
          - exported chat-gpt dialogs
      to dialog markdown.
      
      There is also an intricate typeset function that can translate dialog-markdown to a latex typesetted pdf.
      It supports lots of markdown features like:
      - text formatting
      - code blocks with syntax-highlighting
      - images
      - links
      - math
      - and even tables!
  
paste_image:   
      Utility to retrieve an image from the clipboard. It saves it as a png file to the current directory using a
      datetime-based filename. The filename is printed to stdout. 
      The script can be very useful for example for copy and pasting images into VI.
      In VI you can use the command `:r !paste_image` to save the image and paste the filename from the clipboard 
      into the current buffer.
  
cli:   from ._cli import blue_dosboxpiper:   
      A collection of utilities to be used as a filter in your posix pipes.
      
      Currently there is just a utility to transliterate unicode characters to ascii.
  
project_starter:   
      Replacement for the withdrawn project starter script.
      This script simply outputs the shellcommand to check out the new project template from git.
  
twister:   
      This module contains a mouse wiggler to keep your computer hard from going into standby.


## Project-structure, Installing Dependencies and PYTHONPATH configuration.

This Project houses it's sources below the `src/{projectname}` directory. You have
to have this directory in your module-searchpath to execute the project. It should also
be present in the module-searchpath of your IDE.

If using pycharm or any other Jetbrains-based IDE, use 
`Settings->Project->Project Structure`
to `mark as sourcefolder` the `src`-folder of this.

The Project requirements, as well as the dev-requirements are intended to be listed in the 
`pyproject.toml`-file (see there)

By issuing:

```shell
pip install -e .
```

you add all the project dependencies as well as the projects sourcefolder to your 
[hopefully virtual!] environment, relieving you of the burden of having to manually 
installing anything or having to configure your python path by other means.

Likewise you can install all the dev-dependencies by:

```shell
pip install -e .'[dev]'
```

