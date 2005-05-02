# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
'''
bonds.py -- class Bond, for any supported type of chemical bond between two atoms
(one of which might be a "singlet" to represent an "open bond" in the UI),
and related code

TEMPORARILY OWNED BY BRUCE AS OF 050502 for introducing higher-valence bonds #####@@@@@

$Id$

History:

- originally by Josh

- lots of changes, by various developers

- split out of chem.py by bruce 050502

- support for higher-valence bonds added by bruce 050502 - ??? [ongoing]
'''
__author__ = "Josh"

# a lot of these imports might not be needed here in bonds.py,
# but note that as of 050502 they are all imported into chem.py (at end of that file)
# and everything from it is imported into some other modules.
# [bruce comment 050502] ###@@@

from VQT import *
from LinearAlgebra import *
import string
import re
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from drawer import *
from shape import *

from constants import *
from qt import *
from Utility import *
from MoleculeProp import *
from mdldata import marks, links, filler
from povheader import povpoint #bruce 050413

from debug import print_compact_stack, print_compact_traceback, compact_stack

import platform # for atom_debug; note that uses of atom_debug should all grab it
  # from platform.atom_debug since it can be changed at runtime

from elements import *

## no, better to use it directly so changeable at runtime:
## debug_bonds = platform.atom_debug #####@@@@@ DO NOT COMMIT with 1

# ==

class bondtype:
    """not implemented
    """
    pass
    # int at1, at2;    /* types of the elements */
    # num r0,ks;           /* bond length and stiffness */
    # num ediss;           /* dissociation (breaking) energy */
    # int order;            /* 1 single, 2 double, 3 triple */
    # num length;          // bond length from nucleus to nucleus
    # num angrad1, aks1;        // angular radius and stiffness for at1
    # num angrad2, aks2;        // angular radius and stiffness for at2

def bonded(a1, a2): #bruce 041119 #e optimized by bruce 050502 (this indirectly added "assert a1 != a2")
    "are these atoms (or singlets) already directly bonded?"
    ## return a2 in a1.neighbors()
    return not not find_bond(a1, a2)

def find_bond(a1, a2): #bruce 050502; there might be an existing function in some other file, to merge this with
    "If a1 and a2 are bonded, return their Bond object; if not, return None."
    assert a1 != a2
    for bond in a1.bonds:
        if bond.atom1 == a2 or bond.atom2 == a2:
            return bond
    return None

def bond_atoms_oldversion(at1,at2): #bruce 050502 renamed this from bond_atoms; it's called from the newer version of bond_atoms
    """Make a new bond between atoms at1 and at2 (and add it to their lists of bonds),
    if they are not already bonded; if they are already bonded do nothing. Return None.
    (The new bond object, if one is made, can't be found except by scanning the bonds
    of one of the atoms.)
       If at1 == at2, this is an error; print a warning and do nothing.
       This increases the number of bonds on each atom (when it makes a new bond) --
    it never removes any singlets. Therefore it is mostly for low-level use.
    It could be called directly, but is usually called via the method molecule.bond,
    purely for historical reasons.
    """
    # bruce 041109 split this out of molecule.bond. Since it's the only caller of
    # Bond.__init__, what it does to the atoms could (and probably should) be put
    # inside the constructor. However, it should not simply be replaced with calls
    # to the constructor, in case we someday want it to return the bond which it
    # either makes (as the constructor does) or doesn't make (when the atoms are
    # already bonded). The test for a prior bond makes more sense outside of the
    # Bond constructor.
    if at1 == at2: #bruce 041119, partial response to bug #203
        print "BUG: bond_atoms was asked to bond %r to itself." % at1
        print "Doing nothing (but further bugs may be caused by this)."
        print_compact_stack("stack when same-atom bond attempted: ")
        return

    b = Bond(at1,at2) # (this does all necessary invals)
    
    #bruce 041029 precautionary change -- I find in debugging that the bond
    # can be already in one but not the other of at1.bonds and at2.bonds,
    # as a result of prior bugs. To avoid worsening those bugs, we should
    # change this... but for now I'll just print a message about it.
    #bruce 041109: when this happens I'll now also remove the obsolete bond.
    if (b in at1.bonds) != (b in at2.bonds):
        print "fyi: debug: for new bond %r, (b in at1.bonds) != (b in at2.bonds); removing old bond" % b
        try:
            at1.bonds.remove(b)
        except:
            pass
        try:
            at2.bonds.remove(b)
        except:
            pass
    if not b in at2.bonds:
        at1.bonds += [b]
        at2.bonds += [b]
    else:
        # [bruce comment 041115: I don't know if this ever happens,
        #  or if it's a good idea for it to be allowed, but it is allowed.
        #  #e should it inval the old bond? I think so, but didn't add that.
        #  later: it happens a lot when entering Extrude; guess: mol.copy copies
        #  each internal bond twice (sounds right, but I did not verify this).]
        pass
        
    return

