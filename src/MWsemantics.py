import qt
from qt import QMainWindow, QPixmap, QWidget, QFrame, QPushButton
from qt import QGroupBox, QComboBox, QAction, QMenuBar, QPopupMenu
from qt import SIGNAL, QFileDialog
from GLPane import *
import os
import help
from runSim import runSim

from constants import *
from chem import fullnamePeriodicTable

from MainWindowUI import MainWindow
helpwindow = None
windowList = []


def fileparse(name):
    """breaks name into directory, main name, and extension in a tuple.
    fileparse('~/foo/bar/gorp.xam') ==> ('~/foo/bar/', 'gorp', '.xam')
    """
    m=re.match("(.*\/)*([^\.]+)(\..*)?",name)
    return ((m.group(1) or "./"), m.group(2), (m.group(3) or ""))

class MWsemantics(MainWindow):
    def __init__(self,parent = None, name = None, fl = 0):
	
        global windowList
        MainWindow.__init__(self, parent, name, fl)
        
        windowList += [self]
        if name == None:
            self.setName("Atom")

	# start with empty window
        self.assy = assembly(self, "Empty")

        self.frame4 = QFrame(self.centralWidget(),"frame4")
        self.frame4.setSizePolicy(QSizePolicy(3,3,0,0,False))
        self.frame4.setFrameShape(QFrame.NoFrame)
        self.frame4.setFrameShadow(QFrame.Plain)
        self.frame4Layout = QHBoxLayout(self.frame4,0,0,"frame4Layout")

        Form1Layout = QVBoxLayout(self.centralWidget(),11,6,"Form1Layout")
        Form1Layout.addWidget(self.frame4)

        self.modelTreeView.reparent(self.frame4, 0, QPoint(0,0), True)
        self.frame4Layout.addWidget(self.modelTreeView)
        self.modelTreeView.setSizePolicy(QSizePolicy(0,7,0,244,False))

        
        self.glpane = GLPane(self.assy, self.frame4, "glpane", self)   
        self.frame4Layout.addWidget(self.glpane)
        # do here to avoid a circular dependency
        self.assy.o = self.glpane

        self.setFocusPolicy(QWidget.StrongFocus)
        
        self.Element = 'C'
        self.elTab = [('C', Qt.Key_C, 0),
                      ('H', Qt.Key_H, 1),
                      ('O', Qt.Key_O, 2),
                      ('N', Qt.Key_N, 3),
                      ('B', Qt.Key_B, 4),
                      ('F', Qt.Key_F, 5),
                      ('Al', Qt.Key_A, 6),
                      ('Si', Qt.Key_I, 7),
                      ('P', Qt.Key_P, 8),
                      ('S', Qt.Key_S, 9),
                      ('Cl', Qt.Key_L, 10)]


    ###################################
    # functions from the "File" menu
    ###################################

    def fileNew(self):
        """If this window is empty (has no assembly), do nothing.
        Else create a new empty one.
        """
        foo = MWsemantics()
        foo.show()

    def fileOpen(self):
        self.clear()
        
        wd = globalParms['WorkingDirectory']
        fn = QFileDialog.getOpenFileName(wd, "Molecular machine parts (*.mmp);;Molecules (*.pdb);;Molecular parts assemblies (*.mpa);; All of the above (*.pdb *.mmp *.mpa)",
                                         self )
        fn = str(fn)
        if not os.path.exists(fn): return
        if fn[-3:] == "pdb":
            self.assy.readpdb(fn)
        if fn[-3:] == "mmp":
            self.assy.readmmp(fn)

        dir, fil, ext = fileparse(fn)
        self.assy.name = fil
        self.assy.filename = fn

        self.setCaption(self.trUtf8("Atom: " + self.assy.name))

        self.glpane.scale=self.assy.bbox.scale()
        self.glpane.paintGL()


    def fileSave(self):
        if self.assy:
            if self.assy.filename:
                fn = str(self.assy.filename)
                dir, fil, ext = fileparse(fn)
                self.assy.writemmp(dir + fil + ".mmp")
            else: self.fileSaveAs()

    def fileSaveAs(self):
        if self.assy:
            if self.assy.filename:
                dir, fil, ext = fileparse(self.assy.filename)
            else: dir, fil = "./", self.assy.name
            
	    fileDialog = QFileDialog(dir, "Molecular machine parts (*.mmp);;Molecules (*.pdb)",
                                     self, "Save File As", 1)
            if self.assy.filename:
                fileDialog.setSelection(fil)

            fileDialog.setMode(QFileDialog.AnyFile)
	    if fileDialog.exec_loop() == QDialog.Accepted:
            	fn = fileDialog.selectedFile()
            if fn:
                fn = str(fn)
                dir, fil, ext = fileparse(fn)
                ext = fileDialog.selectedFilter()
                ext = str(ext)
                if ext[-4:-1] == "mmp":
                    self.assy.writemmp(dir + fil + ".mmp")
                elif ext[-4:-1] == "pdb":
                    self.assy.writepdb(dir + fil + ".pdb")

    def fileImage(self):
        if self.assy:
            if self.assy.filename:
                fn = str(self.assy.filename)
                dir, fil, ext = fileparse(fn)
            else: dir, fil, ext = "./", "Picture", "jpg"
        fn = QFileDialog.getSaveFileName(dir + fil + ".jpg",
                                         "JPEG images (*.jpg *.jpeg",
                                         self )
        fn = str(fn)
        self.glpane.image(fn)

    def fileExit(self):
        pass

    def fileClear(self):
        self.__clear()
        self.glpane.paintGL()


    def fileClose(self):
        self.fileSave()
        self.__clear()

    def fileSetWorkDir(self):
	""" Sets working directory (need dialogue window) """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def __clear(self):
        self.glpane.assy = self.assy = assembly(self)
        self.assy.o = self.glpane


    ###################################
    # functions from the "Edit" menu
    ###################################

    def editUndo(self):
        print "MWsemantics.editUndo(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editRedo(self):
        print "MWsemantics.editRedo(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editCut(self):
        print "MWsemantics.editCut(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editCopy(self):
        print "MWsemantics.editCopy(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editPaste(self):
        print "MWsemantics.editPaste(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editFind(self):
        print "MWsemantics.editFind(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    ###################################
    # functions from the "Display" menu
    ###################################

    # GLPane.ortho is checked in GLPane.paintGL
    def viewOrtho(self):
        self.glpane.ortho = 1
        self.glpane.paintGL()

    def viewPerspec(self):
        self.glpane.ortho = 0
        self.glpane.paintGL()

    # set display formats in whatever is selected,
    # or the GLPane global default if nothing is
    def dispDefault(self):
        self.setDisplay(diDEFAULT)

    def dispInvis(self):
        self.setDisplay(diINVISIBLE)

    def dispVdW(self):
        self.setDisplay(diVDW)

    def dispTubes(self):
        self.setDisplay(diTUBES)

    def dispCPK(self):
        self.setDisplay(diCPK)

    def dispLines(self):
        self.setDisplay(diLINES)

    def setDisplay(self, form):
        if self.assy and self.assy.selatoms:
            for ob in self.assy.selatoms.itervalues():
                ob.setDisplay(form)
        elif self.assy and self.assy.selmols:
            for ob in self.assy.selmols:
                ob.setDisplay(form)
        else:
            if self.glpane.display == form: return
            self.glpane.setDisplay(form)
        self.glpane.paintGL()

    def setdisplay(self, a0):
        print 'setdisplay', a0


    # set the color of the selected part(s) (molecule)
    # or the background color if no part is selected.
    # atom colors cannot be changed singly
    def dispObjectColor(self):
        c = self.colorchoose()
        for ob in self.assy.selmols:
            ob.setcolor(c)
        self.glpane.paintGL()


    def dispBGColor(self):
        c = self.colorchoose()
        self.glpane.backgroundColor = c
        self.glpane.paintGL()

    def dispGrid(self):
        print "MWsemantics.dispGrid(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
        

    def gridGraphite(self):
        print "MWsemantics.gridGraphite(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    #######################################
    # functions from the "Orientation" menu
    #######################################

    # points of view corresponding to the three crystal
    # surfaces of diamond

    # along one axis
    def orient100(self):
        self.glpane.snapquat100()

    # halfway between two axes
    def orient110(self):
        self.glpane.snapquat110()

    # equidistant from three axes
    def orient111(self):
        self.glpane.snapquat111()

    # lots of things ???
    def orientView(self, a0=None):
        print "MainWindow.orientView(string):", a0


    # functions from the "Select" menu

    def selectAll(self):
        """Select all parts if nothing selected.
        If some parts are selected, select all atoms in those parts.
        If some atoms are selected, select all atoms in the parts
        in which some atoms are selected.
        """
        self.assy.selectAll()

    def selectNone(self):
        self.assy.selectNone()

    def selectInvert(self):
        """If some parts are selected, select the other parts instead.
        If some atoms are selected, select all currently unselected
        atoms in parts in which there are currently some selected atoms.
        (And unselect all currently selected atoms.)
        """
        self.assy.selectInvert()

    def selectConnected(self):
        """Select any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        """
        self.assy.selectConnected()


    def selectDoubly(self):
        """Select any atom that can be reached from any currently
        selected atom through two or more non-overlapping sequences of
        bonds. Also select atoms that are connected to this group by
        one bond and have no other bonds.
        """
        self.assy.selectDoubly()

    ###################################
    # Functions from the "Make" menu
    ###################################

    # these functions (do or will) create small structures that
    # describe records to send to the simulator
    # they don't do much in Atom itself
    def makeGround(self):
        self.assy.makeground()
        self.glpane.paintGL()

    def makeHandle(self):
        print "MWsemantics.makeHandle(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def makeMotor(self):
        self.assy.makemotor(self.glpane.lineOfSight)
        self.glpane.paintGL()

    def makeLinearMotor(self):
        self.assy.makeLinearMotor(self.glpane.lineOfSight)
        self.glpane.paintGL()


    def makeBearing(self):
        QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def makeSpring(self):
        QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
    def makeDyno(self):
        print "MWsemantics.makeDyno(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def makeHeatsink(self):
        print "MWsemantics.makeHeatsink(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    ###################################
    # functions from the "Modify" menu
    ###################################

    # change surface atom types to eliminate dangling bonds
    # a kludgey hack
    def modifyPassivate(self):
        self.assy.modifyPassivate()

    # add hydrogen atoms to each dangling bond
    def modifyHydrogenate(self):
        self.assy.modifyHydrogenate()

    # form a new part (molecule) with whatever atoms are selected
    def modifySeparate(self):
        self.assy.modifySeparate()

    ###################################
    # Functions from the "Help" menu
    ###################################

    def helpContents(self):
        global helpwindow
        if not helpwindow: helpwindow = help.Help()
        helpwindow.show()

    def helpIndex(self):
        print "MWsemantics.helpIndex(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
    def helpAbout(self):
        QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")


    ###############################################################
    # functions from the buttons down the right side of the display
    ###############################################################

    def toggleToolbar(self):
        print 'toggleToolbar'

    # set up cookiecutter mode
    def toolsCookieCut(self):
        self.glpane.setMode('COOKIE')

    # "push down" one nanometer to cut out the next layer
    def toolsCCAddLayer(self):
        if self.glpane.shape:
            self.glpane.pov -= self.glpane.shape.pushdown()
            self.glpane.paintGL()

    # fill the shape created in the cookiecutter with actual
    # carbon atoms in a diamond lattice (including bonds)
    # this works for all modes, not just add atom
    def toolsDone(self):
        self.glpane.mode.Done()

    def toolsStartOver(self):
        self.glpane.mode.Restart()

    def toolsBackUp(self):
        self.glpane.mode.Backup()

    def toolsCancel(self):
        self.glpane.mode.Flush()

    # turn on and off an "add atom with a mouse click" mode
    def addAtomStart(self):
        self.glpane.setMode('DEPOSIT')

    def toolsAtomStart(self):
        self.glpane.setMode('DEPOSIT')

    # the elements combobox:
    # change selected atoms to the element selected
