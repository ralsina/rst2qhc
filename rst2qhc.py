#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Call rst2html.py and generate a Qt Help Collection from the output.
This program is (c) Roberto Alsina <ealsina@netmanagers.com.ar> 2009
And is licensed under the GPLv2.
Please read the COPYING file for licensing terms.
"""
   
import os,sys,codecs,shutil
from optparse import OptionParser

from docutils.parsers.rst import roles

# Register keyword role
def keyword_role(name, rawtext, text, lineno, inliner,
                 options={}, content=[]):
    return [],[]
roles.register_canonical_role('keyword', keyword_role)
roles.register_local_role('keyword', keyword_role)

import docutils.readers.doctree
import docutils.core
import docutils.nodes as nodes

from docutils.transforms import Transformer

HelpCollection=r"""<?xml version="1.0" encoding="utf-8" ?>
<QHelpCollectionProject version="1.0">
    <docFiles>
        <register>
            <file>doc.qch</file>
        </register>
    </docFiles>
</QHelpCollectionProject>
"""

HelpProject=r"""<?xml version="1.0" encoding="UTF-8"?>
<QtHelpProject version="1.0">
    <namespace>%(namespace)s</namespace>
    <virtualFolder>%(folder)s</virtualFolder>
    <customFilter name="%(filter_name)s">
        %(filter_attributes)s
    </customFilter>
    <filterSection>
        %(filter_attributes)s
        <toc>%(sections)s
        </toc>
        <keywords>%(keywords)s
        </keywords>
        <files>
            %(files)s
        </files>
    </filterSection>
</QtHelpProject>
"""

class HelpProjectTranslator(nodes.SparseNodeVisitor):

    """Processes the rst file and finds things like titles, keyword-role
    elements and creates Qt's help project files accordingly.
    You need to use rst2html to create the actual html files.
    """
    
    def __init__(self, document,file_name):
        self.attributes={
            'namespace':'uRSSus',
            'folder':'doc',
            'filter_name':'uRSSus',
            'filter_attributes':'<filterAttribute>urssus</filterAttribute>',
            'doc_title':'Unknown Title',
            'file_name':file_name,
            'sections':'',
            'keywords':'',
            'files':'<file>index.html</file>'
            }
        self.section_level=0
        self.cur_section_ref=''
        nodes.NodeVisitor.__init__(self, document)

    def visit_section(self, node):
        self.section_level += 1
        
    def depart_section(self, node):
        self.section_level -= 1

    def visit_title(self,node):
        if isinstance(node.parent, nodes.document):
            # Document title
            self.attributes['doc_title']=node.astext()
        elif isinstance(node.parent, nodes.section):
            # Section title
            if self.section_level==1: # Top level sections only
                self.attributes['sections']+='\n                  <section title="%s" ref="%s#%s"/>'%\
                    (node.astext(),
                     self.attributes['file_name'],
                     node_to_ref(node))
            self.cur_section_ref=node_to_ref(node)

    def visit_inline(self, node):
        if 'keyword' in node['classes']:
            # Right now, link it to the last section name. Needs to be better
            self.attributes['keywords']+='\n                  <keyword name="%s" ref="%s#%s"/>'%\
                (node.astext(),
                 self.attributes['file_name'],
                 self.cur_section_ref)
                
def node_to_ref(node):
    ids=node.parent.get('ids',[])
    if ids:
        return ids[0]
    else:
        return ''
 
def main():
    parser=OptionParser()
    parser.add_option('--namespace',dest='namespace',help='Help Project Namespace',default='Unknown')
    parser.add_option('--virtualfolder',dest='virtualfolder',help='Help Project VirtualFolder',default='doc')
    parser.add_option('--customfilter',dest='customfilter',help='Help Project Custom Filter Name',default='Unknown')
    parser.add_option('--filterattributes',dest='filterattr',help='Filter Attributes (colon-separated)',default='')
    parser.add_option('-o','--outputdir',dest='outdir',help='Output Directory',default='out')
    parser.add_option('--rst2htmlopts',dest='rst2htmlopts',help='Options passed to rst2html',default='')
    parser.add_option('--manifest',dest='manifest',help='A list of files to include. Use it for CSS, images, etc.',default='')
    parser.add_option('--create-qhcp',dest='createqhcp',help='Create a basic Help Collection Project file',default=False,action='store_true')
        
    options,args=parser.parse_args()
    outdir=options.outdir
    
    if not os.path.isdir(outdir):
        sys.stderr.write("Please create the output folder %s first!\n"%outdir)
        sys.exit(1)
    
    infiles=args
    
    print "Creating Help File from: %s"%', '.join(infiles)
    print "Saving to: %s"%outdir


    attributes={
        'namespace':options.namespace,
        'folder':options.virtualfolder,
        'filter_name':options.customfilter,
        'filter_attributes':'',
        'doc_title':'Unknown Title',
        'file_name':'',
        'sections':'',
        'keywords':'',
        'files':''
        }
    if options.filterattr:
        attributes['filter_attributes']='\n        '.join('<filterAttribute>%s</filterAttribute>'%a for a in options.filterattr.split(':'))
    if options.manifest:
        # Put everything in the help project
        # And copy into the outdir
        for f in open(options.manifest):
            f=f.strip()
            if f:
                attributes['files']+='\n            <file>%s</file>'%f
                shutil.copy(f,outdir)
    
    for infile in infiles:
        # Generate HTML file in outdir
        filename=os.path.basename(infile)
        if filename.endswith('.txt') or filename.endswith('.rst'):
            outfile = filename[:-4] + '.html'
        else:
            outfile=filename + '.html'
        os.system("rst2html.py %s %s %s"%(infile,os.path.join(outdir,outfile),options.rst2htmlopts))
        
        doctree=docutils.core.publish_doctree(open(infile).read(),source_path=infile)
        translator=HelpProjectTranslator(doctree,outfile)
        doctree.walkabout(translator)
        attributes['keywords']+=translator.attributes['keywords']
        attributes['sections']+='\n             <section title="%s" ref="%s">%s\n             </section>'%\
                (translator.attributes['doc_title'],
                 outfile,
                 translator.attributes['sections'],
                )
        attributes['files']+='\n            <file>%s</file>'%outfile
        
    codecs.open(os.path.join(outdir,'project.qhp'),'w','utf-8').write(HelpProject % attributes)
    os.system("qhelpgenerator %s -o %s"%(os.path.join(outdir,'project.qhp'),os.path.join(outdir,'doc.qhc')))
    print "Created: ",os.path.join(outdir,'help.qhc')
    
    if options.createqhcp:
        codecs.open(os.path.join(outdir,'project.qhcp'),'w','utf-8').write(HelpCollection % attributes)
        print "Created: ",os.path.join(outdir,'project.qhcp')
   
if __name__=='__main__':
    main()
