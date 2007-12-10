# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
packageData.py -- data about modules and packages, for PackageDependency.py

@author: Eric M
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

packageColors = {
    "ui"          : "#8050ff",
    "PM"          : "#8070ff",
    "graphics"    : "#80a0ff",

    "model"       : "#80ff50",
    "foundation"  : "#80ff70",
    "exprs"       : "#80ffa0",

    "io"          : "#ffff80",
    "utilities"   : "#ffa080",

    "examples"    : "#ff3030",
    "test"        : "#ff3060",
    "top"         : "#ff3090",
    }

packageLevels = {
    "top"         : 7,
    "test"        : 7,
    "examples"    : 7,
    "ui"          : 6,
    "PM"          : 6,
    "io"          : 5,
    "model"       : 4,
    "graphics"    : 4,
    "foundation"  : 3,
    "exprs"       : 3,
    "geometry"    : 3,
    "utilities"   : 2,
    "platform"    : 1,
    }

packageMapping = {
    "assembly"                     : "model",
    "Assembly_API"                 : "?",
    "AtomGenerator"                : "ui",
    "AtomGeneratorPropertyManager" : "ui",
    "atomtypes"                    : "model",
    "bonds"                        : "model",
    "bonds_from_atoms"             : "model",
    "bond_chains"                  : "model",
    "bond_constants"               : "model",
    "bond_drawer"                  : "graphics",
    "bond_updater"                 : "model",
    "bond_utils"                   : "model",
    "BoundingBox"                  : "?",
    "BuildAtomsPropertyManager"    : "ui",
    "build_utils"                  : "ui",
    "changedicts"                  : "?",
    "changes"                      : "foundation",
    "chem"                         : "model",
    "chem_patterns"                : "model",
    "chunk"                        : "model",
    "ChunkProp"                    : "ui",
    "ChunkPropDialog"              : "ui",
    "CmdMgr_Constants"             : "ui",
    "Command"                      : "ui",
    "CommandManager"               : "ui",
    "CommandSequencer"             : "ui",
    "Comment"                      : "model",
    "CommentProp"                  : "ui",
    "CommentPropDialog"            : "ui",
    "confirmation_corner"          : "ui",
    "constants"                    : "utilities",
    "CoNTubGenerator"              : "ui",
    "CookieCtrlPanel"              : "ui",
    "cookieMode"                   : "ui",
    "CookiePropertyManager"        : "ui",
    "crossovers"                   : "model",
    "Csys"                         : "?",
    "cursors"                      : "ui",
    "CylinderChunks"               : "graphics",
    "debug"                        : "utilities",
    "DebugMenuMixin"               : "ui",
    "debug_prefs"                  : "utilities",
    "depositMode"                  : "ui",
    "dimensions"                   : "graphics",
    "DirectionArrow"               : "ui",
    "displaymodes"                 : "ui",
    "Dna"                          : "model",
    "DnaDuplex"                    : "?",
    "DnaDuplexEditController"      : "?",
    "DnaDuplexPropertyManager"     : "?",
    "DnaGenerator"                 : "ui",
    "DnaGeneratorPropertyManager"  : "ui",
    "DnaLineMode"                  : "?",
    "Dna_Constants"                : "model",
    "DragHandler"                  : "ui",
    "drawer"                       : "graphics",
    "draw_bond_vanes"              : "graphics",
    "draw_grid_lines"              : "?",
    "DynamicTip"                   : "ui",
    "EditController"               : "ui",
    "EditController_PM"            : "ui",
    "Elem"                         : "?",
    "elementColors"                : "ui",
    "ElementColorsDialog"          : "ui",
    "elements"                     : "model",
    "elementSelector"              : "ui",
    "ElementSelectorDialog"        : "ui",
    "elements_data"                : "?",
    "elements_data_PAM3"           : "?",
    "elements_data_PAM5"           : "?",
    "EndUser"                      : "utilities",
    "env"                          : "utilities",
    "ESPImageProp"                 : "ui",
    "ESPImagePropDialog"           : "ui",
    "example_expr_command"         : "examples",
    "ExecSubDir"                   : "?",
    "extensions"                   : "top_level",
    "extrudeMode"                  : "ui",
    "ExtrudePropertyManager"       : "ui",
    "fileIO"                       : "io",
    "files_gms"                    : "io",
    "files_mmp"                    : "io",
    "files_nh"                     : "io",
    "files_pdb"                    : "io",
    "Font3D"                       : "?",
    "fusechunksMode"               : "ui",
    "FusePropertyManager"          : "ui",
    "GamessJob"                    : "io",
    "GamessProp"                   : "ui",
    "GamessPropDialog"             : "ui",
    "GeneratorBaseClass"           : "ui",
    "GeneratorController"          : "ui",
    "generator_button_images"      : "ui",
    "geometry"                     : "geometry",
    "GlobalPreferences"            : "utilities",
    "global_model_changedicts"     : "?",
    "GLPane"                       : "graphics",
    "GLPane_minimal"               : "graphics",
    "gpl_only"                     : "platform",
    "GrapheneGenerator"            : "ui",
    "GrapheneGeneratorPropertyManager" : "ui",
    "GraphicsMode"                 : "ui",
    "GraphicsMode_API"             : "?",
    "GridPlaneProp"                : "ui",
    "GridPlanePropDialog"          : "ui",
    "GROMACS"                      : "io",
    "Group"                        : "foundation", # some model code?
    "GroupButtonMixin"             : "ui",
    "GroupProp"                    : "ui",
    "GroupPropDialog"              : "ui",
    "handles"                      : "ui",
    "help"                         : "ui",
    "HelpDialog"                   : "ui",
    "HistoryWidget"                : "ui",
    "icon_utilities"               : "io",
    "ImageUtils"                   : "io",
    "_import_roots"                : "top_level",
    "Initialize"                   : "utilities",
    "inval"                        : "foundation",
    "jigmakers_Mixin"              : "?",
    "JigProp"                      : "ui",
    "JigPropDialog"                : "ui",
    "jigs"                         : "model",
    "jigs_measurements"            : "model",
    "jigs_motors"                  : "model",
    "jigs_planes"                  : "model",
    "jig_Gamess"                   : "model",
    "JobManager"                   : "ui",
    "JobManagerDialog"             : "ui",
    "Line"                         : "ui", # geometry, model?
    "LinearMotorEditController"    : "ui",
    "LinearMotorPropertyManager"   : "ui",
    "LineMode"                     : "?",
    "main"                         : "top_level",
    "MainWindowUI"                 : "ui",
    "master_model_updater"         : "?",
    "mdldata"                      : "io",
    "MinimizeEnergyProp"           : "ui",
    "MinimizeEnergyPropDialog"     : "ui",
    "modelTree"                    : "ui",
    "modelTreeGui"                 : "ui",
    "modes"                        : "ui",
    "modifyMode"                   : "ui",
    "MotorPropertyManager"         : "ui",
    "MovePropertyManager"          : "ui",
    "movie"                        : "ui", # mixture of stuff
    "moviefile"                    : "io",
    "movieMode"                    : "ui",
    "MoviePropertyManager"         : "ui",
    "MWsemantics"                  : "ui",
    "NanoHive"                     : "ui",
    "NanoHiveDialog"               : "ui",
    "NanoHiveUtils"                : "io",
    "NanotubeGenerator"            : "ui",
    "NanotubeGeneratorPropertyManager" : "ui",
    "NE1ToolBar"                   : "ui",
    "Node_as_MT_DND_Target"        : "?",
    "node_indices"                 : "foundation",
    "objectBrowse"                 : "?",
    "ops_atoms"                    : "model",
    "ops_connected"                : "model",
    "ops_copy"                     : "model", # parts may be foundation
    "ops_files"                    : "io",
    "ops_motion"                   : "model",
    "ops_rechunk"                  : "model",
    "ops_select"                   : "model",
    "ops_view"                     : "ui", # parts may be graphics
    "op_select_doubly"             : "model",
    "PanMode"                      : "ui",
    "ParameterDialog"              : "ui",
    "parse_utils"                  : "io",
    "part"                         : "foundation", # model, graphics?
    "PartLibPropertyManager"       : "ui",
    "PartLibraryMode"              : "ui",
    "PartProp"                     : "ui",
    "PartPropDialog"               : "ui",
    "pastables"                    : "?",
    "PasteMode"                    : "ui",
    "PastePropertyManager"         : "ui",
    "pi_bond_sp_chain"             : "model",
    "Plane"                        : "ui", # geometry, model?
    "PlaneEditController"          : "ui",
    "PlanePropertyManager"         : "ui",
    "platform"                     : "utilities",
    "PlatformDependent"            : "platform",
    "PlotTool"                     : "ui",
    "PlotToolDialog"               : "ui",
    "Plugins"                      : "?",
    "povheader"                    : "io",
    "povray"                       : "io",
    "PovrayScene"                  : "model", # ?
    "PovraySceneProp"              : "ui",
    "PovrayScenePropDialog"        : "ui",
    "preferences"                  : "utilities",
    "prefsTree"                    : "ui",
    "prefs_constants"              : "utilities",
    "prefs_widgets"                : "ui",
    "Process"                      : "io",
    "PropMgr_Constants"            : "PM",
    "pyrex_test"                   : "top_level",
    "qt4transition"                : "utilities",
    "qutemol"                      : "io",
    "QuteMolPropertyManager"       : "?",
    "ReferenceGeometry"            : "ui", # geometry, model?
    "reposition_baggage"           : "model",
    "ResizeHandle"                 : "?",
    "RotaryMotorEditController"    : "ui",
    "RotaryMotorPropertyManager"   : "ui",
    "RotateMode"                   : "ui",
    "runSim"                       : "io",
    "selectAtomsMode"              : "ui",
    "selectMode"                   : "ui",
    "selectMolsMode"               : "ui",
    "Selobj"                       : "ui", # graphics?
    "SequenceEditor"               : "?",
    "ServerManager"                : "ui",
    "ServerManagerDialog"          : "ui",
    "setup"                        : "tools",
    "setup2"                       : "tools",
    "shape"                        : "ui", # geometry, graphics?
    "SimJob"                       : "io",
    "SimServer"                    : "io",
    "SimSetup"                     : "ui",
    "SimSetupDialog"               : "ui",
    "Sponsors"                     : "ui",
    "state_constants"              : "foundation",
    "state_utils"                  : "foundation",
    "state_utils_unset"            : "foundation",
    "StatProp"                     : "ui",
    "StatPropDialog"               : "ui",
    "StatusBar"                    : "ui",
    "SurfaceChunks"                : "geometry",
    "TemporaryCommand"             : "ui",
    "testdraw"                     : "test",
    "testmode"                     : "test",
    "test_commands"                : "test",
    "test_commands_init"           : "?",
    "test_command_PMs"             : "test",
    "test_connectWithState"        : "test",
    "test_connectWithState_constants" : "test",
    "test_connectWithState_PM"     : "test",
    "texture_fonts"                : "?",
    "texture_helpers"              : "?",
    "ThermoProp"                   : "ui",
    "ThermoPropDialog"             : "ui",
    "ThumbView"                    : "graphics",
    "Ui_BuildAtomsPropertyManager" : "ui",
    "Ui_BuildStructuresMenu"       : "ui",
    "Ui_BuildStructuresToolBar"    : "ui",
    "Ui_BuildToolsMenu"            : "ui",
    "Ui_BuildToolsToolBar"         : "ui",
    "Ui_CommandManager"            : "ui",
    "Ui_CookiePropertyManager"     : "ui",
    "Ui_DimensionsMenu"            : "ui",
    "Ui_DnaFlyout"                 : "?",
    "Ui_EditMenu"                  : "ui",
    "Ui_ExtrudePropertyManager"    : "ui",
    "Ui_FileMenu"                  : "ui",
    "Ui_HelpMenu"                  : "ui",
    "Ui_InsertMenu"                : "ui",
    "Ui_MovePropertyManager"       : "ui",
    "Ui_MoviePropertyManager"      : "ui",
    "Ui_PartWindow"                : "ui",
    "Ui_SelectMenu"                : "ui",
    "Ui_SelectToolBar"             : "ui",
    "Ui_SequenceEditor"            : "?",
    "Ui_SimulationMenu"            : "ui",
    "Ui_SimulationToolBar"         : "ui",
    "Ui_StandardToolBar"           : "ui",
    "Ui_ToolsMenu"                 : "ui",
    "Ui_ViewMenu"                  : "ui",
    "Ui_ViewOrientation"           : "ui",
    "Ui_ViewToolBar"               : "ui",
    "undo"                         : "foundation",
    "undo_archive"                 : "foundation",
    "undo_manager"                 : "foundation",
    "undo_UI"                      : "?",
    "UserPrefs"                    : "ui",
    "UserPrefsDialog"              : "ui",
    "Utility"                      : "foundation", # some model code?
    "version"                      : "utilities",
    "ViewOrientationWindow"        : "ui",
    "VQT"                          : "geometry",
    "whatsthis"                    : "ui",
    "widgets"                      : "ui",
    "widget_controllers"           : "ui",
    "wiki_help"                    : "ui", # some io?
    "ZoomMode"                     : "ui",
    }

# end
