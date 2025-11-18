"""
    Utility to retrieve an image from the clipboard. It saves it as a png file to the current directory using a
    datetime-based filename. The filename is printed to stdout. 
    The script can be very useful for example for copy and pasting images into VI.
    In VI you can use the command `:r !paste_image` to save the image and paste the filename from the clipboard 
    into the current buffer.
"""
