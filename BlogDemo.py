# -*- coding: utf-8 -*-
#!/usr/bin/python

## Imports
import os
from LittleBlogger import *

# Globals
APPLIREP = os.getcwd()

def main():
    import time
    
    t = time.time()
    bm = blogManager(os.path.join(APPLIREP,'BlogDemo'))
    
    # read the blog's config file
    bm.readConf()
    
    # create the posts
    bm.publish()
    
    #transfert it
    #bm.transferToFtp()
    print "Temps de création du blog : %s secondes"%(str(time.time()-t))

## Main Programm
if __name__ == "__main__":
    main()
