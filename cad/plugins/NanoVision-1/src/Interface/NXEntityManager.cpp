
// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 

#include "Nanorex/Interface/NXEntityManager.h"

namespace Nanorex {


/* CONSTRUCTOR */
NXEntityManager::NXEntityManager() {
	importFileTypesString = "";
	exportFileTypesString = "";
}


/* DESTRUCTOR */
NXEntityManager::~NXEntityManager() {
	//delete rootMoleculeSet;
	////delete dataImpExpPluginGroup;
}


/* FUNCTION: loadDataImportExportPlugins */
/**
 * Loads and initializes all the import/export plugins.
 */
void NXEntityManager::loadDataImportExportPlugins(NXProperties* properties) {
	
	int pluginIndex = 0;
	string msg, pluginFormats;
	string pluginKey = "NXEntityManager.importExport.0";
	string pluginLibrary =
		string(properties->getProperty(pluginKey + ".plugin"));

	if (pluginLibrary.length() == 0) {
		msg = "No Data Import/Export plugins to load.";
		cout << "WARNING: " << msg << endl;
		NXLOG_WARNING("NXEntityManager", msg);
	}

	NXDataImportExportPlugin* plugin;
	dataImpExpPluginGroup = new NXPluginGroup();
	while (pluginLibrary.length() != 0) {
		plugin = 0;
		if (dataImpExpPluginGroup->load(pluginLibrary.c_str()))
			plugin =
				(NXDataImportExportPlugin*)
					(dataImpExpPluginGroup->instantiate(pluginLibrary.c_str()));

		if (plugin == 0) {
			msg =
				"Couldn't load Data Import/Export plugin: " +
					pluginLibrary;
			NXLOG_WARNING("NXEntityManager", msg);
			cout << "WARNING: " << msg << endl;

		} else {
			// Read the plugin's config file
			NXProperties* pluginProperties = new NXProperties();
			msg =
				pluginProperties->readFromFile
					(properties->getProperty(pluginKey + ".pluginConfigFile"));
			if (msg.length() != 0)
				NXLOG_WARNING("NXEntityManager", msg);
			properties->addProperties(pluginProperties,
									  (pluginKey + ".").c_str());
			
			// Import formats registration
			pluginFormats =
				string(properties->getProperty(pluginKey +
							".importFormats"));
			if (importFileTypesString.length() == 0)
				importFileTypesString = pluginFormats;
			else
				importFileTypesString.append(";;").append(pluginFormats);
			int index1 = pluginFormats.find("(");
			int index2 = 0;
			string formats, format;
			while (index1 > 0) {
				index2 = pluginFormats.find(")", index1 + 1);
				formats = pluginFormats.substr(index1 + 1, index2 - index1 - 1);
				NXStringTokenizer tokenizer(formats, " ");
				while (tokenizer.hasMoreTokens()) {
					format = tokenizer.getNextToken();
					// Remove the "*."
					format = format.substr(2);
					dataImportTable[format] = plugin;
				}
				index1 = pluginFormats.find("(", index2 + 1);
			}

			// Export formats registration
			pluginFormats =
				string(properties->getProperty(pluginKey +
							".exportFormats"));
			if (exportFileTypesString.length() == 0)
				exportFileTypesString = pluginFormats;
			else
				exportFileTypesString.append(";;").append(pluginFormats);
			index1 = pluginFormats.find("(");
			index2 = 0;
			while (index1 > 0) {
				index2 = pluginFormats.find(")", index1 + 1);
				formats = pluginFormats.substr(index1 + 1, index2 - index1 - 1);
				NXStringTokenizer tokenizer(formats, " ");
				while (tokenizer.hasMoreTokens()) {
					format = tokenizer.getNextToken();
					// Remove the "*."
					format = format.substr(2);
					dataExportTable[format] = plugin;
				}
				index1 = pluginFormats.find("(", index2 + 1);
			}
		}
		pluginIndex++;
		pluginKey =
			string("NXEntityManager.importExport.") +
			NXUtility::itos(pluginIndex);
		pluginLibrary =
			string(properties->getProperty(pluginKey + ".plugin"));
	}
}


/* FUNCTION: importFromFile */
NXCommandResult* NXEntityManager::importFromFile(const string& filename) {

	NXCommandResult* result;
	//PR_Lock(importExportPluginsMutex);
	
	string fileType = getFileType(filename);
	
	map<string, NXDataImportExportPlugin*>::iterator iter =
		dataImportTable.find(fileType);
	if (iter != dataImportTable.end()) {
		NXDataImportExportPlugin* plugin = iter->second;
		NXDataStoreInfo* dataStoreInfo = new NXDataStoreInfo();
		unsigned int frameIndex = addFrame();

		try {
			plugin->setMode(fileType);
			result =
				plugin->importFromFile(getRootMoleculeSet(frameIndex),
									   dataStoreInfo, filename, frameIndex);
			if (result->getResult() == NX_CMD_SUCCESS)
				while ((!dataStoreInfo->isLastFrame()) &&
					   (result->getResult() == NX_CMD_SUCCESS)) {
					frameIndex = addFrame();
					result =
						plugin->importFromFile(getRootMoleculeSet(frameIndex),
											   dataStoreInfo, filename,
											   frameIndex);
				}

		} catch (...) {
			string msg = fileType;
			msg += "->importFromFile() threw exception";
			NXLOG_SEVERE("NXEntityManager", msg);

			result = new NXCommandResult();
			result->setResult(NX_PLUGIN_CAUSED_ERROR);
			vector<QString> resultVector;
			resultVector.push_back("NXEntityManager");
			QString pluginDescriptor = fileType.c_str();
			pluginDescriptor.append("->importFromFile()");
			resultVector.push_back(pluginDescriptor);
			resultVector.push_back("threw exception");
			result->setParamVector(resultVector);
		}

	} else {
		string msg =
			"importFromFile: no NXDataImportExportPlugin found to handle type: " +
			fileType;
		NXLOG_WARNING("NXEntityManager", msg);

		result = new NXCommandResult();
		result->setResult(NX_PLUGIN_NOT_FOUND);
		vector<QString> resultVector;
		resultVector.push_back("NXEntityManager");
		resultVector.push_back(fileType.c_str());
		resultVector.push_back("not found");
		result->setParamVector(resultVector);
	}
	//PR_Unlock(importExportPluginsMutex);
	return result;
}




/* FUNCTION: exportToFile */
/**
 * Exports the system to the specified file with the appropriate
 * import/export plugin.
 */
NXCommandResult* NXEntityManager::exportToFile(const string& filename) {
	NXCommandResult* result;
	//PR_Lock(importExportPluginsMutex);
	
	// TODO: Abort if there are no molecule sets
	
	string fileType = getFileType(filename);
	
	map<string, NXDataImportExportPlugin*>::iterator iter =
		dataExportTable.find(fileType);
	if (iter != dataExportTable.end()) {
		NXDataImportExportPlugin* plugin = iter->second;
		try {
			plugin->setMode(fileType);
			
			unsigned int frameIndex = 0;
			NXDataStoreInfo* dataStoreInfo = new NXDataStoreInfo();
			dataStoreInfo->setLastFrame(frameIndex > moleculeSets.size() - 2);
			vector<NXMoleculeSet*>::iterator iter = moleculeSets.begin();
			result =
				plugin->exportToFile(*iter, dataStoreInfo, filename,
									 frameIndex);
			iter++;
			frameIndex++;
			while (iter != moleculeSets.end() &&
				   (result->getResult() == NX_CMD_SUCCESS)) {
				dataStoreInfo->setLastFrame
					(frameIndex > moleculeSets.size() - 2);
				result =
					plugin->exportToFile(*iter, dataStoreInfo, filename,
										 frameIndex);
				iter++;
				frameIndex++;
			}
			if (result->getResult() != NX_CMD_SUCCESS)
				NXLOG_SEVERE("NXEntityManager",
							 qPrintable(GetNV1ResultCodeString(result)));

		} catch (...) {
			string msg = fileType;
			msg += "->exportToFile() threw exception";
			NXLOG_SEVERE("NXEntityManager", msg);

			result->setResult(NX_PLUGIN_CAUSED_ERROR);
			std::vector<QString> resultVector;
			resultVector.push_back("NXEntityManager");
			QString pluginDescriptor = fileType.c_str();
			pluginDescriptor.append("->exportToFile()");
			resultVector.push_back(pluginDescriptor);
			resultVector.push_back("threw exception");
			result->setParamVector(resultVector);
		}

	} else {
		std::string msg =
			"exportToFile: no DataImportExportPlugin found to handle type: " +
			fileType;
		NXLOG_WARNING("NXEntityManager", msg);

		result = new NXCommandResult();
		result->setResult(NX_PLUGIN_NOT_FOUND);
		// %1 Who is reporting
		// %2 The name of the plugin that was not found
		// %3 Why the plugin was not found
		std::vector<QString> resultVector;
		resultVector.push_back("NXEntityManager");
		resultVector.push_back(fileType.c_str());
		resultVector.push_back("not found");
		result->setParamVector(resultVector);
	}
	//PR_Unlock(importExportPluginsMutex);
	return result;
}


/* FUNCTION: getFileType */
string NXEntityManager::getFileType(const string& filename) {
	int index = filename.rfind(".");
	if (index > 0)
		return filename.substr(index + 1);
	else
		return "";
}

} // Nanorex::
