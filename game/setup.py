from distutils.core import setup
import py2exe
import glob


setup(windows=['pybreakout.py'],
      data_files=[("resources/fonts",glob.glob("resources/fonts/*.TTF")),
                  ("resources/images",glob.glob("resources/images/*.png")),
                  ("resources/sounds",glob.glob("resources/sounds/*.wav")),
                  ("resources/levels",glob.glob("resources/levels/*.dat"))
])