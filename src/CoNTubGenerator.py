# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
"""
CoNTubGenerator.py

Generator functions which use cad/plugins/CoNTub.

$Id$

Also intended as a prototype of code which could constitute the nE-1 side
of a "generator plugin API". Accordingly, the CoNTub-specific code should
as much as possible be isolated into small parts of this, with most of it
knowing nothing about CoNTub's specific functionality or parameters.
"""

__author__ = "bruce"

#k not all imports needed?
## from GeneratorDialogs import ParameterizedDialog ###IMPLEM file and class
import env
from HistoryWidget import redmsg, orangemsg, greenmsg
##from widgets import double_fixup
##from Utility import Group
from GeneratorBaseClass import GeneratorBaseClass
from debug import print_compact_traceback
import os, sys
from platform import find_or_make_Nanorex_subdir, find_or_make_any_directory

# ==

def add_insert_menu_item(win, command, name_of_what_to_insert, options = ()): ###e this should be a method of MWsemantics.py
    menuIndex = 2 ### kluge - right after Nanotube, at the moment (since indices start from 0)
    menu = win.Insert
    menutext = "%s" % (name_of_what_to_insert,)
    undo_cmdname = "Insert %s" % (name_of_what_to_insert,) ## get this from caller, or, make it available to the command as it runs
        ###e but need to translate it ourselves, ##qApp.translate("Main Window", "Recent Files", None)
    ## self.connect(self.recentFilePopupMenu, SIGNAL('activated (int)'), self._openRecentFile)
    from widgets import insert_command_into_menu
    insert_command_into_menu( menu, menutext, command, options = options, position = menuIndex, undo_cmdname = undo_cmdname)
    return

# ==

def builtin_plugins_dir(): # modified from sim_bin_dir_path in runSim.py; should move both that and this to platform.py ###e
    """Return pathname of built-in plugins directory. Should work for either developers or end-users on all platforms.
    (Doesn't check whether it exists.)
    """
    # filePath = the current directory NE-1 is running from.
    filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.normpath(filePath + '/../plugins')

def user_plugins_dir():
    """Return pathname of user custom plugins directory, or None if it doesn't exist."""
    return find_or_make_Nanorex_subdir( 'Plugins', make = False)

def find_plugin_dir(plugin_name):
    "Return (True, dirname) or (False, errortext), with errortext wording chosen as if the requested plugin ought to exist."
    try:
        userdir = user_plugins_dir()
        if userdir and os.path.isdir(userdir):
            path = os.path.join(userdir, plugin_name)
            if os.path.isdir(path):
                return True, path
    except:
        print_compact_traceback("bug in looking for user-customized plugin %r; trying builtin plugins: ")
        pass
    try:
        appdir = builtin_plugins_dir()
        assert appdir
        if not os.path.isdir(appdir):
            return False, "error: can't find built-in plugins directory [%s] (or it's not a directory)" % (appdir,)
        path = os.path.join(appdir, plugin_name)
        if os.path.isdir(path):
            return True, path
        return False, "can't find plugin %r" % (plugin_name,)
    except:
        print_compact_traceback("bug in looking for built-in plugin %r: " % (plugin_name,))
        return False, "can't find plugin %r" % (plugin_name,)
    pass

# ==

class PluginlikeGenerator:
    """Superclass for generators whose code is organized similar to that of a (future) plugin.
    Subclasses contain data and methods which approximate the functionality
    of metadata and/or code that would ultimately be found in a plugin directory.
    See the example subclass in this file for details.
    """
    ok_to_install_in_UI = False # changed to True in instances which become ok to install into the UI; see also errorcode
    # default values of subclass-specific class constants
    what_we_generate = "Something"
    
    def register(subclass): # staticmethod
        win = env.mainwindow()
        try:
            instance = subclass(win)
            if instance.ok_to_install_in_UI:
                instance.install_in_UI()
                if env.debug(): print "debug: registered", instance
            else:
                if env.debug(): print "debug: didn't register", instance
        except:
            print_compact_traceback("bug in instantiating %r or installing its instance: " % subclass)
        return
    register = staticmethod(register)

    errorcode = 0 # set to something true if an error occurs which should prevent us from continuing to set up this plugin
    def fatal(self, errortext, errorcode = 1):
        "Init submethods call this if they detect a fatal setup error; it prints the message appropriately and sets self.errorcode."
        assert errorcode
        if self.errorcode:
            print "plugin %r bug: self.errorcode was already set before fatal was called
        print "plugin %r setup error: %s" % (errortext,)

    def __init__(self, win):
        self.win = win

        # find plugin dir -- if not, error, and don't install in UI
        # (as if we don't know the metadata needed to do so)
        path = self.find_plugin_dir() # might set self.find_plugin_dir_errortext
        if not path:
            ###e too soon for history message??
            self.fatal( self.find_plugin_dir_errortext)
            return
        self.plugin_dir = path # for error messages, and used by runtime methods
        
        # make sure the stuff we need is in there (and try to use it to set up the dialogs, commands, etc)
        if not self.setup_from_plugin_dir():
            # that printed error msgs if it needed to
            return
        
        self.ok_to_install_in_UI = True
        return
        
