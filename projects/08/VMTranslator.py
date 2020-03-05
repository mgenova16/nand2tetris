#!/usr/bin/env python3

import sys
from pathlib import Path

from vm_translator import Translator


def main():
    try:
        p = Path(sys.argv[1])
        translator = Translator(p)
    except IndexError:
        print(f'Usage: {sys.argv[0]} <vm file or directory>')
        sys.exit(1)

    translator.translate_all()


if __name__ == '__main__':
    main()
