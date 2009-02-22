In short:

* Create restructured text files, one per manual.

* Use the keyword role to mark keywords. For example::

    This is an :keyword:`important place`

  If you intend to use keywords, define the keyword role at the beginning of your doc::

    .. role:: keyword

* Call rst2qhc like this (of course, with the right namespace, and other arguments as needed)::

    python rst2qhc.py example.txt -o out --namespace urssus \
    --filterattributes urssus:0.2.13 \
    --rst2htmlopts="--stylesheet=mystyle.css"

To see the accepted arguments, do::

  python rst2qhc --help

KNOWN BUGS: the .qhpc file doesn't work, if anyone can give a hand, that's nice.