##     def elemChange(self, string):
##         if self.assy.selatoms:
##             for a in self.assy.selatoms.itervalues():
##                 a.mvElement(fullnamePeriodicTable[str(string)])
##             self.glpane.paintGL()
##         else:
##             el = fullnamePeriodicTable[str(string)].symbol
##             self.setElement(el)

    def elemChange(self,a0):
        print "elemchange",a0

    def setCarbon(self):
        self.setElement("C")

    def setHydrogen(self):
        self.setElement("H")

    def setOxygen(self):
        self.setElement("O")

    def setNitrogen(self):
        self.setElement("N")

    def setBoron(self):
        self.setElement("B")

    def setElement(self, elt):
        # element specified as chemical symbol
        self.Element = elt
        for sym, key, num in self.elTab:
            if elt == sym: self.elemChangeComboBox.setCurrentItem(num)


    # Play a movie from the simulator
    def toolsMovie(self):
        dir, fil, ext = fileparse(self.assy.filename)
        self.glpane.startmovie(dir + fil + ".dpb")

    
    ###################################
    # some unimplemented buttons:
    ###################################

    # bring molecules together and bond unbonded sites
    def modifyWeldMolecule(self):
        print "MWsemantics.modifyWeldMolecule(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
 

    
    # create bonds where reasonable between selected and unselected
    def modifyEdgeBond(self):
        print "MWsemantics.modifyEdgeBond(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
        
    # create bonds where reasonable between selected and unselected
    def modifyAddBond(self):
        print "MWsemantics.modifyAddBond(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    # Turn on or off the axis icon
    def dispTrihedron(self):
        self.glpane.drawAxisIcon = not self.glpane.drawAxisIcon
        self.glpane.paintGL()

    # break bonds between selected and unselected atoms
    def modifyDeleteBond(self):
        print "MWsemantics.modifyDeleteBond(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    # Make a copy of the selected part (molecule)
    # cannot copy individual atoms
    def copyDo(self):
        self.assy.copy()
        self.glpane.paintGL()

    # 2BDone: make a copy of the selected part, move it, and bondEdge it,
    # having unselected the original and selected the copy.
    # the motion is to be the same relative motion done to a part
    # between copying and bondEdging it.
    def modifyCopyBond(self):
        print "MWsemantics.modifyCopyBond(): Not implemented yet"
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    # delete selected parts or atoms
    def killDo(self):
        self.assy.kill()
        self.glpane.paintGL()

    # utility functions

    def colorchoose(self):
        c = QColorDialog.getColor(QColor(100,100,100), self, "choose")
        return c.red()/256.0, c.green()/256.0, c.blue()/256.0


    def keyPressEvent(self, e):
        self.glpane.mode.keyPress(e.key())

    ##############################################################
    # Some future slot functions for the UI                      #
    ##############################################################

    def dispCsys(self):
	""" Toggle on/off center coordinate axes """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def dispDatumLines(self):
        """ Toggle on/off datum lines """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def dispDatumPlanes(self):
        """ Toggle on/off datum planes """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def dispOpenBonds(self):
        """ Toggle on/off open bonds """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def editPrefs(self):
        """ Edit square grid line distances(dx, dy, dz) in nm/angtroms """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
 
    def elemChangePTable(self):
        """ Future: element change via periodic table
        (only elements we support) """

    def modifyMinimize(self):
        """ Minimize """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")

    def toolsSimulator(self):
        self.simCntl = runSim(self.assy)
        self.simCntl.show()

    def viewFitToWindow(self):
        """ Fit to Window """
	QMessageBox.warning(self, "ATOM User Notice:", 
	         "This function is not implemented yet, coming soon...")
