
LIBS += -L$(OPENBABEL_LIBPATH) \
 -L../../../lib \
 -lNanorexUtility \
 -lopenbabel

HEADERS += \
../../../include/Nanorex/Interface/NXDataImportExportPlugin.h \
 ../../../include/Nanorex/Interface/NXDataStoreInfo.h \
 ../../../include/Nanorex/Interface/NXEntityManager.h \
 ../../../include/Nanorex/Interface/NXMoleculeData.h \
 ../../../include/Nanorex/Interface/NXMoleculeSet.h \
 ../../../include/Nanorex/Interface/NXNanoVisionResultCodes.h \
 ../../../include/Nanorex/Interface/NXNumbers.h \
 ../../../include/Nanorex/Interface/NXAtomRenderData.h \
 ../../../include/Nanorex/Interface/NXBondRenderData.h \
 ../../../include/Nanorex/Interface/NXTrackball.h \
 ../../../include/Nanorex/Interface/NXRendererPlugin.h \
 ../../../include/Nanorex/Interface/NXRenderingEngine.h \
 ../../../include/Nanorex/Interface/NXAtomData.h \
 ../../../include/Nanorex/Interface/NXSceneGraph.h

INCLUDEPATH += ../../../include \
 $(OPENBABEL_INCPATH) \
 ../../../src \
 $(HDF5_SIMRESULTS_INCPATH)
# The "../../../src" and $HDF5... are temporary for NXEntityManager to access an
# HDF5_SimResultsImportExport plugin function directly.

SOURCES += ../../Interface/NXDataStoreInfo.cpp \
 ../../Interface/NXEntityManager.cpp \
 ../../Interface/NXMoleculeData.cpp \
 ../../Interface/NXMoleculeSet.cpp \
 ../../Interface/NXNumbers.cpp \
 ../../Interface/NXAtomRenderData.cpp \
 ../../Interface/NXBondRenderData.cpp \
 ../../Interface/NXNanoVisionResultCodes.cpp \
 ../../Interface/NXSceneGraph.cpp \
 ../../Interface/NXRenderingEngine.cpp \
 ../../Interface/NXAtomData.cpp

TEMPLATE = lib

CONFIG += stl \
 dll \
 debug_and_release
win32 : CONFIG -= dll
win32 : CONFIG += staticlib

TARGET = NanorexInterface

DESTDIR = ../../../lib

TARGETDEPS += ../../../lib/libNanorexUtility.so
macx : TARGETDEPS ~= s/.so/.dylib/g
win32 : TARGETDEPS ~= s/.so/.a/g

QT -= gui

