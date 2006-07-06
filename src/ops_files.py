# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
ops_files.py provides fileSlotsMixin for MWsemantics,
with file slot methods and related helper methods.

$Id$

Note: most other ops_*.py files provide mixin classes for Part,
not for MWsemantics like this one.

History:

bruce 050907 split this out of MWsemantics.py.
[But it still needs major cleanup and generalization.]

bruce 050913 used env.history in some places.
'''

from qt import QFileDialog, QMessageBox, QString, qApp, QSettings
from assembly import assembly
import os, shutil
import platform

from constants import * # needed for at least globalParms
from fileIO import * # this might be needed for some of the many other modules it imports; who knows? [bruce 050418 comment]
    # (and it's certainly needed for the functions it defines, e.g. writepovfile.)
from files_pdb import readpdb, insertpdb, writepdb
from files_gms import readgms, insertgms
from files_mmp import readmmp, insertmmp, fix_assy_and_glpane_views_after_readmmp
from debug import print_compact_traceback

from HistoryWidget import greenmsg, redmsg, orangemsg, _graymsg

import preferences
import env

def set_waitcursor(on_or_off):
    """For on_or_off True, set the main window waitcursor.
    For on_or_off False, revert to the prior cursor.
    [It might be necessary to always call it in matched pairs, I don't know [bruce 050401]. #k]
    """
    if on_or_off:
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
    else:
        QApplication.restoreOverrideCursor() # Restore the cursor
    return

debug_part_files = True #&&& Debug prints to history. Change to False after QA. Mark 060703 [revised by bruce 060704]

def fileparse(name): #bruce 050413 comment: see also filesplit and its comments.
    # This has known bugs (e.g. for basename containing two dots);
    # should be revised to use os.path.split and splitext. ###@@@
    """breaks name into directory, main name, and extension in a tuple.
    fileparse('~/foo/bar/gorp.xam') ==> ('~/foo/bar/', 'gorp', '.xam')
    """
    m=re.match("(.*\/)*([^\.]+)(\..*)?",name)
    return ((m.group(1) or "./"), m.group(2), (m.group(3) or ""))


class fileSlotsMixin: #bruce 050907 moved these methods out of class MWsemantics
    "Mixin class to provide file-related methods for class MWsemantics. Has slot methods and their helper methods."
    
    def fileNew(self):
        """If this window is empty (has no assembly), do nothing.
        Else create a new empty one.
        """
        #bruce 050418 comment: this has never worked correctly to my knowledge,
        # and therefore it was made unavailable from the UI some time ago.
        from MWsemantics import MWsemantics #bruce 050907 (might have a recursive import problem if done at toplevel)
        foo = MWsemantics()
        foo.show()

    def fileInsert(self):
        
        env.history.message(greenmsg("Insert File:"))
         
        wd = globalParms['WorkingDirectory']
        fn = QFileDialog.getOpenFileName(wd,
                "Molecular machine parts (*.mmp);;Protein Data Bank (*.pdb);;GAMESS (*.out);;All of the above (*.pdb *.mmp *.out)",
                self,
                "Insert File dialog",
                "Select file to insert" ) # This is the caption for the dialog.  Fixes bug 1125. Mark 051116.
                
        if not fn:
             env.history.message("Cancelled")
             return
        
        if fn:
            fn = str(fn)
            if not os.path.exists(fn):
                #bruce 050415: I think this should never happen;
                # in case it does, I added a history message (to existing if/return code).
                env.history.message( redmsg( "File not found: " + fn) )
                return

            if fn[-3:] == "mmp":
                try:
                    insertmmp(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting MMP file [%s]: " % fn )
                    env.history.message( redmsg( "Internal error while inserting MMP file: " + fn) )
                else:
                    self.assy.changed() # The file and the part are not the same.
                    env.history.message( "MMP file inserted: " + fn )
            
            if fn[-3:] in ["pdb","PDB"]:
                try:
                    insertpdb(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting PDB file [%s]: " % fn )
                    env.history.message( redmsg( "Internal error while inserting PDB file: " + fn) )
                else:
                    self.assy.changed() # The file and the part are not the same.
                    env.history.message( "PDB file inserted: " + fn )
            
            if fn[-3:] in ["out","OUT"]:
                try:
                    r = insertgms(self.assy, fn)
                except:
                    print_compact_traceback( "MWsemantics.py: fileInsert(): error inserting GAMESS OUT file [%s]: " % fn )
                    env.history.message( redmsg( "Internal error while inserting GAMESS OUT file: " + fn) )
                else:
                    if r:
                        env.history.message( redmsg("File not inserted."))
                    else:
                        self.assy.changed() # The file and the part are not the same.
                        env.history.message( "GAMESS file inserted: " + fn )
                    
                    
            self.glpane.scale = self.assy.bbox.scale()
            self.glpane.gl_update()
            self.mt.mt_update()


    def fileOpen(self, recentFile = None):
        '''By default, users open a file through 'Open File' dialog. If <recentFile> is provided, it means user
           is opening a file named <recentFile> through the 'Recent Files' menu list. The file may or may not exist. '''
        env.history.message(greenmsg("Open File:"))
        
        mmkit_was_hidden = self.hide_MMKit_during_open_or_save_on_MacOS() # Fixes bug 1744. mark 060325
        
        if self.assy.has_changed():
            ret = QMessageBox.warning( self, self.name(),
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before opening a new part?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2
            
            if ret==0: # Save clicked or Alt+S pressed or Enter pressed.
                ##Huaicai 1/6/05: If user canceled save operation, return 
                ## without letting user open another file
                if not self.fileSave():
                    if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
                    return
                
            ## Huaicai 12/06/04. Don't clear it, user may cancel the file open action    
            elif ret==1: pass#self.__clear() 
            
            elif ret==2: 
                env.history.message("Cancelled.")
                if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
                return # Cancel clicked or Alt+C pressed or Escape pressed

        # Determine what directory to open.
        if self.assy.filename: odir, fil, ext = fileparse(self.assy.filename)
        else: odir = globalParms['WorkingDirectory']

        if recentFile:
            if not os.path.exists(recentFile):
              QMessageBox.warning( self, self.name(),
                "The file " + recentFile + " doesn't exist any more.", QMessageBox.Ok, QMessageBox.NoButton)
              if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
              return
            
            fn = recentFile
        else:
            fn = QFileDialog.getOpenFileName(odir,
                    "All Files (*.mmp *.pdb);;Molecular machine parts (*.mmp);;Protein Data Bank (*.pdb)",
                    self )
                    
            if not fn:
                env.history.message("Cancelled.")
                if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
                return
        
        if fn:
            self._updateRecentFileList(fn)

            self.__clear() # leaves glpane.mode as nullmode, as of 050911
            self.glpane.start_using_mode( '$DEFAULT_MODE') #bruce 050911 [now needed here, to open files in default mode]
                
            fn = str(fn)
            if not os.path.exists(fn):
                if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
                return

            #k Can that return ever happen? Does it need an error message?
            # Should preceding clear and modechange be moved down here??
            # (Moving modechange even farther below would be needed,
            #  if we ever let the default mode be one that cares about the
            #  model or viewpoint when it's entered.)
            # [bruce 050911 questions]

            isMMPFile = False
            if fn[-3:] == "mmp":
                readmmp(self.assy,fn)
                    #bruce 050418 comment: we need to check for an error return
                    # and in that case don't clear or have other side effects on assy;
                    # this is not yet perfectly possible in readmmmp.
                env.history.message("MMP file opened: [" + fn + "]")
                isMMPFile = True
                
            if fn[-3:] in ["pdb","PDB"]:
                readpdb(self.assy,fn)
                env.history.message("PDB file opened: [" + fn + "]")

            dir, fil, ext = fileparse(fn)
            ###@@@e could replace some of following code with new method just now split out of saved_main_file [bruce 050907 comment]
            self.assy.name = fil
            self.assy.filename = fn
            self.assy.reset_changed() # The file and the part are now the same

#            self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.filename + "]"))
            self.update_mainwindow_caption()

            if isMMPFile:
                #bruce 050418 moved this code into a new function in files_mmp.py
                # (but my guess is it should mostly be done by readmmp itself)
                fix_assy_and_glpane_views_after_readmmp( self.assy, self.glpane)
            else: ###PDB or other file format        
                self.setViewFitToWindow()

            self.assy.clear_undo_stack() #bruce 060126, fix bug 1398

            self.glpane.gl_update_duration(new_part=True) #mark 060116.
            
            self.mt.mt_update()

        if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
        
        return

    def fileSave(self):
        
        env.history.message(greenmsg("Save File:"))
        
        #Huaicai 1/6/05: by returning a boolean value to say if it is really 
        # saved or not, user may choose "Cancel" in the "File Save" dialog          
        if self.assy:
            if self.assy.filename: 
                self.saveFile(self.assy.filename)
                return True
            else: 
                return self.fileSaveAs()
        return False #bruce 050927 added this line (should be equivalent to prior implicit return None)

    def fileSaveAs(self): #bruce 050927 revised this
        safile = self.fileSaveAs_filename()
        # fn will be None or a Python string
        if safile:
            self.saveFile(safile)
            return True
        else:
            # user cancelled, or some other error; message already emitted.
            return False
        pass

    def fileSaveAs_filename(self, images_ok = True):
        #bruce 050927 split this out of fileSaveAs, added some comments, added images_ok option
        """Ask user to choose a save-as filename (and file type) based on the current main filename.
        If file exists, ask them if they want to overwrite that file.
        If user cancels either dialog, or if some error occurs,
        emit a history message and return None.
        Otherwise return the file name to save to, as a Python string.
           If images_ok is false, don't offer the image formats as possible choices for filetype.
        This is needed due to limits in how callers save these image formats
        (and that also determines the set of image formats excluded by this option).
        """
        # figure out sdir, sfilter from existing filename
        if self.assy:
            if self.assy.filename:
                dir, fil, ext = fileparse(self.assy.filename)
                sdir = self.assy.filename
            else: 
                dir, fil = "./", self.assy.name
                ext = ".mmp"
                sdir = globalParms['WorkingDirectory']
        else:
            env.history.message( "Save Ignored: Part is currently empty." )
            return None

        if ext == ".pdb": sfilter = QString("Protein Data Bank (*.pdb)")
        else: sfilter = QString("Molecular machine parts (*.mmp)")

        # ask user for new filename (and file type); they might cancel; fn will be a QString
        formats = \
                    "Molecular Machine Part (*.mmp);;"\
                    "Protein Data Bank (*.pdb);;"\
                    "POV-Ray (*.pov);;"\
                    "Model MDL (*.mdl);;"
        if images_ok:
            formats += \
                    "JPEG (*.jpg);;"\
                    "Portable Network Graphics (*.png)"

        mmkit_was_hidden = self.hide_MMKit_during_open_or_save_on_MacOS() # Fixes bug 1744. mark 060325
        
        fn = QFileDialog.getSaveFileName(sdir, formats,
                    self, "IDONTKNOWWHATTHISIS",
                    "Save As",
                    sfilter)

        if fn:
            fn = str(fn)
            # figure out name of new file, safile [bruce question: when and why can this differ from fn?]
            dir, fil, ext2 = fileparse(fn)
            del fn #bruce 050927
            ext =str(sfilter[-5:-1]) # Get "ext" from the sfilter. It *can* be different from "ext2"!!! - Mark
            safile = dir + fil + ext # full path of "Save As" filename

            # ask user before overwriting an existing file (other than this part's main file)
            if self.assy.filename != safile: # If the current part name and "Save As" filename are not the same...
                if os.path.exists(safile): # ...and if the "Save As" file exists...

                    # ... confirm overwrite of the existing file.
                    ret = QMessageBox.warning( self, self.name(),
                        "The file \"" + fil + ext + "\" already exists.\n"\
                        "Do you want to overwrite the existing file or cancel?",
                        "&Overwrite", "&Cancel", None,
                        0,      # Enter == button 0
                        1 )     # Escape == button 1

                    if ret==1: # The user cancelled
                        env.history.message( "Cancelled.  Part not saved." )
                        if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
                        return None # Cancel clicked or Alt+C pressed or Escape pressed

            ###e bruce comment 050927: this might be a good place to test whether we can write to that filename,
            # so if we can't, we can let the user try choosing one again, within this method.
            # But we shouldn't do this if it's the main filename, to avoid erasing that file now.
            # (If we only do this test with each function
            # that writes into the file, then if that fails it'll more likely require user to redo the entire op.)
            
            if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
            
            return safile
            
        else:
            if mmkit_was_hidden: self.glpane.mode.MMKit.show() # Fixes bug 1744. mark 060325
            
            return None ## User canceled.

    def fileSaveSelection(self): #bruce 050927
        "slot method for Save Selection"
        env.history.message(greenmsg("Save Selection:"))
            # print this before counting up what selection contains, in case that's slow or has bugs
        (part, killfunc, desc) = self.assy.part_for_save_selection()
            # part is existing part (if entire current part was selected)
            # or new homeless part with a copy of the selection (if selection is not entire part)
            # or None (if the current selection can't be saved [e.g. if nothing selected ##k]).
            # If part is not None, its contents are described in desc;
            # otherwise desc is an error message intended for the history.
        if part is None:
            env.history.message(redmsg(desc))
            return
        # now we're sure the current selection is savable
        safile = self.fileSaveAs_filename( images_ok = False)
            ##e if entire part is selected, could pass images_ok = True,
            # if we also told part_for_save_selection above never to copy it,
            # which is probably appropriate for all image-like file formats
        saved = self.savePartInSeparateFile(part, safile)
        if saved:
            desc = desc or "selection"
            env.history.message( "Saved %s in %s" % (desc, safile) )
                #e in all histmsgs like this, we should encode html chars in safile and desc!
        else:
            pass # assume savePartInSeparateFile emitted error message
        killfunc()
        return

    def saveFile(self, safile):
        
        dir, fil, ext = fileparse(safile)
            #e only ext needed in most cases here, could replace with os.path.split [bruce 050907 comment]
                    
        if ext == ".mmp" : # Write MMP file
            self.save_mmp_file( safile)

        elif ext == ".pdb": # Write PDB file.
            try:
                writepdb(self.assy.part, safile) #bruce 050927 revised arglist
            except:
                print_compact_traceback( "MWsemantics.py: saveFile(): error writing file %r: " % safile )
                env.history.message(redmsg( "Problem saving PDB file: " + safile ))
            else:
                self.saved_main_file(safile, fil)
                    #bruce 050907 split out this common code, though it's probably bad design for PDB files (as i commented elsewhere)
                env.history.message( "PDB file saved: " + self.assy.filename )
                    #bruce 050907 moved this after mt_update (which is now in saved_main_file)
        else:
            self.savePartInSeparateFile( self.assy.part, safile)
        return

    def savePartInSeparateFile( self, part, safile): #bruce 050927 added part arg, renamed method
        """Save some aspect of part (which might or might not be self.assy.part) in a separate file, named safile,
        without resetting self.assy's changed flag or filename. For some filetypes, use display attributes from self.glpane.
        For JPG and PNG, assert part is the glpane's current part, since current implem only works then.
        """
        #e someday this might become a method of a "saveable object" (open file) or a "saveable subobject" (part, selection).
        dir, fil, ext = fileparse(safile)
            #e only ext needed in most cases here, could replace with os.path.split [bruce 050908 comment]
        type = "this" # never used (even if caller passes in unsupported filetype) unless there are bugs in this routine
        saved = True # be optimistic (not bugsafe; fix later by having save methods which return a success code)
        glpane = self.glpane
        try:
            # all these cases modify type variable, for use only in subsequent messages.
            # kluges: glpane is used for various display options;
            # and for grabbing frame buffer for JPG and PNG formats
            # (only correct when the part being saved is the one it shows, which we try to check here).
            if ext == ".mmp": #bruce 050927; for now, only used by Save Selection
                type = "MMP"
                part.writemmpfile( safile) ###@@@ WRONG, stub... this writes a smaller file, unreadable before A5, with no saved view.
                #e also, that func needs to report errors; it probably doesn't now.
                ###e we need variant of writemmpfile_assy, but the viewdata will differ... pass it a map from partindex to part?
                # or, another way, better if it's practical: ###@@@ DOIT
                #   make a new assy (no shelf, same pov, etc) and save that. kill it at end.
                #   might need some code cleanups. what's done to it? worry about saver code reset_changed on it...
                msg = "Save Selection: not yet fully implemented; saved MMP file lacks viewpoint and gives warnings when read."
                # in fact, it lacks chunk/group structure and display modes too, and gets hydrogenated as if for sim!
                print msg
                env.history.message( orangemsg(msg) )
            elif ext == ".pdb": #bruce 050927; for now, only used by Save Selection
                type = "PDB"
                writepdb(part, safile)
            elif ext == ".pov":
                type = "POV-Ray"
                writepovfile(part, glpane, safile) #bruce 050927 revised arglist
            elif ext == ".mdl":
                type = "MDL"
                writemdlfile(part, glpane, safile) #bruce 050927 revised arglist
            elif ext == ".jpg":
                type = "JPEG"
                image = glpane.grabFrameBuffer()
                image.save(safile, "JPEG", 85)
                assert part is self.assy.part, "wrong image was saved" #bruce 050927
                assert self.assy.part is glpane.part, "wrong image saved since glpane not up to date" #bruce 050927
            elif ext == ".png":
                type = "PNG"
                image = glpane.grabFrameBuffer()
                image.save(safile, "PNG")
                assert part is self.assy.part, "wrong image was saved" #bruce 050927
                assert self.assy.part is glpane.part, "wrong image saved since glpane not up to date" #bruce 050927
            else: # caller passed in unsupported filetype (should never happen)
                saved = False
                env.history.message(redmsg( "File Not Saved. Unknown extension: " + ext))
        except:
            print_compact_traceback( "error writing file %r: " % safile )
            env.history.message(redmsg( "Problem saving %s file: " % type + safile ))
        else:
            if saved:
                env.history.message( "%s file saved: " % type + safile )
        return

    def save_mmp_file(self, safile): #bruce 050907 split this out of saveFile; maybe some of it should be moved back into caller ###@@@untested
        dir, fil, extjunk = fileparse(safile)
        try:
            tmpname = os.path.join(dir, '~' + fil + '.m~')
            self.assy.writemmpfile(tmpname)
        except:
            #bruce 050419 revised printed error message
            print_compact_traceback( "MWsemantics.py: saveFile(): error writing file [%s]: " % safile )
            env.history.message(redmsg( "Problem saving file: " + safile ))
            
            # If you want to see what was wrong with the MMP file, you
            # can comment this out so you can see what's in
            # the temp MMP file.  Mark 050128.
            if os.path.exists(tmpname):
                os.remove (tmpname) # Delete tmp MMP file
        else:
            if os.path.exists(safile):
                os.remove (safile) # Delete original MMP file
                #bruce 050907 suspects this is never necessary, but not sure;
                # if true, it should be removed, so there is never a time with no file at that filename.
                # (#e In principle we could try just moving it first, and only if that fails, try removing and then moving.)

            os.rename( tmpname, safile) # Move tmp file to saved filename.
            
            errorcode, oldPartFilesDir = self.assy.find_or_make_part_files_directory(make = False) # Mark 060703.
            if errorcode:
                # This code is guessing that the "error" is only that the old part_files_dir is not there.
                # If there is some other error, we need to print a history warning about it,
                # and then we can proceed as if the dir was not there. Printing that message is not implemented yet. ####@@@@
                # [bruce 060704 comment]
                oldPartFilesDir = None # Make sure we don't try to copy it.

            self.saved_main_file(safile, fil)

            env.history.message( "MMP file saved: " + self.assy.filename )
                #bruce 060704 moved this before copying part files,
                # which will now ask for permission before removing files,
                # and will start and end with a history message if it does anything.

            if oldPartFilesDir: #bruce 060704 revised this code
                errorcode, errortext = self.copy_part_files_dir(oldPartFilesDir) # Mark 060703. [only copies them if they exist]
                    #bruce 060704 will modify that function, e.g. to make it print a history message when it starts copying.
                if errorcode:
                    env.history.message( orangemsg("Problem copying part files: " + errortext ))
                else:
                    if debug_part_files:
                        env.history.message( _graymsg("debug: Success copying part files: " + errortext ))
            else:
                if debug_part_files:
                    env.history.message( _graymsg("debug: No part files to copy." ))
            
        return
    
    def copy_part_files_dir(self, oldPartFilesDir): # Mark 060703. NFR bug 2042. Revised by bruce 060704 for user safety, history.
        """Recursively copy the entire directory tree rooted at oldPartFilesDir to the assy's (new) Part Files directory.
        Return errorcode, message (message might be for error or for success, but is not needed for success except for debugging).
        Might also print history messages (and in future, maintain progress indicators) about progress.
        """
        set_waitcursor(True)
        if not oldPartFilesDir:
            set_waitcursor(False)
            return 0, "No part files directory to copy."
        
        errorcode, newPartFilesDir = self.assy.get_part_files_directory() # misnamed -- actually just gets its name
        if errorcode:
            set_waitcursor(False)
            return 1, "Problem getting part files directory name: " + newPartFilesDir
            
        if oldPartFilesDir == newPartFilesDir:
            set_waitcursor(False)
            return 0, "Nothing copied since the part files directory is the same."
        
        if os.path.exists(newPartFilesDir): 
            # Destination directory must not exist. copytree() will create it.
            # Assume the user was prompted and confirmed overwriting the MMP file, 
            # and thus its part files directory, so remove newPartFilesDir.
            
            #bruce 060704 revision -- it's far too dangerous to do this without explicit permission.
            # Best fix would be to integrate this permission with the one for overwriting the main mmp file
            # (which may or may not have been given at this point, in the current code --
            #  it might be that the newPartFilesDir exists even if the new mmp file doesn't).
            # For now, if no time for better code for A8, just get permission here. ###@@@
            if os.path.isdir(newPartFilesDir):
                if "need permission":
                    # ... confirm overwrite of the existing file. [code copied from another method above]
                    ret = QMessageBox.warning( self, self.name(), ###k what is self.name()?
                        "The Part Files directory for the copied mmp file,\n[" + newPartFilesDir + "], already exists.\n"\
                        "Do you want to overwrite this directory, or skip copying the Part Files from the old mmp file?\n"\
                        "(If you skip copying them now, you can rename this directory and copy them using your OS;\n"\
                        "if you don't rename it, the copied mmp file will use it as its own Part Files directory.)",
                        "&Overwrite", "&Skip", None,
                        0,      # Enter == button 0
                        1 )     # Escape == button 1

                    if ret==1: # The user wants to skip copying the part files
                        msg = "Not copying Part Files; preexisting Part Files directory at new name [%s] will be used unless renamed." % newPartFilesDir
                        env.history.message( orangemsg( msg ) )
                        return 0, "Nothing copied since user skipped overwriting existing part files directory"
                    else:
                        # even this could take a long time; and the user needs to have a record that we're doing it
                        # (in case they later realize it was a mistake).
                        msg = "Removing existing part files directory [%s]" % newPartFilesDir
                        env.history.message( orangemsg( msg ) )
                        env.history.h_update() # needed, since following op doesn't processEvents and might take a long time
                try:
                    shutil.rmtree(newPartFilesDir)
                except Exception, e:
                    set_waitcursor(False)
                    return 1, ("Problem removing an existing part files directory [%s]" % newPartFilesDir
                               + " - ".join(map(str, e.args)))
        
        # time to start copying; tell the user what's happening
        # [in future, ASAP, this needs to be abortable, and maybe have a progress indicator]
        ###e this ought to have a wait cursor; should grab code from e.g. SurfaceChunks
        msg = "Copying part files from [%s] to [%s]" % ( oldPartFilesDir, newPartFilesDir )
        env.history.message( msg )
        env.history.h_update() # needed
        
        try:
            shutil.copytree(oldPartFilesDir, newPartFilesDir)
        except Exception, e:
            eic.handle_exception()
            set_waitcursor(False)
            return 1, ("Problem copying files to the new parts file directory " + newPartFilesDir
                       + " - ".join(map(str, e.args)))

        set_waitcursor(False)
        env.history.message( "Done.")
        return 0, 'Part files copied from "' + oldPartFilesDir + '" to "' + newPartFilesDir + '"'

    def saved_main_file(self, safile, fil): #bruce 050907 split this out of mmp and pdb saving code
        """Record the fact that self.assy itself is now saved into (the same or a new) main file
        (and will continue to be saved into that file, until further notice)
        (as opposed to part or all of it being saved into some separate file, with no change in status of main file).
        Do necessary changes (filename, window caption, assy.changed status) and updates, but emit no history message.
        """
        # (It's probably bad design of pdb save semantics for it to rename the assy filename -- it's more like saving pov, etc.
        #  This relates to some bug reports. [bruce 050907 comment])
        # [btw some of this should be split out into an assy method, or more precisely a savable-object method #e]
        self.assy.filename = safile
        self.assy.name = fil
        self.assy.reset_changed() # The file and the part are now the same.
#                self.setCaption(self.trUtf8(self.name() + " - " + "[" + self.assy.filename + "]"))
        self._updateRecentFileList(safile)
            #bruce 050927 code cleanup: moved _updateRecentFileList here (before, it preceded each call of this method)        
        self.update_mainwindow_caption()
        self.mt.mt_update() # since it displays self.assy.name [bruce comment 050907; a guess]
            # [note, before this routine was split out, the mt_update happened after the history message printed by our callers]
        return
        
    def prepareToClose(self): #bruce 050907 split this out of MWsemantics.closeEvent method, added docstring
        """Prepare to close the main window and exit (e.g. ask user whether to save file if necessary).
        If user cancels, or anything else means we should not actually close and exit,
        return False; otherwise return True.
        """
        # wware 060406 bug 1263 - signal the simulator that we are exiting
        from runSim import SimRunner
        if not self.assy.has_changed():
            SimRunner.PREPARE_TO_CLOSE = True
            return True
        else:
            rc = QMessageBox.warning( self, self.name(),
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before exiting?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2

            if rc == 0:
                # Save
                isFileSaved = self.fileSave() # Save clicked or Alt+S pressed or Enter pressed.
                ##Huaicai 1/6/05: While in the "Save File" dialog, if user chooses
                ## "Cancel", the "Exit" action should be ignored. bug 300
                if isFileSaved:
                    SimRunner.PREPARE_TO_CLOSE = True
                    return True
                else:
                    return False
            elif rc == 1: # Discard
                SimRunner.PREPARE_TO_CLOSE = True
                return True
            else: # Cancel
                return False
        pass
            
    def closeEvent(self,ce): #bruce 050907 split this into two methods, revised docstring
        """slot method, called via File > Exit or clicking X titlebar button"""
        #bruce 090507 comment: this slot method should be moved back to MWsemantics.py.
        shouldEventBeAccepted = self.prepareToClose()
        if shouldEventBeAccepted:
            self.cleanUpBeforeExiting() #bruce 060127 added this re bug 1412 (defined in MWsemantics)
            ce.accept()
            ##self.periodicTable.close()
        else:
            ce.ignore()
            env.history.message("Cancelled exit.") # bruce 050907 added this message
        return

    def fileClose(self):
        
        env.history.message(greenmsg("Close File:"))
        
        isFileSaved = True
        if self.assy.has_changed():
            ret = QMessageBox.warning( self, self.name(),
                "The part contains unsaved changes.\n"
                "Do you want to save the changes before closing this part?",
                "&Save", "&Discard", "Cancel",
                0,      # Enter == button 0
                2 )     # Escape == button 2
            
            if ret==0: isFileSaved = self.fileSave() # Save clicked or Alt+S pressed or Enter pressed.
            elif ret==1:
                env.history.message("Changes discarded.")
            elif ret==2: 
                env.history.message("Cancelled.")
                return # Cancel clicked or Alt+C pressed or Escape pressed
        
        if isFileSaved: 
                self.__clear() # leaves glpane.mode as nullmode, as of 050911
                self.glpane.start_using_mode( '$STARTUP_MODE') #bruce 050911: File->Clear sets same mode as app startup does
                self.assy.reset_changed() #bruce 050429, part of fixing bug 413
                self.assy.clear_undo_stack() #bruce 060126, maybe not needed, or might fix an unreported bug related to 1398
                self.win_update()
        return

    def fileSetWorkDir(self):
        """Sets working directory"""

        env.history.message(greenmsg("Set Working Directory:"))
        
        wd = globalParms['WorkingDirectory']
        wdstr = "Current Working Directory - [" + wd  + "]"
        wd = QFileDialog.getExistingDirectory( wd, self, "get existing directory", wdstr, 1 )
        
        if not wd:
            env.history.message("Cancelled.")
            return
            
        if wd:
            wd = str(wd)
            wd = os.path.normpath(wd)
            globalParms['WorkingDirectory'] = wd
            
            env.history.message( "Working Directory set to " + wd )

            # bruce 050119: store this in prefs database so no need for ~/.ne1rc
            from preferences import prefs_context
            prefs = prefs_context()
            prefs['WorkingDirectory'] = wd
                
    def __clear(self): #bruce 050911 revised this: leaves glpane.mode as nullmode
        #bruce 050907 comment: this is only called from two file ops in this mixin, so I moved it here from MWsemantics
        # even though its name-mangled name was thereby changed. It should really be given a normal name.
        # Some comments in other files still call it MWsemantics.__clear. [See also the 060127 kluge below.]
        
        self.assy = assembly(self, "Untitled", own_window_UI = True) # own_window_UI is required for this assy to support Undo
            #bruce 060127 added own_window_UI flag to help fix bug 1403
        self.update_mainwindow_caption()
        self.glpane.setAssy(self.assy) # leaves glpane.mode as nullmode, as of 050911
        self.assy.mt = self.mt
        
        ### Hack by Huaicai 2/1 to fix bug 369
        self.mt.resetAssy_and_clear() 
        
        self.deleteMMKit() #mark 051215.  Fixes bug 1222 (was bug 961, item #4).
        return

    _MWsemantics__clear = __clear #bruce 060127 kluge so it can be called as __clear from inside class MWsemantics itself.
    
    def _updateRecentFileList(self, fileName):
        '''Add the <fileName> into the recent file list '''
        LIST_CAPACITY = 4 #This could be set by user preference, not added yet
        from MWsemantics import recentfiles_use_QSettings #bruce 050919 debug code #####@@@@@
            
        if recentfiles_use_QSettings:
            prefsSetting = QSettings()
            fileList = prefsSetting.readListEntry('/Nanorex/nE-1/recentFiles')[0]
        else:
            fileName = str(fileName)
            prefsSetting = preferences.prefs_context()
            fileList = prefsSetting.get('/Nanorex/nE-1/recentFiles', [])
        
        if len(fileList) > 0:
           if fileName == fileList[0]:
               return
           else:
               for ii in range(len(fileList)):
                   if fileList[ii] == fileName: ## Put this one at the top
                       del fileList[ii]
                       break
        
        if recentfiles_use_QSettings:
            fileList.prepend(fileName)
        else:
            fileList.insert(0, fileName)
            
        fileList = fileList[:LIST_CAPACITY]
        
        if recentfiles_use_QSettings:
            prefsSetting.writeEntry('/Nanorex/nE-1/recentFiles', fileList)
        else:
            prefsSetting['/Nanorex/nE-1/recentFiles'] = fileList 
        
        del prefsSetting
        
        self._createRecentFilesList()
        
        

    def _openRecentFile(self, idx):
        '''Slot method when user choose from the recently opened files submenu. '''
        from MWsemantics import recentfiles_use_QSettings #bruce 050919 debug code #####@@@@@
        if recentfiles_use_QSettings:
            prefsSetting = QSettings()
            fileList = prefsSetting.readListEntry('/Nanorex/nE-1/recentFiles')[0]
        else:
            prefsSetting = preferences.prefs_context()
            fileList = prefsSetting.get('/Nanorex/nE-1/recentFiles', [])
        
        assert idx <= len(fileList)
        
        selectedFile = str(fileList[idx])
        self.fileOpen(selectedFile)
        
        
    def _createRecentFilesList(self):
        '''Dynamically construct the list of recently opened files submenus '''
        from MWsemantics import recentfiles_use_QSettings #bruce 050919 debug code #####@@@@@
        
        if recentfiles_use_QSettings:
            prefsSetting = QSettings()
            fileList = prefsSetting.readListEntry('/Nanorex/nE-1/recentFiles')[0]
        else:
            prefsSetting = preferences.prefs_context()
            fileList = prefsSetting.get('/Nanorex/nE-1/recentFiles', [])
        
        self.recentFilePopupMenu = QPopupMenu(self)
        for ii in range(len(fileList)):
            self.recentFilePopupMenu.insertItem(qApp.translate("Main Window",  "&" + str(ii+1) + "  " + str(fileList[ii]), None), ii)
        
        menuIndex = self.RECENT_FILES_MENU_INDEX
        self.fileMenu.removeItemAt(menuIndex)
        self.fileMenu.insertItem(qApp.translate("Main Window", "Recent Files", None), self.recentFilePopupMenu, menuIndex, menuIndex)
        
        self.connect(self.recentFilePopupMenu, SIGNAL('activated (int)'), self._openRecentFile)
  

    pass # end of class fileSlotsMixin

# end


## Test code--By cleaning the recent files list of QSettings###
if __name__ == '__main__':
    prefs = QSettings()
    from qt import QStringList
    emptyList = QStringList()
    prefs.writeEntry('/Nanorex/nE-1/recentFiles', emptyList)
    
    
    del prefs
    
