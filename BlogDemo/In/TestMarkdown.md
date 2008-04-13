[tit]Test de Markdown[/tit]
[date]2007 12 12 15 6[/date]
[tags]Python,Markup[/tags]
[markup]markdown[/markup]

Les langages de Markup comme [reStructuredText][2] et [Markdown][1]

On peut aussi bien sûr y placer des bouts de code colorisés, comme ceci :

    #!python
    def addActions(self):
        """Add all the possible actions to
        the BlogMenu

        - Publish this post
        - Remove a post
        """
        newPost = QtGui.QAction(self.parent)
        newPost.setText("publish")
        self.menuBlog.addAction(newPost)
        self.parent.connect(newPost,QtCore.SIGNAL("triggered()"),self.bm.publish)

        removePost = QtGui.QAction(self.parent)
        removePost.setText("transfert by FTP")
        self.menuBlog.addAction(removePost)
        self.parent.connect(removePost,QtCore.SIGNAL("triggered()"),self.bm.transferToFtp)

[1]: http://daringfireball.net/projects/markdown        "Markdown"
[2]: http://docutils.sourceforge.net/rst.html           "reStructuredText"