#bruce 050429: preliminary plan for higher-valence bonds (might need a better term for that):
#
# - Bond objects continue to compare equal when on same pair of atoms (even if they have a
# different valence), and (partly by means of this -- probably it's a kluge) they continue
# to allow only one Bond between any two atoms (two real atoms, or one real atom and one singlet).
#
# - I don't think we need to change anything basic about "internal vs external bonds",
# coordinates, basic inval/draw schemes (except to properly draw new kinds of bonds),
# etc. (Well, not due to bond valence -- we might change those things for other reasons.)
#
# - Each Bond object has a valence. Atoms often sum the valences of their bonds
# and worry about this, but they no longer "count their bonds" -- at least not as a
# substitute for summing the valences. (To prevent this from being done by accident,
# we might even decide that their list of bonds is not really a list, at least temporarily
# while this is being debugged. #?)
#
# This is the first time bonds have any state that needs to be saved,
# except for their existence between their two atoms. This will affect mmpfile read/write,
# copying of molecules (which needs rewriting anyway, to copy jigs/groups/atomsets too),
# lots of things about depositMode, maybe more.
#
# - Any bond object can have its valence change over time (just as the coords,
# elements, or even identities of its atoms can also change). This makes it a lot
# easier to write code which modifies chemical structures in ways which preserve (some)
# bonding but with altered valence on some bonds.
#
# - Atoms might decide they fit some "bonding pattern" and reorder
# their list of bonds into a definite order to match that pattern (this is undecided #?).
# This might mean that code which replaces one bond with a same-valence bond should do it
# in the same place in the list of bonds (no idea if we even have any such code #k).
#
# - We might also need to "invalidate an atom's bonding pattern" when we change anything
# it might care about, about its bonds or even its neighboring elements (two different flags). #?
#
# - We might need to permit atoms to have valence errors, either temporarily or permanently,
# and keep track of this. We might distinguish between "user-permitted" or even "user-intended"
# valence errors, vs "transient undesired" valence errors which we intend to automatically
# quickly get rid of. If valence errors can be long-lasting, we'll want to draw them somehow.
# 
# - Singlets still require exactly one bond (unless they've been killed), but it can have
# any valence. This might affect how they're drawn, how they consider forming new bonds
# (in extrude, fuse chunks, depositMode, etc), and how they're written into sim-input mmp files.
#
# - We represent the bond valence as an integer (6 times the actual valence), since we don't
# want to worry about roundoff errors when summing and comparing valences. (Nor to pay the speed
# penalty for using exactly summable python objects that pretend to have the correct numeric value.)
#
# An example of what we don't want to have to worry about:
#
#   >>> 1/2.0 + 1/3.0 + 1/6.0
#   0.99999999999999989
#   >>> _ >= 1.0
#   False
#
# We do guarantee to all code using these bond-valence constants that they can be subtracted
# and compared as numbers -- i.e. that they are "proportional" to the numeric valence.
# Some operations transiently create bonds with unsupported values of valence, especially bonds
# to singlets, and this is later cleaned up by the involved atoms when they update their bonding
# patterns, before those bonds are ever drawn. Except for bugs or perhaps during debugging,
# only standard-valence bonds will ever be drawn, or saved in files, or seen by most code.

# ==

# Bond valence constants -- exact ints, 6 times the numeric valence they represent.
# If these need an order, their standard order is the same as the order of their numeric valences
# (as shown here).  ###e move these into constants.py? maybe not...

V_SINGLE = 6 * 1
V_GRAPHITE = 6 * 4/3  # (this can't be written 6 * (1+1/3) or 6 * (1+1/3.0) - first one is wrong, second one is not an exact int)
V_AROMATIC = 6 * 3/2
V_DOUBLE = 6 * 2
V_TRIPLE = 6 * 3

BOND_VALENCES = [V_SINGLE, V_GRAPHITE, V_AROMATIC, V_DOUBLE, V_TRIPLE]
BOND_MMPRECORDS = ['bond1', 'bondg', 'bonda', 'bond2', 'bond3'] # some code assumes these all start with "bond"

