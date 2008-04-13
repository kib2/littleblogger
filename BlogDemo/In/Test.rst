.. [tit]Mon titre ici[/tit]
.. [date]2007 9 23 13 41[/date]
.. [tags]LaTeX,Python,Lisp,Blog[/tags]


Un petit test de poste dans ``LittleBlogger``.

.. sourcecode:: python

    for block in blocks(sys.stdin):
    
    block = re.sub(r'\*\*(.+?)\*\*', r'<str>\1</str>', block)
    block = re.sub(r'\*(.+?)\*', r'<em>\1</em>', block)
    
    if title:
        print '<h1>'
        print block
        print '</h1>'
        title = 0
    else:
        print '<p>'
        print block
        print '</p>'

Ca marche ?