##    def commandline_args(self, params):
##        "Return the arguments for the HJ commandline, not including the output filename..." ###
##        return "stub"###e
##    def run_command(self, args):
##        ""
##        # get executable
##        # make filename
##        # run it
##        # look at exitcode
##        # etc
    def find_plugin_dir(self):
        ok, path = find_plugin_dir(self.plugin_name)
        if ok:
            assert os.path.isdir(path)
            return path
        else:
            self.find_plugin_dir_errortext = path
            return None
        pass
    
    def setup_from_plugin_dir(self):
        "Using self.plugin_dir, setup dialogs, commands, etc. Report errors to self.fatal as usual."
        param_desc_path = os.path.join(self.plugin_dir, self.parameter_set_filename)
        self.param_desc_path = param_desc_path
        if not os.path.isfile(param_desc_path):
            return self.fatal("can't find param description file [%s]" % (param_desc_path,)
        ###E more -- the dialog, param set, executable exists, etc (even a self test if it defines one?)
        return
    
    def create_working_directory(self): # we should not call this until the plugin is first used. #####@@@@@
        "Create a temporary directory (fixed pathname per plugin) for this plugin to use. Report errors to self.fatal as usual."
        subdir = os.path.join( tempfiles_dir(), "plugin-" + self.plugin_name )
        errorcode, path = find_or_make_any_directory(subdir)
        if errorcode:
            # should never happen; not sure we can rely on this fatal system since this is done only when needed ###@@@
            errortext = path
            return self.fatal(errortext)
        self.working_path = working_path
        return
        
    def install_in_UI(self):
        assert self.ok_to_install_in_UI
        #e create whatever we want to be persistent which was not already done in setup_from_plugin_dir (e.g. a job dir for it)
        
        0
        #e install the necessary commands in the UI (eg in insert menu)
        ### WRONG -- menu text should not contain Insert, but undo cmdname should (so separate option is needed), and needs icon
        ###e add options for things like tooltip text, whatsthis text, iconset
        options = [('iconset','junk.png')]
        add_insert_menu_item( self.win, self.insert_menu_command, self.what_we_generate, options)
        pass
    def insert_menu_command(self):
        """Run an Insert Whatever menu command to let the user generate things using this plugin.
        """
        print 'ought to insert a', self.what_we_generate
        pass###e
    pass # end of class PluginlikeGenerator

class HeterojunctionGenerator(PluginlikeGenerator):
    """Encapsulate the plugin-specific data and code (or references to it)
    for the CoNTub plugin's heterojunction command.
       In a real plugin API, this data would come from the plugin directory,
    and this code would be equivalent to either code in nE-1 parameterized by metadata in the plugin directory,
    and/or actual code in the plugin directory.
       (The present example is clearly simple enough to be the contents of a metadata file,
    but not all of the other built-in generators are that simple.)
    """
    topic = 'Nanotubes' # for sponsor_keyword for GeneratorBaseClass's SponsorableMixin superclass (and for submenu?)
    what_we_generate = "Heterojunction"
        # used for insert menu item text, undo cmdname, history messages; not sure about wikihelp featurename
    menu_item_icon = "blablabla"
    plugin_name = "CoNTub"
        # used as directory name, looked for in ~/Nanorex/Plugins someday, and in cad/plugins now and someday...
    parameter_set_filename = "HJ_param_desc.txt" #e or .desc?
    executable = "HJ" # no .exe, we'll add that if necessary on Windows ## this might not be required of every class
    outputfiles_pattern = "$out1.mmp"
    executable_args_pattern = "$p1 $p2 $out1.mmp"
    
    pass # end of class HeterojunctionGenerator

PluginlikeGenerator.register(HeterojunctionGenerator)

# end