BOND_LETTERS = ['?'] * (V_TRIPLE+1)
for v6,mmprec in zip(BOND_VALENCES,BOND_MMPRECORDS):
    BOND_LETTERS[v6] = mmprec[4] # '1','g',etc
BOND_LETTERS[0] = '0' # see comment in Bond.draw
BOND_LETTERS = "".join(BOND_LETTERS)
    ## print "BOND_LETTERS:",BOND_LETTERS # 0?????1?ga??2?????3

# == helper functions related to bonding (I might move these lower in the file #e)

def bond_atoms(a1, a2, vnew = None, s1 = None, s2 = None, no_corrections = False):
    """Bond atoms a1 and a2 by making a new bond of valence vnew (which must be one
    of the constants in chem.BOND_VALENCES, not a numerically expressed valence).
    The new bond is returned. If for some reason it can't be made, None is returned
    (but if that can happen, we should revise the API so an error message can be returned).
    Error if these two atoms are already bonded.
       If provided, s1 and s2 are the existing singlets on a1 and a2 (respectively)
    whose valence should be reduced (or eliminated, in which case they are deleted)
    to provide valence for the new bond. (If they don't have enough, other adjustments
    will be made; this function is free to alter, remove, or replace any existing
    singlets on either atom.)
       For now, this function will never alter the valence of any existing bonds
    to real atoms. If necessary, it will introduce valence errors on a1 and/or a2.
    (Or if they already had valence errors, it might remove or alter those.)
       If no_corrections = True, this function will not alter singlets on a1 or a2,
    but will either completely ignore issues of total valence of these atoms, or will
    limit itself to tracking valence errors or setting related flags (this is undecided).
    (This might be useful for code which builds new atoms rather than modifying
    existing ones, such as when reading mmp files or copying existing atoms.)
       vnew should always be provided (to get the behavior documented here).
    For backwards compatibility, when vnew is not provided, this function calls the
    old code [pre-higher-valence-bonds, pre-050502] which acts roughly as if
    vnew = V_SINGLE, s1 = s2 = None, no_corrections = True, except that it returns
    None rather than the newly made bond, and unlike this function doesn't mind
    if there's an existing bond, but does nothing in that case; this behavior might
    be relied on by the current code for copying bonds when copying a chunk, which
    might copy some of them twice.
       Using the old bond_atoms code by not providing vnew is deprecated,
    and might eventually be made impossible after all old calling code is converted
    for higher-valence bonds.
    """
    if vnew == None:
        assert s1 == s2 == None
        assert no_corrections == False
        bond_atoms_oldversion( a1, a2)
        return
    # quick hack for new version, using old version
    assert vnew in BOND_VALENCES
    assert not bonded(a1,a2)
    bond_atoms_oldversion(a1,a2)
    bond = find_bond(a1,a2) ###IMPLEM
    assert bond
    if vnew != V_SINGLE:
        bond.increase_valence_noupdate( vnew - V_SINGLE)
    if not no_corrections:
        if s1:
            s1.singlet_reduce_valence_noupdate(vnew)
        if s2:
            s2.singlet_reduce_valence_noupdate(vnew) ###k
        a1.update_valence() ###k
        a2.update_valence()
    return bond

def bond_v6(bond):
    "Return bond.v6. Useful in map, filter, etc."
    return bond.v6

# ==

#bruce 041109:
# Capitalized name of class Bond, so we can find all uses of it in the code;
# as of now there is only one use, in bond_atoms (used by molecule.bond).
# I also rewrote lots of the code in class Bond.

