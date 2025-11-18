import re
from collections import namedtuple
from datetime import datetime


def mangleLine(line):
    # HTTP-Links https://www.diskpart.com/articles/format-2tb-hard-drive-to-fat32-7201.html
    line = re.sub(r'(https?://[^ \n]+)', r'[\1](\1)', line)
    return line


Speak = namedtuple('Speak', ['dtime', 'name', 'text'])


def try_parse_english_line(line):
    expression = r"([0-9]{1,2})/([0-9]{1,2})/([0-9]{1,4}), ([0-9]{1,2}):([0-9]{1,2}) - ([^:]+): (.+)"

    match = re.match(expression, line)
    if not match:
        #print(f"{expression} does not match {line}", file=sys.stderr)
        return None

    month = int(match[1])
    day = int(match[2])
    year = int(match[3])
    year = year + 2000 if year < 100 else year
    hours = int(match[4])
    minutes = int(match[5])
    name = match[6]
    text = match[7]

    dtime = datetime(year, month, day, hours, minutes)
    return Speak(dtime, name, text)


def parse_date_line(line):
    match = re.match(
        r'([0-9]{1,2})\.([0-9]{1,2})\.([(0-9]{2}), '
        + r'([0-9]{1,2}):([0-9]{1,2}) - ([^:]+): (.+)',
        line
    )
    if not match:
        return try_parse_english_line(line)
    dtime = datetime(
        2000 + int(match[3]),
        int(match[2]),
        int(match[1]),
        int(match[4]),
        int(match[5])
    )
    return Speak(dtime, match[6], match[7])


def whatsapp_zip_to_dialog_md(infile, outfile):
    olddate = None
    oldspeak = None
    for line in infile:
        speak = parse_date_line(line)
        if speak is None and oldspeak is not None:
            oldspeak = Speak(
                oldspeak.dtime, oldspeak.name, oldspeak.text + mangleLine(line)
            )
        else:
            if oldspeak is not None:
                if oldspeak.dtime.date() != olddate:
                    print(
                        f'# {oldspeak.dtime.year}-{oldspeak.dtime.month:02d}-{oldspeak.dtime.day:02d}\n',
                        file=outfile
                    )
                    olddate = oldspeak.dtime.date()

                the_text = oldspeak.text.replace('\n', '\n\n')
                the_text = re.sub(r'(IMG-[0-9]+-WA[0-9]+\.jpg)', r'\n![](\1)\n\n', the_text)
                the_text = re.sub(r'(VID-[0-9]+-WA[0-9]+\.mp4)', r'\n[\1](\1)\n', the_text)
                the_text = mangleLine(the_text)
                print(
                    f'## {oldspeak.name}, {oldspeak.dtime.hour:02d}:{oldspeak.dtime.minute:02d}\n\n{the_text}\n',
                    file=outfile
                )
            oldspeak = speak
    if oldspeak is not None:
        if oldspeak.dtime.date() != olddate:
            print(
                f'# {oldspeak.dtime.year}-{oldspeak.dtime.month:02d}-{oldspeak.dtime.day:02d}\n',
                file=outfile
            )

        the_text = oldspeak.text.replace('\n', '\n\n')
        the_text = re.sub(r'(IMG-[0-9]+-WA[0-9]+\.jpg)', r'\n![](\1)\n', the_text)
        the_text = re.sub(r'(VID-[0-9]+-WA[0-9]+\.mp4)', r'\n[\1](\1)\n', the_text)
        the_text = mangleLine(the_text)
        print(
            f'## {oldspeak.name}, {oldspeak.dtime.hour:02d}:{oldspeak.dtime.minute:02d}\n\n{the_text}\n',
            file=outfile
        )