from pynput.keyboard import Key, Controller
import subprocess
import time

# Mapping für typische Sonderzeichen auf deutschem Layout
# char → (taste auf deutscher tastatur, ggf. Modifier)
SPECIAL_CHARS = {
    '\n': (Key.enter, None),
    '!': ('1', Key.shift_l),
    '"': ('2', Key.shift_l),
    '§': ('3', Key.shift_l),
    '$': ('4', Key.shift_l),
    '%': ('5', Key.shift_l),
    '&': ('6', Key.shift_l),
    '/': ('7', Key.shift_l),
    '(': ('8', Key.shift_l),
    ')': ('9', Key.shift_l),
    '=': ('0', Key.shift_l),
    '?': ('ß', Key.shift_l),
    '*': ('+', Key.shift_l),
    '+': ('+', None),
    '-': ('-', None),
    '_': ('-', Key.shift_l),
    ':': ('.', Key.shift_l),
    ';': (',', Key.shift_l),
    '@': ('q', Key.alt_gr),
    '{': ('7', Key.alt_gr),
    '[': ('8', Key.alt_gr),
    ']': ('9', Key.alt_gr),
    '}': ('0', Key.alt_gr),
    '<': ('<', None),
    '>': ('<', Key.shift_l),
    '\\': ('ß', Key.alt_gr),
    '^': ('^', None),
    '€': ('e', Key.alt_gr),
    '`': ('^', None),
    '~': ('+', Key.alt_gr),
    "'": ('#', None),
    '#': ('#', Key.shift_l),
}

keyboard = Controller()



def escape_char_for_osascript(char: str) -> str:
    """
    Escape problematische Zeichen für AppleScript keystroke.
    """
    replacements = {
        '"': '\\"',
        '\\': '\\\\',
    }
    return replacements.get(char, char)

def type_text_osascript(text: str, delay: float = 0.05):
    """
    Tippt Text auf macOS zuverlässig über AppleScript (osascript).
    Shift & Sonderzeichen werden korrekt erkannt.
    """
    for char in text:
        if char == '\n':
            script = 'tell application "System Events" to key code 36'  # Return
        elif char == '\t':
            script = 'tell application "System Events" to key code 48'  # Tab
        else:
            escaped = escape_char_for_osascript(char)
            script = f'tell application "System Events" to keystroke "{escaped}"'

        subprocess.run(["osascript", "-e", script])
        time.sleep(delay)


def type_text_pynput(text, delay=0.1):
    """
    Tippt den gegebenen Text systemweit über pynput.
    Shift wird automatisch gedrückt, wenn nötig.
    """
    for char in text:
        if char in SPECIAL_CHARS:
            # Sonderzeichen, für die wir Shift oder andere Modifier brauchen
            key, modifier = SPECIAL_CHARS[char]
            if modifier:
                keyboard.press(modifier)
                time.sleep(0.1)  # kurz warten, damit Modifier wirklich aktiv ist
                keyboard.press(key)
                keyboard.release(key)
                keyboard.release(modifier)
                print(f"Typing {repr(char)} as key={repr(key)}, modifier={modifier}")
            else:
                keyboard.press(key)
                keyboard.release(key)
        elif char.isupper():
            # Großbuchstaben => Shift gedrückt halten
            with keyboard.pressed(Key.shift):
                keyboard.press(char.lower())
                keyboard.release(char.lower())
        else:
            keyboard.press(char)
            keyboard.release(char)

        time.sleep(delay)