class Bond:
    """A Bond is essentially a record pointing to two atoms
    (either one of which might be a real atom or a "singlet"),
    representing a bond between them if it also occurs in atom.bonds
    for each atom. It should occur in both or neither of atom.bonds
    of its two atoms, except transiently.
       The two atoms in a bond should always be different objects.
       We don't support more than one bond between the same two
    atoms; trying to add the second one will do nothing, because
    of Bond.__eq__. We don't yet support double or triple bonds...
    but [bruce 050429 addendum] soon after Alpha 5 we'll start
    supporting those, and I'll start prototyping them right now --
    DO NOT COMMIT until post-Alpha5.
       Bonds have a private member 'key' so they can be compared equal
    whenever they involve the same pair of atoms (in either order).
       Bonds sometimes store geometric info used to draw them; see
    the method setup_invalidate, which must be called when the atoms
    are changed in certain ways. Bonds don't store any selection
    state or display-mode state, and they record no info about the
    bonded molecules (but each bonded atom knows its molecule).
       Bonds are called "external" if they connect atoms in two
    different molecules, or "internal" if they connect two atoms
    in the same molecule. This affects what kind of info is
    invalidated by the private method invalidate_bonded_mols, which
    should be called by internal code whenever the bond is actually
    added to or removed from its atoms
    (or is probably about to be added or removed).
       Bonds can be removed from their atoms by Bond.bust, and then
    forgotten about (no need to kill or otherwise explicitly destroy
    them after they're not on their atoms).
    """
    
    def __init__(self, at1, at2, v6 = V_SINGLE): # no longer also called from self.rebond()
        """create a bond from atom at1 to atom at2.
        the key created will be the same whichever order the atoms are
        given, and is used to compare bonds.
        [further comments by bruce 041029:]
        Private method (that is, creating of bond objects is private, for
        affected molecules and/or atoms). Note: the bond is not actually added
        to the atoms' molecules! Caller must do that. But [new feature 041109]
        we will do all necessary invalidations, in case the new bond is indeed
        added to those atoms (as I think it always will be in the current code).
        """
        self.atom1 = at1 ###k are these public attributes? For now I'll assume yes. [bruce 050502]
        self.atom2 = at2
        self.v6 = v6 # bond-valence times 6, as exact int; a public attribute
        assert v6 in BOND_VALENCES
        ## self.picked = 0 # bruce 041029 removed this since it seems unused
        self.changed_atoms()
        self.invalidate_bonded_mols() #bruce 041109 new feature

    def set_v6(self, v6):
        assert v6 in BOND_VALENCES
        self.v6 = v6
        #e update geometric things?? tell the atoms too??
        if self.atom1.molecule == self.atom2.molecule:
            # we're in that molecule's display list
            self.atom1.molecule.changeapp(0)
        return

    def numeric_valence(self): # has a long name so you won't be tempted to use it when you should use .v6
        return self.v6 / 6.0
    
    def changed_atoms(self):
        """Private method to call when the atoms assigned to this bond are changed.
        WARNING: does not call setup_invalidate(), though that would often also
        be needed, as would invalidate_bonded_mols() both before and after the change.
        """
        at1 = self.atom1
        at2 = self.atom2
        assert at1 != at2
        self.key = 65536*min(at1.key,at2.key)+max(at1.key,at2.key)
        #bruce 050317: debug warning for interpart bonds, or bonding killed atoms/chunks,
        # or bonding to chunks not yet added to any Part (but not warning about internal
        # bonds, since mol.copy makes those before a copied chunk is added to any Part).
        #   This covers new bonds (no matter how made) and the .rebond method.
        #   Maybe this should be an actual error, or maybe it should set a flag so that
        # involved chunks are checked for interpart bonds when the user event is done
        # (in case caller plans to move the chunks into the same part, but hasn't yet).
        # It might turn out this happens a lot (and is not a bug), if callers make a
        # new chunk, bond to it, and only then add it into the tree of Nodes.
        if platform.atom_debug and at1.molecule != at2.molecule:
            if (not at1.molecule.assy) or (not at2.molecule.assy):
                print_compact_stack( "atom_debug: bug?: bonding to a killed chunk(?); atoms are: %r, %r" % (at1,at2))
            elif (not at1.molecule.part) or (not at2.molecule.part): # assume false means None, maybe untrue if bugs happen
                if 0: #bruce 050321 this happens a lot when reading an mmp file, so disable it for now
                    print_compact_stack( "atom_debug: bug or fyi: one or both Parts None when bonding atoms: %r, %r" % (at1,at2))
            elif at1.molecule.part != at2.molecule.part:
                print_compact_stack( "atom_debug: likely bug: bonding atoms whose parts differ: %r, %r" % (at1,at2))
        return
    
    def invalidate_bonded_mols(self): #bruce 041109
        """Private method to call when a bond is made or destroyed;
        knows which kinds of bonds are put into a display list by molecule.draw
        (internal bonds) or put into into mol.externs (external bonds),
        though this knowledge should ideally be private to class molecule.
        """
        # assume mols are not None (they might be _nullMol, that's ok)
        mol1 = self.atom1.molecule
        mol2 = self.atom2.molecule
        if mol1 != mol2:
            # external bond
            mol1.invalidate_attr('externs')
            mol2.invalidate_attr('externs')
        else:
            # internal bond
            mol1.havelist = 0
        return

    def setup_invalidate(self):
        """Semi-private method for bonds. Invalidates cached geometric values
        related to drawing the bond.
         This must be called whenever the position or element of either bonded
        atom is changed, or when either atom's molecule changes if this affects
        whether it's an external bond (since the coordinate system used for drawing
        is different in each case).
         (FYI: It need not be called for other changes that might affect bond
        appearance, like disp or color of bonded molecules, though for internal
        bonds, the molecule's .havelist should be reset when those things change.)
          Note that before the "inval/update" revisions [bruce 041104],
        self.setup() (the old name for this method, from point of view of callers)
        did the recomputation now done on demand by __setup_update; now this method
        only does the invalidation which makes sure that recomputation will happen
        when it's needed.
        """
        # just delete all the attrs recomputed by self.__setup_update()
        try:
            del self.c1
        except AttributeError:
            pass # assume other attrs are also not there
        else:
            # assume other attrs are also there
            del self.c2, self.center, self.a1pos, self.a2pos, self.toolong
        # For internal bonds, or bonds that used to be internal,
        # callers need to have reset havelist of affected mols,
        # but the changes in atoms that required them to call setup_invalidate
        # mean they should have done that anyway (except for bond making and
        # breaking, in this file, which does this in invalidate_bonded_mols).
        # Bruce 041207 scanned all callers and concluded they do this as needed,
        # so I'm removing the explicit resets of havelist here, which were often
        # more than needed since they hit both mols of external bonds.
        # This change might speed up some redraws, esp. in move or deposit modes.
        return

    def __setup_update(self):
        """Private method. Before bruce 041104 this was called self.setup()
        and was called more widely; now the method of that name just invalidates
        the same attrs we recompute, by deleting them.
           This method is only called by __getattr__ when we need to recompute one
        or more of certain attributes, to set up the bond for drawing, or to
        compute the unbonding point with bond.ubp() (used to make replacement
        singlets in atom.unbond and atom.kill methods, even if they'll be
        discarded right away as all atoms in some big chunk are killed 1 by 1).
           We store all attributes we compute in the same coordinate system,
        which is mol-relative (basecenter/quat) for internal bonds, but absolute
        for external bonds.
           The specific attributes we recompute (and set, until next invalidated)
        are: a1pos, a2pos (positions of the atoms); c1, c2, and center (points
        along the bond useful for drawing it); toolong (flag) saying whether bond
        is too long. (Before 041112 there was no toolong flag, but center was None
        for long bonds.)
           As of 041201 we'll no longer recompute atpos or basepos if they are
        invalid, so that atom.kill (our caller via unbond and ubp), which
        invalidates them, won't also recompute them.
        """
        # [docstring revised, and inval/update scheme added, by bruce 041104]
        # [docstring improved, and code revised to not recompute basepos, 041201]
        if self.atom1.molecule != self.atom2.molecule:
            # external bond; use absolute positions for all attributes.
            self.a1pos = self.atom1.posn()
            self.a2pos = self.atom2.posn()
        else:
            # internal bond; use mol-relative positions for all attributes.
            # Note 1: this means any change to mol's coordinate system
            # (basecenter and quat) requires calling setup_invalidate
            # in this bond! That's a pain (and inefficient), so I might
            # replace it by a __getattr__ mol-coordsys-version-number check...
            # ##e [bruce 041115]
            self.a1pos = self.atom1.baseposn()
            self.a2pos = self.atom2.baseposn()
        vec = self.a2pos - self.a1pos
        leng = 0.98 * vlen(vec)
        vec = norm(vec)
        # (note: as of 041217 rcovalent is always a number; it's 0.0 for Helium,
        #  etc, so the entire bond is drawn as if "too long".)
        rcov1 = self.atom1.element.rcovalent
        rcov2 = self.atom2.element.rcovalent
        self.c1 = self.a1pos + vec*rcov1
        self.c2 = self.a2pos - vec*rcov2
        self.toolong = (leng > rcov1 + rcov2)
        self.center = (self.c1 + self.c2) / 2.0 # before 041112 this was None when self.toolong
        return

    def __getattr__(self, attr): # bond.__getattr__ #bruce 041104
        """Called when one of the attrs computed by self.__setup_update() is
        needed, but was not yet computed or was deleted since last computed
        (as our way of invalidating it). Also might be called for an arbitrary
        missing attr due to a bug in the calling code. Now that this __getattr__
        method exists, no other calls of self.__setup_update() should be needed.
        """
        if attr[0] == '_' or (not attr in ['a1pos','a2pos','c1','c2','center','toolong']):
            # unfortunately (since it's slow) we can't avoid checking this first,
            # or we risk infinite recursion due to a missing attr needed by setup
            raise AttributeError, attr # be fast since probably common for __xxx__
        self.__setup_update() # this should add the attribute (or raise an exception
          # if it's called too early while initing the bond or one of its molecules)
        return self.__dict__[attr] # raise exception if attr still missing

    def other(self, atm):
        """Given one atom the bond is connected to, return the other one
        """
        if self.atom1 == atm: return self.atom2
        assert self.atom2 == atm #bruce 041029
        return self.atom1

    def othermol(self, mol): #bruce 041123; not yet used or tested
        """Given the molecule of one atom of this bond, return the mol
        of the other one. Error if mol is not one of the bonded mols.
        Note that this implies that for an internal bond within mol,
        the input must be mol and we always return mol.
        """
        if mol == self.atom1.molecule:
            return self.atom2.molecule
        elif mol == self.atom2.molecule:
            return self.atom1.molecule
        else:
            assert mol in [self.atom1.molecule, self.atom2.molecule]
            # this always fails -- it's just our "understandable error message"
        pass
    
    def ubp(self, atom):
        """ unbond point (atom must be one of the bond's atoms) """
        #bruce 041115 bugfixed this for when mol.quat is not 1,
        # tho i never looked for or saw an effect from the bug in that case
        if atom == self.atom1:
            point = self.c1 # this might call self.__setup_update()
        else:
            assert atom == self.atom2
            point = self.c2
        # now figure out what coord system that's in
        if self.atom1.molecule != self.atom2.molecule:
            return point
        else:
            # convert to absolute position for caller
            # (note: this never recomputes basepos/atpos or modifies the mol-
            #  relative coordinate system)
            return self.atom1.molecule.base_to_abs(point)
        pass

    # "break" is a python keyword
    def bust(self):
        """Destroy this bond, modifying the bonded atoms as needed
        (by adding singlets in place of this bond -- they might overlap!),
        and invalidating the bonded molecules as needed.
        Return the added singlets as a 2-tuple.
        (This method is named 'bust' since 'break' is a python keyword.)
        If either atom is a singlet, kill that atom.
        (Note: as of 041115 bust is never called with either atom a singlet.
        If it ever is, retval remains a 2-tuple but has None in 1 or both
        places ... precise effect needs review in that case.)
        """
        # bruce 041115: bust is never called with either atom a singlet,
        # but since atom.unbond now kills singlets lacking any bonds,
        # and since not doing that would be bad, I added a note about that
        # to the docstring.
        x1 = self.atom1.unbond(self) # does all needed invals
        x2 = self.atom2.unbond(self)
        ###e do we want to also change our atoms and key to None, for safety?
        ###e check all callers and decide
        return x1, x2 # retval is new feature, bruce 041222
    
    def rebond(self, old, new):
        """Self is a bond between old (typically a singlet) and some atom A;
        replace old with new in this same bond (self),
        so that old no longer bonds to A but new does.
        Unlike some other bonding methods, the number of bonds on new increases
        by 1, since no singlet on new is removed -- new is intended to be
        a just-created atom, not one with the right number of existing bonds.
        If old is a singlet, then kill it since it now has no bonds.
        Do the necessary invalidations in self and all involved molecules.
           Warning: this can make a duplicate of an existing bond (so that
        atoms A and B are connected by two equal copies of a bond). That
        situation is an error, not supported by the code as of 041203,
        and is drawn exactly as if it was a single bond. Avoiding this is
        entirely up to the caller.
        """
        # [bruce 041109 added docstring and rewrote Josh's code:]
        # Josh said: intended for use on singlets, other uses may have bugs.
        # bruce 041109: I think that means "old" is intended to be a singlet.
        # I will try to make it safe for any atoms, and do all needed invals.
        if self.atom1 == old:
            old.unbond(self) # also kills old if it's a singlet, as of 041115
            ## if len(old.bonds) == 1: del old.molecule.atoms[old.key] --
            ## the above code removed the singlet, old, without killing it.
            self.atom1 = new
        elif self.atom2 == old:
            old.unbond(self)
            self.atom2 = new
        else:
            print "fyi: bug: rebond: %r doesn't contain atom %r to replace with atom %r" % (self, old, new)
            # no changes in the structure
            return
        # bruce 041109 worries slightly about order of the following:
        # invalidate this bond itself
        self.changed_atoms()
        self.setup_invalidate()
        # add this bond to new (it's already on A, i.e. in the list A.bonds)
        new.bonds += [self]
            #e put this in some private method on new, new.add_new_bond(self)??
            #  Note that it's intended to increase number of bonds on new,
            #  not to zap a singlet already bonded to new.
        # Invalidate molecules (of both our atoms) as needed, due to our existence
        self.invalidate_bonded_mols()
        if 1:
            # This debug code helped catch bug 232, but seems useful in general:
            # warn if this bond is a duplicate of an existing bond on A or new.
            # (Usually it will have the same count on each atom, but other bugs
            #  could make that false, so we check both.) [bruce 041203]
            A = self.other(new)
            if A.bonds.count(self) > 1:
                print "rebond bug (%r): A.bonds.count(self) == %r" % (self, A.bonds.count(self))
            if new.bonds.count(self) > 1:
                print "rebond bug (%r): new.bonds.count(self) == %r" % (self, new.bonds.count(self))
        return

    def __eq__(self, ob):
        return ob.key == self.key

    def __ne__(self, ob):
        # bruce 041028 -- python doc advises defining __ne__
        # whenever you define __eq__
        return not self.__eq__(ob)

    def draw(self, glpane, dispdef, col, level):
        """Draw the bond. Note that for external bonds, this is called twice,
        once for each bonded molecule (in arbitrary order)
        (and is never cached in either mol's display list);
        each of these calls gets dispdef, col, and level from a different mol.
        [bruce, 041104, thinks that leads to some bugs in bond looks.]
        Bonds are drawn only in certain display modes (CPK, LINES, TUBES).
        The display mode is inherited from the atoms or molecule (as passed in
         via dispdef from the calling molecule -- this might cause bugs if some
         callers change display mode but don't set havelist = 0, but maybe they do).
        Lines or tubes change color from atom to atom, and are red in the middle
        for long bonds. CPK bonds are drawn in the calling molecule's color or
        in the constant bondColor (which is light gray).
        """
        #bruce 041104 revised docstring, added comments about possible bugs.
        # Note that this code depends on finding the attrs toolong, center,
        # a1pos, a2pos, c1, c2, as created by self.__setup_update().
        # As of 041109 this is now handled by bond.__getattr__.
        # The attr toolong is new as of 041112.
        
        color1 = col or self.atom1.element.color
        color2 = col or self.atom2.element.color

        disp=max(self.atom1.display, self.atom2.display)
        if disp == diDEFAULT: disp= dispdef
        if disp == diLINES:
            if not self.toolong:
                drawline(color1, self.a1pos, self.center)
                drawline(color2, self.a2pos, self.center)
            else:
                drawline(color1, self.a1pos, self.c1)
                drawline(color2, self.a2pos, self.c2)
                drawline(red, self.c1, self.c2)
        if disp == diCPK:
            drawcylinder(col or bondColor, self.a1pos, self.a2pos, 0.1)
        if disp == diTUBES:
            v1 = self.atom1.display != diINVISIBLE
            v2 = self.atom2.display != diINVISIBLE
            ###e bruce 041104 suspects v1, v2 wrong for external bonds, needs
            # to look at each mol's .hidden (but this is purely a guess)
            if not self.toolong:
                if v1:
                    drawcylinder(color1, self.a1pos, self.center, TubeRadius)
                if v2:
                    drawcylinder(color2, self.a2pos, self.center, TubeRadius)
                if not (v1 and v2):
                    drawsphere(black, self.center, TubeRadius, level)
