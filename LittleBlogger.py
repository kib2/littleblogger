#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""LittleBlogger is just a small Python app for writting a static blog:

- you give it an 'In/' directory containing you posts written in some markup
  languages (supported are : reSt, Markdown).

  The first 4 lines of each post file will be parsed as they contain each
  post:

  *  [tit] Post Title [/tit]
  *  [date] Post Date (year month day hour minute)[/date]
  *  [tags] Post Tags [/tags]
  *  [markup] Post Markup Language [/markup]

- transfert its contents to FTP;

"""

import os
import glob
import codecs
import re
import datetime
import md5
from time import localtime, strftime
import itertools

## For Configuration file : ConfigParser
import ConfigParser

## For RSS generation : RSS2Gen
import PyRSS2Gen

## For Highligtning code : pygments
import RegisterPygment

## docutils
from docutils.core import publish_parts

## markdown
try:
    import markdown
except ImportError:
    raise ImportError, 'This plugins requires the Python markdown package.'

## mako templates
from mako.template import Template
from mako.lookup import TemplateLookup

## FTP support
from ftplib import FTP
from FtpUpload import FtpUpload

## ----- blogManager --------------------------------------------------------
class blogManager(object):
    """Class is used to manage the Blog Posts.

    - Retrieves all the posts from a given directory
    - Parse them one by one and then build a tags list
      from (avoiding doubles).
    """
    def __init__(self, postdir = '',parent=None):
        self.parent = parent
        
        ## Added on April,10 2008
        ## Archive managing
        ## self.archives[2007] returns all posts from year 2007
        self.archives = {}
        self.monthsNames = {
        1:"Janvier",  2:"Février",  3:"Mars",  4:"Avril",
        5:"Mai",  6:"Juin",  7:"Juillet",  8:"Aôut",
        9:"Septembre", 10:"Octobre", 11:"Novembre", 12:"Décembre",
        }

        self.postdir = postdir
        # the following line will setup
        # self._in, self._out, self._static , self._templates
        self.getInOutDirs() 

        self.blogFiles = os.listdir(self._in)
        print "self.blogFiles = ",self.blogFiles
        self.util()
        self.getPostListAndIds()

    ## Added on April,10 2008
    def getArchives(self):
        for k, g in itertools.groupby(self.all_posts, lambda p:p.postdate.year):
            self.archives[k] = list(g)
        return self.archives

    def util(self):
        """Prints on screen the blog times
        
        just for debugging purpose
        """
        for bf in self.blogFiles :
            f = self.postdir +'/In/%s'%(bf)
            tlm = os.path.getmtime(f)
            tlml = localtime(tlm)
            print strftime('%m%d%y_%H%M%S', tlml)
            print datetime.datetime.now()

    def readConf(self):
        """Read the blog's configuration file
        """
        config = ConfigParser.RawConfigParser()
        try:
            config.read(os.path.join(self.postdir,'blog.conf'))
        except:
            print "You don't have a blog.conf file inside your Blog directory."
            return

        aw = "Away"
        away   = config.get(aw, 'BlogHomePage')
        host   = config.get(aw, 'Host')
        user   = config.get(aw, 'User')
        passw  = config.get(aw, 'Password')
        remote = config.get(aw, 'RemoteDir')
        
        ## the blog's dictionnary
        bg = "Blog"
        self.blog_dic_names = {
        "blog_name" : config.get(bg, 'Name'),
        }
        print "\nBlog Dictionnary names : %s \n"%(str(self.blog_dic_names))
        return away,host,user,passw,remote

    def changePostDir(self, other_postdir):
        """Some methods for changing the current Blog directory
        """
        self.posts_list = []
        self.postdir = other_postdir
        self.getInOutDirs()
        self.blogFiles = os.listdir(self._in)
        self.getPostListAndIds()

    def getPostListAndIds(self):
        self.posts_list = self.getPosts()
        for i,p in enumerate(self.getPostByDate(self.posts_list,rev=False)) :
            p.realid = i

    def getInOutDirs(self):
        """In, Out and Templates directories setup
        """
        self._in = os.path.join(self.postdir,'In/')
        self._out = os.path.join(self.postdir,'Out/')
        self._static = os.path.join(self.postdir,'Static/')
        self._templates = os.path.join(self.postdir,'Templates/')

    def getPosts(self):
        """Posts retrieving
        Return the Posts list by date
        """
        posts = []
        for thePost in self.blogFiles:
            posts.append(Post(thePost, self))
            
        self.all_posts = self.getPostByDate(posts)
        return self.all_posts

    def getPostByDate(self, postslist, rev=True):
        """Sort a given postlist according to
        their postDate.
        
        @rev -> reversed postlist is True or False
        
        It is not used directly, but called from self.getPosts
        """
        def keyDate(elt):
            return elt.postdate
        return sorted(postslist,key=keyDate,reverse=rev)

    def addPost(self,post):
        """Add/Sub Posts [Never used for the moment]
        """
        if post not in self.posts_list :
            self.posts_list.append(post)

    def removePost(self,post):
        """Remove a given Post from self.posts_list
        """
        if post not in self.posts_list :
            raise noExitingPostError(post)
        else:
            self.posts_list.remove(post)

    ## Rendering methods
    def render(self):
        """Save all the Posts to HTML according to the
        given templates wirtten in Mako.
        """
        for post in self.posts_list:
            print '\nsaving post %s\n'%(post.title.encode('utf-8'))
            post.saveWithMako()

    def publish(self):
        print 'publishing your Blog in dir%s'%(self.postdir)
        for p in self.posts_list :
            p.getInfos()
            
        print "Rendering of posts..."
        self.render()
        print "Creating the index..."
        self.buildIndex()
        print "Creating the tags..."
        self.builTaggedPages()
        print self.tags
        print "Creating the static pages..."
        self.buildStaticPages()
        print "Creating the RSS..."
        self.buildRss()
        
        self.builArchivedPages()

    def buildIndex(self):
        """Build the index Page of the blog.
        The number of viewed Posts on this page is
        set inside the Mako template.
        """

        # setup the mako template
        mylookup = TemplateLookup(directories=["/"])
        my_tpl = Template(  filename = \
                            os.path.join(self._templates, 'Index.mako'),
                            lookup = mylookup,
                            input_encoding = 'utf-8',
                            output_encoding = 'utf-8')

        f = file(os.path.join(self._out,'index.html'),'w')
        

        #f.write(my_tpl.render(  bm = truc,))
        f.write(my_tpl.render(  articles  = self.posts_list, 
                                tags      = self.tags, 
                                archive   = self.getArchives(),
                                noms_mois = self.monthsNames, ))
        f.close()

    def builArchivedPages(self):
        for annee in self.getArchives().keys():
            groupes = itertools.groupby(self.archives[annee], lambda p:p.postdate.month)
            for k,g in groupes :
                # setup the mako template
                mylookup = TemplateLookup(directories=['/'])
                my_tpl = Template(  filename=os.path.join \
                                    (self._templates,'Archived.mako'),
                                    lookup=mylookup,
                                    input_encoding='utf-8',
                                    output_encoding='utf-8')

                f = open( os.path.join(self._out, "%s_%s.html"%(k,annee) ), "w" )
                f.write(my_tpl.render(  mois="%s %s"%(self.monthsNames[int(k)].decode('utf-8'),annee),
                                        billets = list(g),
                                        articles = self.posts_list,
                                        tags = self.tags))
                f.close()

    def builTaggedPages(self):
        """Construct all the tagged pages according to
        the 'Tagged.mako' file template 
        """
        for t in self.tags :

            post_list = t.get_posts
            
            # setup the mako template
            mylookup = TemplateLookup(directories=[''])
            my_tpl = Template(  filename=os.path.join \
                                (self._templates,'Tagged.mako'),
                                lookup=mylookup,
                                input_encoding='utf-8',
                                output_encoding='utf-8')

            f = open( os.path.join(self._out, t.url), "w" )
            f.write(my_tpl.render(  cat=t.tagname,
                                    tagged=post_list,
                                    articles= self.posts_list,
                                    tags=self.tags))
            f.close()
        #print "j'ai sauvegarde %s postes_tagges"%(len(self.tags ))

    def buildStaticPages(self):
        """Construct all the static pages according to
        the 'Static.mako' file template 
        """
        chem = os.path.join(self._static,'*.rst')

        for filename in os.listdir(self._static) :
            ## the filename will be used to store the page's title
            f = codecs.open( os.path.join(self._static,filename), "r", "utf-8" )
            cont = f.read()
            contenu = publish_parts(cont, writer_name="html")["html_body"]
            f.close()

            # setup the mako template
            mylookup = TemplateLookup(directories=["/"])
            mytemplate = Template(filename=os.path.join( \
                                self._templates,'Static.mako'), 
                                lookup=mylookup,
                                input_encoding='utf-8', 
                                output_encoding='utf-8')
            # taken on
            # http://xahlee.org/perl-python/split_fullpath.html
            (dirName, fileName) = os.path.split(filename)
            (fileBaseName, fileExtension)=os.path.splitext(fileName)

            titre = unicode(fileBaseName.replace("_"," ")).encode("utf-8")
            print "TITRE STATIQUE =",titre
            
            f = file(os.path.join(self._out, '%s.html'%(fileBaseName)),'w')
            f.write(mytemplate.render(
                    static = contenu,
                    articles = self.posts_list,
                    tags = self.tags,
                    title = titre))
            f.close()

    def buildRss(self):
        """Construct the RSS feed of the blog
        """
        last_post = self.posts_list[0]
        
        away,host,user,password,remote = self.readConf()
        rss_name = remote.replace('/','')
        # decalage de temps
        delta_t = datetime.timedelta(hours=1)
        
        p_items = [PyRSS2Gen.RSSItem(
             title = post.title,
             link = away + post.url,
             description = post.html_content,
             pubDate = post.postdate-delta_t) \
             for post in self.posts_list]

        rss = PyRSS2Gen.RSS2(
        title = "%s feed"%self.blog_dic_names["blog_name"],
        
        # added on 9 mars 2008
        language = "fr",
        webMaster = "kib2@free.fr",
        pubDate = post.postdate-delta_t,
        generator = "PyRSS2Gen",
        
        link = away + "index.html",
        description = last_post.html_content , # le contenu
        lastBuildDate = datetime.datetime.now(),
        items = p_items)
        rss.write_xml(open(os.path.join(self._out,"flux.xml"), "w"))


    def transferToFtp(self):
        away,host,user,password,remote = self.readConf()
        print "away,host,user,password,remote",away,host,user,password,remote

        fu = FtpUpload()
        fu.setHost(host, user, password)
        fu.setMd5File('free.md5')
        fu.upload(
            hostdir=remote, src=self._out,
            text='*.html *.css *.xml', binary='*.gif *.jpg'
            )
        # more upload() calls can go here..
        fu.deleteOldFiles()
        fu.finish()
        
        print "Blog builded successfully!\n"

    @property
    def tags(self):
        """We build the list of Tags here by looking at
        each Post instance, grabbing its string based tags list.

        From them, it builds a real Tags list instances.

        """
        thetags = []

        for post in self.posts_list :
            # iterate over each post pseudo-tag
            for tag in post.tags :
                #if tag not in thetags :
                thetagsNames = [k.tagname for k in thetags]
                #print 'Checking %s versus %s'%(tag.tagname,thetagsNames)
                if tag.tagname not in thetagsNames :
                    thetags.append(tag)

        ## Iterate over each tab and feeds it with
        ## corresponding posts
        for t in thetags:
            for p in self.posts_list:
                if t.tagname in [t1.tagname \
                    for t1 in p.tags if p not in t.posts]:
                    t.posts.append(p)
        thetags.sort()
        return thetags

#=============================================================================
# Main Classes :
# - Post
# - Tag
# ============================================================================

## ----- Post  --------------------------------------------------------------
class Post(object):
    pid = 0

    def __init__(self, filename = None, manager=None):
        self.manager = manager
        self.filename = filename

        ## note that post.contents is done inside self.getInfos()
        self.title, self.postdate, self.tags, self.extension = self.getInfos()

        Post.pid += 1
        self.id = Post.pid

    def normalise_name(self,tname):
        return tname.strip().replace(' ', '_')

    def getInfos(self):
        """ Given a filename, parse the document to retrieve :

        - post title
        - post date
        - post tags
        - post markup [optioanl, reSt by default]
        """

        infos = ('tit','date','tags','markup')
        markup = {  'rest': '.rst',
                    'markdown' : '.md',
                 }

        post_title, post_time, post_tags, post_markup = None, None, None, 'rest'

        f = open(self.manager._in + self.filename,'r')
        contents = f.readlines() # returns a list
        f.close()

        self.contents = ''.join(contents[4:]).decode('utf-8')

        self.toBeParsed = contents[0:4]

        ## We start by retrieving the beginning 5 lines
        ## of each Post file to get the title, date, tags and markup
        for el in infos :
            motif = re.compile(r'\[%s\](?P<conf>.*?)\[/%s\]'\
                    %(el,el),re.MULTILINE|re.UNICODE)
            for m in re.finditer(motif, ''.join( \
                                self.toBeParsed).decode('utf-8')):

                if el == 'tit' :
                    post_title = m.group('conf')
                elif el == 'date' :
                    t = m.group('conf').split()
                    post_time = datetime.datetime(  int(t[0]),
                                                    int(t[1]),
                                                    int(t[2]),
                                                    int(t[3]),
                                                    int(t[4])
                                                )
                elif el == 'tags':
                    post_tags = [Tag(t.strip().encode('utf-8')) \
                                for t in m.group('conf').split(',')]
                    # now each tag in the post is added
                elif el == 'markup':
                    post_markup = m.group('conf')
        extension = markup[post_markup]

        return post_title, post_time, post_tags, extension

    @property
    def html_content(self):
        if self.extension == '.rst' :
            return publish_parts(self.contents,
                    writer_name="html")["html_body"]
        elif self.extension == '.md' :
            return markdown.markdown(self.contents,
                                    extensions= ['codehilite']
                                    )

    @property
    def get_tags(self):
        return ",".join([t.tagname for t in self.tags])

    @property
    def get_tags_one_by_one(self):
        return [t.tagname for t in self.tags]

    @property
    def get_time(self):
        temps= self.postdate.strftime('le %A %d %B %Y à %H h %M min')
        return temps.decode('utf-8')

    @property
    def url(self):
        return "%s.html"%(self.normalise_name(self.title))

    def __repr__(self):
        return "<Post(%r,%s)>" % (self.title, str(self.postdate))

    def saveWithMako(self):
        ## Va chercher le template mako, 
        ## le remplis et le sauvegarde
        ## Si la date du fichier à générer est plus vielle 
        ## que le fichier source, on génère...sinon pas !
        mylookup = TemplateLookup(directories=["/"])
        my_tpl = Template(  filename=self.manager._templates + 'Detail.mako',
                            lookup=mylookup,
                            format_exceptions=True,
                            input_encoding='utf-8',
                            output_encoding='utf-8')

        #tit = normalise_name(self.title)
        f = open( self.manager._out + self.url, "w" )
        f.write(my_tpl.render(  p=self,
                                articles= self.manager.posts_list,
                                tags = self.manager.tags ))
        f.close()

## ----- Tag ----------------------------------------------------------------
class Tag(object):
    """A Post tag object.

    The Posts relatives to a given Tag will be
    filled inside the blogManager class.
    """
    def __init__(self, tagname):
        #self.tagname = tagname.decode('utf-8')

        self.tagname = tagname.decode('utf-8')
        self.posts = []
        
    def __repr__(self):
        return self.tagname.encode('utf-8')
    
    def __cmp__(self, other):
        """To sort the tags by name, we need to
        compare their names"""
        return cmp(self.tagname.encode('utf-8'), other.tagname.encode('utf-8'))

    def normalise_name(self,tname):
        return tname.strip().replace(' ', '_')

    @property
    def url(self):
        return "tagged_%s.html"%(self.normalise_name(self.tagname))

    @property
    def get_posts(self):
        return [(p.title, unicode(p.url)) for p in self.posts]

    @property
    def get_number_of_posts(self):
        return len(self.posts)

## ----- Main Programm  -----------------------------------------------------
def main():
    print md5.md5(open('Fonction.rst', 'rb').read()).hexdigest()

if __name__ == "__main__":
    main()