#                print "draw: bond 1---2: ", self.a1pos, self.a2pos    
            else:
                drawcylinder(red, self.c1, self.c2, TubeRadius)
#                print "draw: bond c1--c2: ", self.c1, self.c2    
                if v1:
                    drawcylinder(color1, self.a1pos, self.c1, TubeRadius)
#                    print "draw: bond a1---c1: ", self.a1pos, self.c1    
                else:
                    drawsphere(black, self.c1, TubeRadius, level)
                if v2:
                    drawcylinder(color2, self.a2pos, self.c2, TubeRadius)
#                    print "draw: bond a2---c2: ", self.a2pos, self.c2    
                else:
                    drawsphere(black, self.c2, TubeRadius, level)
        if self.v6 != V_SINGLE or platform.atom_debug: # debug_bonds #####@@@@@
            glDisable(GL_LIGHTING)
            ## glDisable(GL_DEPTH_TEST)
            glPushMatrix()
            font = QFont( QString("Times"), 10)#QFont(QString("Helvetica"), 12, QFont.Normal) ###E optimize this, keep in glpane
            glpane.qglColor(QColor(75, 75, 75))
            p = self.center + glpane.out * 0.6
                ###WRONG -- depends on rotation when display list is made! But quite useful for now.
            v6 = self.v6
            try:
                ltr = BOND_LETTERS[v6]
                    # includes special case of '0' for v6 == 0,
                    # which should only show up for transient states that are never drawn, except in case of bugs
            except IndexError: # should only show up for transient states...
                if v6 < 0:
                    ltr = '-'
                else:
                    ltr = '+'
            glpane.renderText(p[0], p[1], p[2], QString(ltr), font) #k need explicit QString??
            glPopMatrix()
            ## glEnable(GL_DEPTH_TEST)
            glEnable(GL_LIGHTING)
        return # from Bond.draw

    # write to a povray file:  draw a single bond [never reviewed by bruce]
    # [note: this redundantly computes attrs like __setup_update computes for
    #  draw, and instead we should just use those attrs, but I did not make
    #  this change since there is a current bug report which someone might
    #  fix by altering povpoint and the V(1,1,-1) kluges in here,
    #  and I want to avoid a cvs merge conflict. When this is fixed,
    #  note that I have changed self.center and added self.toolong; see
    #  self.draw() for details. -- bruce 041112 ###e]
    def writepov(self, file, dispdef, col):
       ##Huaicai 1/15/05: It seems the attributes from __setup__update() is not correct,
       ## at least for pov file writing, so compute it here locally. To fix bug 346,347
        disp=max(self.atom1.display, self.atom2.display)
        if disp == diDEFAULT: disp= dispdef
        color1 = col or self.atom1.element.color
        color2 = col or self.atom2.element.color
        
        a1pos = self.atom1.posn()
        a2pos = self.atom2.posn()
        
        vec = a2pos - a1pos
        leng = 0.98 * vlen(vec)
        vec = norm(vec)
        # (note: as of 041217 rcovalent is always a number; it's 0.0 for Helium,
        #  etc, so the entire bond is drawn as if "too long".)
        rcov1 = self.atom1.element.rcovalent
        rcov2 = self.atom2.element.rcovalent
        c1 = a1pos + vec*rcov1
        c2 = a2pos - vec*rcov2
        toolong = (leng > rcov1 + rcov2)
        center = (c1 + c2) / 2.0 # before 041112 this was None when self.toolong
        
        
        if disp<0: disp= dispdef
        if disp == diLINES:
            file.write("line(" + povpoint(a1pos) +
                       "," + povpoint(a2pos) + ")\n")
        if disp == diCPK:
            file.write("bond(" + povpoint(a1pos) +
                       "," + povpoint(a2pos) + ")\n")
        if disp == diTUBES:
        ##Huaicai: If rcovalent is close to 0, like singlets, avoid 0 length 
        ##             cylinder written to a pov file    
            DELTA = 1.0E-5
            isSingleCylinder = False
            if  self.atom1.element.rcovalent < DELTA:
                    col = color2
                    isSingleCylinder = True
            if  self.atom2.element.rcovalent < DELTA:
                    col = color1
                    isSingleCylinder = True
            if isSingleCylinder:        
                file.write("tube3(" + povpoint(a1pos) + ", " + povpoint(a2pos) + ", " + stringVec(col) + ")\n")
            else:      
                if not self.toolong:
                        file.write("tube2(" + povpoint(a1pos) +
                           "," + stringVec(color1) +
                           "," + povpoint(center) + "," +
                           povpoint(a2pos) + "," +
                           stringVec(color2) + ")\n")
                else:
                        file.write("tube1(" + povpoint(a1pos) +
                           "," + stringVec(color1) +
                           "," + povpoint(c1) + "," +
                           povpoint(c2) + "," + 
                           povpoint(a2pos) + "," +
                           stringVec(color2) + ")\n")

    def __str__(self):
        return str(self.atom1) + " <--> " + str(self.atom2)

    def __repr__(self):
        return str(self.atom1) + "::" + str(self.atom2)

    pass # end of class Bond

# end of bonds.py
