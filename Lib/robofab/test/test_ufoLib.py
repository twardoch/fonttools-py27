#! /usr/local/bin/apppython
# -*- coding: utf-8 -*-

import os
import shutil
import unittest
import tempfile
import codecs
from plistlib import writePlist, readPlist
from robofab.ufoLib import UFOReader, UFOWriter, UFOLibError, \
	convertUFOFormatVersion1ToFormatVersion2, convertUFOFormatVersion2ToFormatVersion1
from robofab.test.testSupport import fontInfoVersion1, fontInfoVersion2, fontInfoVersion3, expectedFontInfo1To2Conversion, expectedFontInfo2To1Conversion


# the format version 1 lib.plist contains some data
# that these tests shouldn't be concerned about.
removeFromFormatVersion1Lib = [
	"org.robofab.opentype.classes",
	"org.robofab.opentype.features",
	"org.robofab.opentype.featureorder",
	"org.robofab.postScriptHintData"
]


class TestInfoObject(object): pass


class ReadFontInfoVersion1TestCase(unittest.TestCase):

	def setUp(self):
		self.dstDir = tempfile.mktemp()
		os.mkdir(self.dstDir)
		metaInfo = {
			"creator": "test",
			"formatVersion": 1
		}
		path = os.path.join(self.dstDir, "metainfo.plist")
		writePlist(metaInfo, path)

	def tearDown(self):
		shutil.rmtree(self.dstDir)

	def _writeInfoToPlist(self, info):
		path = os.path.join(self.dstDir, "fontinfo.plist")
		writePlist(info, path)

	def testRead(self):
		originalData = dict(fontInfoVersion1)
		self._writeInfoToPlist(originalData)
		infoObject = TestInfoObject()
		reader = UFOReader(self.dstDir)
		reader.readInfo(infoObject)
		for attr in dir(infoObject):
			if attr not in fontInfoVersion2:
				continue
			originalValue = fontInfoVersion2[attr]
			readValue = getattr(infoObject, attr)
			self.assertEqual(originalValue, readValue)

	def testFontStyleConversion(self):
		fontStyle1To2 = {
			64 : "regular",
			1  : "italic",
			32 : "bold",
			33 : "bold italic"
		}
		for old, new in fontStyle1To2.items():
			info = dict(fontInfoVersion1)
			info["fontStyle"] = old
			self._writeInfoToPlist(info)
			reader = UFOReader(self.dstDir)
			infoObject = TestInfoObject()
			reader.readInfo(infoObject)
			self.assertEqual(new, infoObject.styleMapStyleName)

	def testWidthNameConversion(self):
		widthName1To2 = {
			"Ultra-condensed" : 1,
			"Extra-condensed" : 2,
			"Condensed"		  : 3,
			"Semi-condensed"  : 4,
			"Medium (normal)" : 5,
			"Semi-expanded"	  : 6,
			"Expanded"		  : 7,
			"Extra-expanded"  : 8,
			"Ultra-expanded"  : 9
		}
		for old, new in widthName1To2.items():
			info = dict(fontInfoVersion1)
			info["widthName"] = old
			self._writeInfoToPlist(info)
			reader = UFOReader(self.dstDir)
			infoObject = TestInfoObject()
			reader.readInfo(infoObject)
			self.assertEqual(new, infoObject.openTypeOS2WidthClass)


class ReadFontInfoVersion2TestCase(unittest.TestCase):

	def setUp(self):
		self.dstDir = tempfile.mktemp()
		os.mkdir(self.dstDir)
		metaInfo = {
			"creator": "test",
			"formatVersion": 2
		}
		path = os.path.join(self.dstDir, "metainfo.plist")
		writePlist(metaInfo, path)

	def tearDown(self):
		shutil.rmtree(self.dstDir)

	def _writeInfoToPlist(self, info):
		path = os.path.join(self.dstDir, "fontinfo.plist")
		writePlist(info, path)

	def testRead(self):
		originalData = dict(fontInfoVersion2)
		self._writeInfoToPlist(originalData)
		infoObject = TestInfoObject()
		reader = UFOReader(self.dstDir)
		reader.readInfo(infoObject)
		readData = {}
		for attr in fontInfoVersion2.keys():
			readData[attr] = getattr(infoObject, attr)
		self.assertEqual(originalData, readData)

	def testGenericRead(self):
		# familyName
		info = dict(fontInfoVersion2)
		info["familyName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# styleName
		info = dict(fontInfoVersion2)
		info["styleName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# styleMapFamilyName
		info = dict(fontInfoVersion2)
		info["styleMapFamilyName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# styleMapStyleName
		## not a string
		info = dict(fontInfoVersion2)
		info["styleMapStyleName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## out of range
		info = dict(fontInfoVersion2)
		info["styleMapStyleName"] = "REGULAR"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# versionMajor
		info = dict(fontInfoVersion2)
		info["versionMajor"] = "1"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# versionMinor
		info = dict(fontInfoVersion2)
		info["versionMinor"] = "0"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# copyright
		info = dict(fontInfoVersion2)
		info["copyright"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# trademark
		info = dict(fontInfoVersion2)
		info["trademark"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# unitsPerEm
		info = dict(fontInfoVersion2)
		info["unitsPerEm"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# descender
		info = dict(fontInfoVersion2)
		info["descender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# xHeight
		info = dict(fontInfoVersion2)
		info["xHeight"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# capHeight
		info = dict(fontInfoVersion2)
		info["capHeight"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# ascender
		info = dict(fontInfoVersion2)
		info["ascender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# italicAngle
		info = dict(fontInfoVersion2)
		info["italicAngle"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())

	def testHeadRead(self):
		# openTypeHeadCreated
		## not a string
		info = dict(fontInfoVersion2)
		info["openTypeHeadCreated"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## invalid format
		info = dict(fontInfoVersion2)
		info["openTypeHeadCreated"] = "2000-Jan-01 00:00:00"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeHeadLowestRecPPEM
		info = dict(fontInfoVersion2)
		info["openTypeHeadLowestRecPPEM"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeHeadFlags
		info = dict(fontInfoVersion2)
		info["openTypeHeadFlags"] = [-1]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())

	def testHheaRead(self):
		# openTypeHheaAscender
		info = dict(fontInfoVersion2)
		info["openTypeHheaAscender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeHheaDescender
		info = dict(fontInfoVersion2)
		info["openTypeHheaDescender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeHheaLineGap
		info = dict(fontInfoVersion2)
		info["openTypeHheaLineGap"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeHheaCaretSlopeRise
		info = dict(fontInfoVersion2)
		info["openTypeHheaCaretSlopeRise"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeHheaCaretSlopeRun
		info = dict(fontInfoVersion2)
		info["openTypeHheaCaretSlopeRun"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeHheaCaretOffset
		info = dict(fontInfoVersion2)
		info["openTypeHheaCaretOffset"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())

	def testNameRead(self):
		# openTypeNameDesigner
		info = dict(fontInfoVersion2)
		info["openTypeNameDesigner"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameDesignerURL
		info = dict(fontInfoVersion2)
		info["openTypeNameDesignerURL"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameManufacturer
		info = dict(fontInfoVersion2)
		info["openTypeNameManufacturer"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameManufacturerURL
		info = dict(fontInfoVersion2)
		info["openTypeNameManufacturerURL"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameLicense
		info = dict(fontInfoVersion2)
		info["openTypeNameLicense"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameLicenseURL
		info = dict(fontInfoVersion2)
		info["openTypeNameLicenseURL"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameVersion
		info = dict(fontInfoVersion2)
		info["openTypeNameVersion"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameUniqueID
		info = dict(fontInfoVersion2)
		info["openTypeNameUniqueID"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameDescription
		info = dict(fontInfoVersion2)
		info["openTypeNameDescription"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNamePreferredFamilyName
		info = dict(fontInfoVersion2)
		info["openTypeNamePreferredFamilyName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNamePreferredSubfamilyName
		info = dict(fontInfoVersion2)
		info["openTypeNamePreferredSubfamilyName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameCompatibleFullName
		info = dict(fontInfoVersion2)
		info["openTypeNameCompatibleFullName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameSampleText
		info = dict(fontInfoVersion2)
		info["openTypeNameSampleText"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameWWSFamilyName
		info = dict(fontInfoVersion2)
		info["openTypeNameWWSFamilyName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameWWSSubfamilyName
		info = dict(fontInfoVersion2)
		info["openTypeNameWWSSubfamilyName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())

	def testOS2Read(self):
		# openTypeOS2WidthClass
		## not an int
		info = dict(fontInfoVersion2)
		info["openTypeOS2WidthClass"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## out or range
		info = dict(fontInfoVersion2)
		info["openTypeOS2WidthClass"] = 15
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2WeightClass
		info = dict(fontInfoVersion2)
		## not an int
		info["openTypeOS2WeightClass"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## out of range
		info["openTypeOS2WeightClass"] = -50
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2Selection
		info = dict(fontInfoVersion2)
		info["openTypeOS2Selection"] = [-1]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2VendorID
		info = dict(fontInfoVersion2)
		info["openTypeOS2VendorID"] = 1234
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2Panose
		## not an int
		info = dict(fontInfoVersion2)
		info["openTypeOS2Panose"] = [0, 1, 2, 3, 4, 5, 6, 7, 8, str(9)]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## too few values
		info = dict(fontInfoVersion2)
		info["openTypeOS2Panose"] = [0, 1, 2, 3]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## too many values
		info = dict(fontInfoVersion2)
		info["openTypeOS2Panose"] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2FamilyClass
		## not an int
		info = dict(fontInfoVersion2)
		info["openTypeOS2FamilyClass"] = [1, str(1)]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## too few values
		info = dict(fontInfoVersion2)
		info["openTypeOS2FamilyClass"] = [1]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## too many values
		info = dict(fontInfoVersion2)
		info["openTypeOS2FamilyClass"] = [1, 1, 1]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## out of range
		info = dict(fontInfoVersion2)
		info["openTypeOS2FamilyClass"] = [1, 201]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2UnicodeRanges
		## not an int
		info = dict(fontInfoVersion2)
		info["openTypeOS2UnicodeRanges"] = ["0"]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## out of range
		info = dict(fontInfoVersion2)
		info["openTypeOS2UnicodeRanges"] = [-1]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2CodePageRanges
		## not an int
		info = dict(fontInfoVersion2)
		info["openTypeOS2CodePageRanges"] = ["0"]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## out of range
		info = dict(fontInfoVersion2)
		info["openTypeOS2CodePageRanges"] = [-1]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2TypoAscender
		info = dict(fontInfoVersion2)
		info["openTypeOS2TypoAscender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2TypoDescender
		info = dict(fontInfoVersion2)
		info["openTypeOS2TypoDescender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2TypoLineGap
		info = dict(fontInfoVersion2)
		info["openTypeOS2TypoLineGap"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2WinAscent
		info = dict(fontInfoVersion2)
		info["openTypeOS2WinAscent"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2WinDescent
		info = dict(fontInfoVersion2)
		info["openTypeOS2WinDescent"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2Type
		## not an int
		info = dict(fontInfoVersion2)
		info["openTypeOS2Type"] = ["1"]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## out of range
		info = dict(fontInfoVersion2)
		info["openTypeOS2Type"] = [-1]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SubscriptXSize
		info = dict(fontInfoVersion2)
		info["openTypeOS2SubscriptXSize"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SubscriptYSize
		info = dict(fontInfoVersion2)
		info["openTypeOS2SubscriptYSize"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SubscriptXOffset
		info = dict(fontInfoVersion2)
		info["openTypeOS2SubscriptXOffset"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SubscriptYOffset
		info = dict(fontInfoVersion2)
		info["openTypeOS2SubscriptYOffset"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SuperscriptXSize
		info = dict(fontInfoVersion2)
		info["openTypeOS2SuperscriptXSize"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SuperscriptYSize
		info = dict(fontInfoVersion2)
		info["openTypeOS2SuperscriptYSize"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SuperscriptXOffset
		info = dict(fontInfoVersion2)
		info["openTypeOS2SuperscriptXOffset"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SuperscriptYOffset
		info = dict(fontInfoVersion2)
		info["openTypeOS2SuperscriptYOffset"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2StrikeoutSize
		info = dict(fontInfoVersion2)
		info["openTypeOS2StrikeoutSize"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2StrikeoutPosition
		info = dict(fontInfoVersion2)
		info["openTypeOS2StrikeoutPosition"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())

	def testVheaRead(self):
		# openTypeVheaVertTypoAscender
		info = dict(fontInfoVersion2)
		info["openTypeVheaVertTypoAscender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeVheaVertTypoDescender
		info = dict(fontInfoVersion2)
		info["openTypeVheaVertTypoDescender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeVheaVertTypoLineGap
		info = dict(fontInfoVersion2)
		info["openTypeVheaVertTypoLineGap"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeVheaCaretSlopeRise
		info = dict(fontInfoVersion2)
		info["openTypeVheaCaretSlopeRise"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeVheaCaretSlopeRun
		info = dict(fontInfoVersion2)
		info["openTypeVheaCaretSlopeRun"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeVheaCaretOffset
		info = dict(fontInfoVersion2)
		info["openTypeVheaCaretOffset"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())

	def testFONDRead(self):
		# macintoshFONDFamilyID
		info = dict(fontInfoVersion2)
		info["macintoshFONDFamilyID"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# macintoshFONDName
		info = dict(fontInfoVersion2)
		info["macintoshFONDName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())

	def testPostscriptRead(self):
		# postscriptFontName
		info = dict(fontInfoVersion2)
		info["postscriptFontName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# postscriptFullName
		info = dict(fontInfoVersion2)
		info["postscriptFullName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# postscriptSlantAngle
		info = dict(fontInfoVersion2)
		info["postscriptSlantAngle"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# postscriptUniqueID
		info = dict(fontInfoVersion2)
		info["postscriptUniqueID"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptUnderlineThickness
		info = dict(fontInfoVersion2)
		info["postscriptUnderlineThickness"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptUnderlinePosition
		info = dict(fontInfoVersion2)
		info["postscriptUnderlinePosition"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptIsFixedPitch
		info = dict(fontInfoVersion2)
		info["postscriptIsFixedPitch"] = 2
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptBlueValues
		## not a list
		info = dict(fontInfoVersion2)
		info["postscriptBlueValues"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## uneven value count
		info = dict(fontInfoVersion2)
		info["postscriptBlueValues"] = [500]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## too many values
		info = dict(fontInfoVersion2)
		info["postscriptBlueValues"] = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptOtherBlues
		## not a list
		info = dict(fontInfoVersion2)
		info["postscriptOtherBlues"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## uneven value count
		info = dict(fontInfoVersion2)
		info["postscriptOtherBlues"] = [500]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## too many values
		info = dict(fontInfoVersion2)
		info["postscriptOtherBlues"] = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptFamilyBlues
		## not a list
		info = dict(fontInfoVersion2)
		info["postscriptFamilyBlues"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## uneven value count
		info = dict(fontInfoVersion2)
		info["postscriptFamilyBlues"] = [500]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## too many values
		info = dict(fontInfoVersion2)
		info["postscriptFamilyBlues"] = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptFamilyOtherBlues
		## not a list
		info = dict(fontInfoVersion2)
		info["postscriptFamilyOtherBlues"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## uneven value count
		info = dict(fontInfoVersion2)
		info["postscriptFamilyOtherBlues"] = [500]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## too many values
		info = dict(fontInfoVersion2)
		info["postscriptFamilyOtherBlues"] = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptStemSnapH
		## not list
		info = dict(fontInfoVersion2)
		info["postscriptStemSnapH"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## too many values
		info = dict(fontInfoVersion2)
		info["postscriptStemSnapH"] = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptStemSnapV
		## not list
		info = dict(fontInfoVersion2)
		info["postscriptStemSnapV"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## too many values
		info = dict(fontInfoVersion2)
		info["postscriptStemSnapV"] = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptBlueFuzz
		info = dict(fontInfoVersion2)
		info["postscriptBlueFuzz"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptBlueShift
		info = dict(fontInfoVersion2)
		info["postscriptBlueShift"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptBlueScale
		info = dict(fontInfoVersion2)
		info["postscriptBlueScale"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptForceBold
		info = dict(fontInfoVersion2)
		info["postscriptForceBold"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptDefaultWidthX
		info = dict(fontInfoVersion2)
		info["postscriptDefaultWidthX"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptNominalWidthX
		info = dict(fontInfoVersion2)
		info["postscriptNominalWidthX"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptWeightName
		info = dict(fontInfoVersion2)
		info["postscriptWeightName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptDefaultCharacter
		info = dict(fontInfoVersion2)
		info["postscriptDefaultCharacter"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptWindowsCharacterSet
		info = dict(fontInfoVersion2)
		info["postscriptWindowsCharacterSet"] = -1
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# macintoshFONDFamilyID
		info = dict(fontInfoVersion2)
		info["macintoshFONDFamilyID"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# macintoshFONDName
		info = dict(fontInfoVersion2)
		info["macintoshFONDName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())


class ReadFontInfoVersion3TestCase(unittest.TestCase):

	def setUp(self):
		self.dstDir = tempfile.mktemp()
		os.mkdir(self.dstDir)
		metaInfo = {
			"creator": "test",
			"formatVersion": 3
		}
		path = os.path.join(self.dstDir, "metainfo.plist")
		writePlist(metaInfo, path)

	def tearDown(self):
		shutil.rmtree(self.dstDir)

	def _writeInfoToPlist(self, info):
		path = os.path.join(self.dstDir, "fontinfo.plist")
		writePlist(info, path)

	def testRead(self):
		originalData = dict(fontInfoVersion3)
		self._writeInfoToPlist(originalData)
		infoObject = TestInfoObject()
		reader = UFOReader(self.dstDir)
		reader.readInfo(infoObject)
		readData = {}
		for attr in fontInfoVersion3.keys():
			readData[attr] = getattr(infoObject, attr)
		self.assertEqual(originalData, readData)

	def testGenericRead(self):
		# familyName
		info = dict(fontInfoVersion3)
		info["familyName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# styleName
		info = dict(fontInfoVersion3)
		info["styleName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# styleMapFamilyName
		info = dict(fontInfoVersion3)
		info["styleMapFamilyName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# styleMapStyleName
		## not a string
		info = dict(fontInfoVersion3)
		info["styleMapStyleName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## out of range
		info = dict(fontInfoVersion3)
		info["styleMapStyleName"] = "REGULAR"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# versionMajor
		info = dict(fontInfoVersion3)
		info["versionMajor"] = "1"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# versionMinor
		info = dict(fontInfoVersion3)
		info["versionMinor"] = "0"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["versionMinor"] = -1
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# copyright
		info = dict(fontInfoVersion3)
		info["copyright"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# trademark
		info = dict(fontInfoVersion3)
		info["trademark"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# unitsPerEm
		info = dict(fontInfoVersion3)
		info["unitsPerEm"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["unitsPerEm"] = -1
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["unitsPerEm"] = -1.0
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# descender
		info = dict(fontInfoVersion3)
		info["descender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# xHeight
		info = dict(fontInfoVersion3)
		info["xHeight"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# capHeight
		info = dict(fontInfoVersion3)
		info["capHeight"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# ascender
		info = dict(fontInfoVersion3)
		info["ascender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# italicAngle
		info = dict(fontInfoVersion3)
		info["italicAngle"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())

	def testGaspRead(self):
		# not a list
		info = dict(fontInfoVersion3)
		info["openTypeGaspRangeRecords"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# empty list
		info = dict(fontInfoVersion3)
		info["openTypeGaspRangeRecords"] = []
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# not a dict
		info = dict(fontInfoVersion3)
		info["openTypeGaspRangeRecords"] = ["abc"]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# dict not properly formatted
		info = dict(fontInfoVersion3)
		info["openTypeGaspRangeRecords"] = [dict(rangeMaxPPEM=0xFFFF, notTheRightKey=1)]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["openTypeGaspRangeRecords"] = [dict(notTheRightKey=1, rangeGaspBehavior=[0])]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# not an int for ppem
		info = dict(fontInfoVersion3)
		info["openTypeGaspRangeRecords"] = [dict(rangeMaxPPEM="abc", rangeGaspBehavior=[0]), dict(rangeMaxPPEM=0xFFFF, rangeGaspBehavior=[0])]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# not a list for behavior
		info = dict(fontInfoVersion3)
		info["openTypeGaspRangeRecords"] = [dict(rangeMaxPPEM=10, rangeGaspBehavior="abc"), dict(rangeMaxPPEM=0xFFFF, rangeGaspBehavior=[0])]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# invalid behavior value
		info = dict(fontInfoVersion3)
		info["openTypeGaspRangeRecords"] = [dict(rangeMaxPPEM=10, rangeGaspBehavior=[-1]), dict(rangeMaxPPEM=0xFFFF, rangeGaspBehavior=[0])]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# not sorted
		info = dict(fontInfoVersion3)
		info["openTypeGaspRangeRecords"] = [dict(rangeMaxPPEM=0xFFFF, rangeGaspBehavior=[0]), dict(rangeMaxPPEM=10, rangeGaspBehavior=[-1])]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# no 0xFFFF
		info = dict(fontInfoVersion3)
		info["openTypeGaspRangeRecords"] = [dict(rangeMaxPPEM=10, rangeGaspBehavior=[0]), dict(rangeMaxPPEM=20, rangeGaspBehavior=[-1])]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())

	def testHeadRead(self):
		# openTypeHeadCreated
		## not a string
		info = dict(fontInfoVersion3)
		info["openTypeHeadCreated"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## invalid format
		info = dict(fontInfoVersion3)
		info["openTypeHeadCreated"] = "2000-Jan-01 00:00:00"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeHeadLowestRecPPEM
		info = dict(fontInfoVersion3)
		info["openTypeHeadLowestRecPPEM"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["openTypeHeadLowestRecPPEM"] = -1
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeHeadFlags
		info = dict(fontInfoVersion3)
		info["openTypeHeadFlags"] = [-1]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())

	def testHheaRead(self):
		# openTypeHheaAscender
		info = dict(fontInfoVersion3)
		info["openTypeHheaAscender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeHheaDescender
		info = dict(fontInfoVersion3)
		info["openTypeHheaDescender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeHheaLineGap
		info = dict(fontInfoVersion3)
		info["openTypeHheaLineGap"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeHheaCaretSlopeRise
		info = dict(fontInfoVersion3)
		info["openTypeHheaCaretSlopeRise"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeHheaCaretSlopeRun
		info = dict(fontInfoVersion3)
		info["openTypeHheaCaretSlopeRun"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeHheaCaretOffset
		info = dict(fontInfoVersion3)
		info["openTypeHheaCaretOffset"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())

	def testNameRead(self):
		# openTypeNameDesigner
		info = dict(fontInfoVersion3)
		info["openTypeNameDesigner"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameDesignerURL
		info = dict(fontInfoVersion3)
		info["openTypeNameDesignerURL"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameManufacturer
		info = dict(fontInfoVersion3)
		info["openTypeNameManufacturer"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameManufacturerURL
		info = dict(fontInfoVersion3)
		info["openTypeNameManufacturerURL"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameLicense
		info = dict(fontInfoVersion3)
		info["openTypeNameLicense"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameLicenseURL
		info = dict(fontInfoVersion3)
		info["openTypeNameLicenseURL"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameVersion
		info = dict(fontInfoVersion3)
		info["openTypeNameVersion"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameUniqueID
		info = dict(fontInfoVersion3)
		info["openTypeNameUniqueID"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameDescription
		info = dict(fontInfoVersion3)
		info["openTypeNameDescription"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNamePreferredFamilyName
		info = dict(fontInfoVersion3)
		info["openTypeNamePreferredFamilyName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNamePreferredSubfamilyName
		info = dict(fontInfoVersion3)
		info["openTypeNamePreferredSubfamilyName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameCompatibleFullName
		info = dict(fontInfoVersion3)
		info["openTypeNameCompatibleFullName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameSampleText
		info = dict(fontInfoVersion3)
		info["openTypeNameSampleText"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameWWSFamilyName
		info = dict(fontInfoVersion3)
		info["openTypeNameWWSFamilyName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameWWSSubfamilyName
		info = dict(fontInfoVersion3)
		info["openTypeNameWWSSubfamilyName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeNameRecords
		## not a list
		info = dict(fontInfoVersion3)
		info["openTypeNameRecords"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## not a dict
		info = dict(fontInfoVersion3)
		info["openTypeNameRecords"] = ["abc"]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## invalid dict structure
		info = dict(fontInfoVersion3)
		info["openTypeNameRecords"] = [dict(foo="bar")]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## incorrect keys
		info = dict(fontInfoVersion3)
		info["openTypeNameRecords"] = [
			dict(nameID=1, platformID=1, encodingID=1, languageID=1, string="Name Record.", foo="bar")
		]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["openTypeNameRecords"] = [
			dict(platformID=1, encodingID=1, languageID=1, string="Name Record.")
		]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["openTypeNameRecords"] = [
			dict(nameID=1, encodingID=1, languageID=1, string="Name Record.")
		]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["openTypeNameRecords"] = [
			dict(nameID=1, platformID=1, languageID=1, string="Name Record.")
		]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["openTypeNameRecords"] = [
			dict(nameID=1, platformID=1, encodingID=1, string="Name Record.")
		]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["openTypeNameRecords"] = [
			dict(nameID=1, platformID=1, encodingID=1, languageID=1)
		]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## invalid values
		info = dict(fontInfoVersion3)
		info["openTypeNameRecords"] = [
			dict(nameID="1", platformID=1, encodingID=1, languageID=1, string="Name Record.")
		]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["openTypeNameRecords"] = [
			dict(nameID=1, platformID="1", encodingID=1, languageID=1, string="Name Record.")
		]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["openTypeNameRecords"] = [
			dict(nameID=1, platformID=1, encodingID="1", languageID=1, string="Name Record.")
		]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["openTypeNameRecords"] = [
			dict(nameID=1, platformID=1, encodingID=1, languageID="1", string="Name Record.")
		]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["openTypeNameRecords"] = [
			dict(nameID=1, platformID=1, encodingID=1, languageID=1, string=1)
		]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## duplicate
		info = dict(fontInfoVersion3)
		info["openTypeNameRecords"] = [
			dict(nameID=1, platformID=1, encodingID=1, languageID=1, string="Name Record."),
			dict(nameID=1, platformID=1, encodingID=1, languageID=1, string="Name Record.")
		]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())

	def testOS2Read(self):
		# openTypeOS2WidthClass
		## not an int
		info = dict(fontInfoVersion3)
		info["openTypeOS2WidthClass"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## out or range
		info = dict(fontInfoVersion3)
		info["openTypeOS2WidthClass"] = 15
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2WeightClass
		info = dict(fontInfoVersion3)
		## not an int
		info["openTypeOS2WeightClass"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## out of range
		info["openTypeOS2WeightClass"] = -50
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2Selection
		info = dict(fontInfoVersion3)
		info["openTypeOS2Selection"] = [-1]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2VendorID
		info = dict(fontInfoVersion3)
		info["openTypeOS2VendorID"] = 1234
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2Panose
		## not an int
		info = dict(fontInfoVersion3)
		info["openTypeOS2Panose"] = [0, 1, 2, 3, 4, 5, 6, 7, 8, str(9)]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## negative
		info = dict(fontInfoVersion3)
		info["openTypeOS2Panose"] = [0, 1, 2, 3, 4, 5, 6, 7, 8, -9]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## too few values
		info = dict(fontInfoVersion3)
		info["openTypeOS2Panose"] = [0, 1, 2, 3]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## too many values
		info = dict(fontInfoVersion3)
		info["openTypeOS2Panose"] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2FamilyClass
		## not an int
		info = dict(fontInfoVersion3)
		info["openTypeOS2FamilyClass"] = [1, str(1)]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## too few values
		info = dict(fontInfoVersion3)
		info["openTypeOS2FamilyClass"] = [1]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## too many values
		info = dict(fontInfoVersion3)
		info["openTypeOS2FamilyClass"] = [1, 1, 1]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## out of range
		info = dict(fontInfoVersion3)
		info["openTypeOS2FamilyClass"] = [1, 201]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2UnicodeRanges
		## not an int
		info = dict(fontInfoVersion3)
		info["openTypeOS2UnicodeRanges"] = ["0"]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## out of range
		info = dict(fontInfoVersion3)
		info["openTypeOS2UnicodeRanges"] = [-1]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2CodePageRanges
		## not an int
		info = dict(fontInfoVersion3)
		info["openTypeOS2CodePageRanges"] = ["0"]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## out of range
		info = dict(fontInfoVersion3)
		info["openTypeOS2CodePageRanges"] = [-1]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2TypoAscender
		info = dict(fontInfoVersion3)
		info["openTypeOS2TypoAscender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2TypoDescender
		info = dict(fontInfoVersion3)
		info["openTypeOS2TypoDescender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2TypoLineGap
		info = dict(fontInfoVersion3)
		info["openTypeOS2TypoLineGap"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2WinAscent
		info = dict(fontInfoVersion3)
		info["openTypeOS2WinAscent"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["openTypeOS2WinAscent"] = -1
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2WinDescent
		info = dict(fontInfoVersion3)
		info["openTypeOS2WinDescent"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		info = dict(fontInfoVersion3)
		info["openTypeOS2WinDescent"] = -1
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2Type
		## not an int
		info = dict(fontInfoVersion3)
		info["openTypeOS2Type"] = ["1"]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		## out of range
		info = dict(fontInfoVersion3)
		info["openTypeOS2Type"] = [-1]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SubscriptXSize
		info = dict(fontInfoVersion3)
		info["openTypeOS2SubscriptXSize"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SubscriptYSize
		info = dict(fontInfoVersion3)
		info["openTypeOS2SubscriptYSize"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SubscriptXOffset
		info = dict(fontInfoVersion3)
		info["openTypeOS2SubscriptXOffset"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SubscriptYOffset
		info = dict(fontInfoVersion3)
		info["openTypeOS2SubscriptYOffset"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SuperscriptXSize
		info = dict(fontInfoVersion3)
		info["openTypeOS2SuperscriptXSize"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SuperscriptYSize
		info = dict(fontInfoVersion3)
		info["openTypeOS2SuperscriptYSize"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SuperscriptXOffset
		info = dict(fontInfoVersion3)
		info["openTypeOS2SuperscriptXOffset"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2SuperscriptYOffset
		info = dict(fontInfoVersion3)
		info["openTypeOS2SuperscriptYOffset"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2StrikeoutSize
		info = dict(fontInfoVersion3)
		info["openTypeOS2StrikeoutSize"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeOS2StrikeoutPosition
		info = dict(fontInfoVersion3)
		info["openTypeOS2StrikeoutPosition"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())

	def testVheaRead(self):
		# openTypeVheaVertTypoAscender
		info = dict(fontInfoVersion3)
		info["openTypeVheaVertTypoAscender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeVheaVertTypoDescender
		info = dict(fontInfoVersion3)
		info["openTypeVheaVertTypoDescender"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeVheaVertTypoLineGap
		info = dict(fontInfoVersion3)
		info["openTypeVheaVertTypoLineGap"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeVheaCaretSlopeRise
		info = dict(fontInfoVersion3)
		info["openTypeVheaCaretSlopeRise"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeVheaCaretSlopeRun
		info = dict(fontInfoVersion3)
		info["openTypeVheaCaretSlopeRun"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# openTypeVheaCaretOffset
		info = dict(fontInfoVersion3)
		info["openTypeVheaCaretOffset"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())

	def testFONDRead(self):
		# macintoshFONDFamilyID
		info = dict(fontInfoVersion3)
		info["macintoshFONDFamilyID"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# macintoshFONDName
		info = dict(fontInfoVersion3)
		info["macintoshFONDName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())

	def testPostscriptRead(self):
		# postscriptFontName
		info = dict(fontInfoVersion3)
		info["postscriptFontName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# postscriptFullName
		info = dict(fontInfoVersion3)
		info["postscriptFullName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# postscriptSlantAngle
		info = dict(fontInfoVersion3)
		info["postscriptSlantAngle"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, info=TestInfoObject())
		# postscriptUniqueID
		info = dict(fontInfoVersion3)
		info["postscriptUniqueID"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptUnderlineThickness
		info = dict(fontInfoVersion3)
		info["postscriptUnderlineThickness"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptUnderlinePosition
		info = dict(fontInfoVersion3)
		info["postscriptUnderlinePosition"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptIsFixedPitch
		info = dict(fontInfoVersion3)
		info["postscriptIsFixedPitch"] = 2
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptBlueValues
		## not a list
		info = dict(fontInfoVersion3)
		info["postscriptBlueValues"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## uneven value count
		info = dict(fontInfoVersion3)
		info["postscriptBlueValues"] = [500]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## too many values
		info = dict(fontInfoVersion3)
		info["postscriptBlueValues"] = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptOtherBlues
		## not a list
		info = dict(fontInfoVersion3)
		info["postscriptOtherBlues"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## uneven value count
		info = dict(fontInfoVersion3)
		info["postscriptOtherBlues"] = [500]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## too many values
		info = dict(fontInfoVersion3)
		info["postscriptOtherBlues"] = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptFamilyBlues
		## not a list
		info = dict(fontInfoVersion3)
		info["postscriptFamilyBlues"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## uneven value count
		info = dict(fontInfoVersion3)
		info["postscriptFamilyBlues"] = [500]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## too many values
		info = dict(fontInfoVersion3)
		info["postscriptFamilyBlues"] = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptFamilyOtherBlues
		## not a list
		info = dict(fontInfoVersion3)
		info["postscriptFamilyOtherBlues"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## uneven value count
		info = dict(fontInfoVersion3)
		info["postscriptFamilyOtherBlues"] = [500]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## too many values
		info = dict(fontInfoVersion3)
		info["postscriptFamilyOtherBlues"] = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptStemSnapH
		## not list
		info = dict(fontInfoVersion3)
		info["postscriptStemSnapH"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## too many values
		info = dict(fontInfoVersion3)
		info["postscriptStemSnapH"] = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptStemSnapV
		## not list
		info = dict(fontInfoVersion3)
		info["postscriptStemSnapV"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## too many values
		info = dict(fontInfoVersion3)
		info["postscriptStemSnapV"] = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptBlueFuzz
		info = dict(fontInfoVersion3)
		info["postscriptBlueFuzz"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptBlueShift
		info = dict(fontInfoVersion3)
		info["postscriptBlueShift"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptBlueScale
		info = dict(fontInfoVersion3)
		info["postscriptBlueScale"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptForceBold
		info = dict(fontInfoVersion3)
		info["postscriptForceBold"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptDefaultWidthX
		info = dict(fontInfoVersion3)
		info["postscriptDefaultWidthX"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptNominalWidthX
		info = dict(fontInfoVersion3)
		info["postscriptNominalWidthX"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptWeightName
		info = dict(fontInfoVersion3)
		info["postscriptWeightName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptDefaultCharacter
		info = dict(fontInfoVersion3)
		info["postscriptDefaultCharacter"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# postscriptWindowsCharacterSet
		info = dict(fontInfoVersion3)
		info["postscriptWindowsCharacterSet"] = -1
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# macintoshFONDFamilyID
		info = dict(fontInfoVersion3)
		info["macintoshFONDFamilyID"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# macintoshFONDName
		info = dict(fontInfoVersion3)
		info["macintoshFONDName"] = 123
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())

	def testWOFFRead(self):
		# woffMajorVersion
		info = dict(fontInfoVersion3)
		info["woffMajorVersion"] = 1.0
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		info = dict(fontInfoVersion3)
		info["woffMajorVersion"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# woffMinorVersion
		info = dict(fontInfoVersion3)
		info["woffMinorVersion"] = 1.0
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		info = dict(fontInfoVersion3)
		info["woffMinorVersion"] = "abc"
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# woffMetadataUniqueID
		## none
		info = dict(fontInfoVersion3)
		del info["woffMetadataUniqueID"]
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		reader.readInfo(TestInfoObject())
		## not a dict
		info = dict(fontInfoVersion3)
		info["woffMetadataUniqueID"] = 1
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## unknown key
		info = dict(fontInfoVersion3)
		info["woffMetadataUniqueID"] = dict(id="foo", notTheRightKey=1)
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## no id
		info = dict(fontInfoVersion3)
		info["woffMetadataUniqueID"] = dict()
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## not a string for id
		info = dict(fontInfoVersion3)
		info["woffMetadataUniqueID"] = dict(id=1)
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## empty string
		info = dict(fontInfoVersion3)
		info["woffMetadataUniqueID"] = dict(id="")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		reader.readInfo(TestInfoObject())
		# woffMetadataVendor
		## no name
		info = dict(fontInfoVersion3)
		info["woffMetadataVendor"] = dict(url="foo")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## name not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataVendor"] = dict(name=1, url="foo")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## name an empty string
		info = dict(fontInfoVersion3)
		info["woffMetadataVendor"] = dict(name="", url="foo")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		reader.readInfo(TestInfoObject())
		## no URL
		info = dict(fontInfoVersion3)
		info["woffMetadataVendor"] = dict(name="foo")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		reader.readInfo(TestInfoObject())
		## url not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataVendor"] = dict(name="foo", url=1)
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## url empty string
		info = dict(fontInfoVersion3)
		info["woffMetadataVendor"] = dict(name="foo", url="")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		reader.readInfo(TestInfoObject())
		## have dir
		info = dict(fontInfoVersion3)
		info["woffMetadataVendor"] = dict(name="foo", url="bar", dir="ltr")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		reader.readInfo(TestInfoObject())
		info = dict(fontInfoVersion3)
		info["woffMetadataVendor"] = dict(name="foo", url="bar", dir="rtl")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		reader.readInfo(TestInfoObject())
		## dir not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataVendor"] = dict(name="foo", url="bar", dir=1)
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## dir not ltr or rtl
		info = dict(fontInfoVersion3)
		info["woffMetadataVendor"] = dict(name="foo", url="bar", dir="utd")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## have class
		info = dict(fontInfoVersion3)
		info["woffMetadataVendor"] = {"name"  : "foo", "url" : "bar", "class" : "hello"}
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		reader.readInfo(TestInfoObject())
		## class not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataVendor"] = {"name"  : "foo", "url" : "bar", "class" : 1}
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## class empty string
		info = dict(fontInfoVersion3)
		info["woffMetadataVendor"] = {"name"  : "foo", "url" : "bar", "class" : ""}
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		reader.readInfo(TestInfoObject())
		# woffMetadataCredits
		## no credits attribute
		info = dict(fontInfoVersion3)
		info["woffMetadataCredits"] = {}
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## unknown attribute
		info = dict(fontInfoVersion3)
		info["woffMetadataCredits"] = dict(credits=[dict(name="foo")], notTheRightKey=1)
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## not a list
		info = dict(fontInfoVersion3)
		info["woffMetadataCredits"] = dict(credits="abc")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## no elements in credits
		info = dict(fontInfoVersion3)
		info["woffMetadataCredits"] = dict(credits=[])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## credit not a dict
		info = dict(fontInfoVersion3)
		info["woffMetadataCredits"] = dict(credits=["abc"])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## unknown key
		info = dict(fontInfoVersion3)
		info["woffMetadataCredits"] = dict(credits=[dict(name="foo", notTheRightKey=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## no name
		info = dict(fontInfoVersion3)
		info["woffMetadataCredits"] = dict(credits=[dict(url="foo")])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## name not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataCredits"] = dict(credits=[dict(name=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## url not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataCredits"] = dict(credits=[dict(name="foo", url=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## role not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataCredits"] = dict(credits=[dict(name="foo", role=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## dir not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataCredits"] = dict(credits=[dict(name="foo", dir=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## dir not ltr or rtl
		info = dict(fontInfoVersion3)
		info["woffMetadataCredits"] = dict(credits=[dict(name="foo", dir="utd")])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## class not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataCredits"] = dict(credits=[{"name"  : "foo", "class" : 1}])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# woffMetadataDescription
		## no url
		info = dict(fontInfoVersion3)
		info["woffMetadataDescription"] = dict(text=[dict(text="foo")])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		reader.readInfo(TestInfoObject())
		## url not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataDescription"] = dict(text=[dict(text="foo")], url=1)
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## no text
		info = dict(fontInfoVersion3)
		info["woffMetadataDescription"] = dict(url="foo")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text not a list
		info = dict(fontInfoVersion3)
		info["woffMetadataDescription"] = dict(text="abc")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text item not a dict
		info = dict(fontInfoVersion3)
		info["woffMetadataDescription"] = dict(text=["abc"])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text item unknown key
		info = dict(fontInfoVersion3)
		info["woffMetadataDescription"] = dict(text=[dict(text="foo", notTheRightKey=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text item missing text
		info = dict(fontInfoVersion3)
		info["woffMetadataDescription"] = dict(text=[dict(language="foo")])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataDescription"] = dict(text=[dict(text=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## url not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataDescription"] = dict(text=[dict(text="foo", url=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## language not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataDescription"] = dict(text=[dict(text="foo", language=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## dir not ltr or rtl
		info = dict(fontInfoVersion3)
		info["woffMetadataDescription"] = dict(text=[dict(text="foo", dir="utd")])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## class not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataDescription"] = dict(text=[{"text"  : "foo", "class" : 1}])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# woffMetadataLicense
		## no url
		info = dict(fontInfoVersion3)
		info["woffMetadataLicense"] = dict(text=[dict(text="foo")])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		reader.readInfo(TestInfoObject())
		## url not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataLicense"] = dict(text=[dict(text="foo")], url=1)
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## id not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataLicense"] = dict(text=[dict(text="foo")], id=1)
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## no text
		info = dict(fontInfoVersion3)
		info["woffMetadataLicense"] = dict(url="foo")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		reader.readInfo(TestInfoObject())
		## text not a list
		info = dict(fontInfoVersion3)
		info["woffMetadataLicense"] = dict(text="abc")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text item not a dict
		info = dict(fontInfoVersion3)
		info["woffMetadataLicense"] = dict(text=["abc"])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text item unknown key
		info = dict(fontInfoVersion3)
		info["woffMetadataLicense"] = dict(text=[dict(text="foo", notTheRightKey=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text item missing text
		info = dict(fontInfoVersion3)
		info["woffMetadataLicense"] = dict(text=[dict(language="foo")])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataLicense"] = dict(text=[dict(text=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## url not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataLicense"] = dict(text=[dict(text="foo", url=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## language not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataLicense"] = dict(text=[dict(text="foo", language=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## dir not ltr or rtl
		info = dict(fontInfoVersion3)
		info["woffMetadataLicense"] = dict(text=[dict(text="foo", dir="utd")])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## class not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataLicense"] = dict(text=[{"text"  : "foo", "class" : 1}])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# woffMetadataCopyright
		## unknown attribute
		info = dict(fontInfoVersion3)
		info["woffMetadataCopyright"] = dict(text=[dict(text="foo")], notTheRightKey=1)
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## no text
		info = dict(fontInfoVersion3)
		info["woffMetadataCopyright"] = dict()
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text not a list
		info = dict(fontInfoVersion3)
		info["woffMetadataCopyright"] = dict(text="abc")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text item not a dict
		info = dict(fontInfoVersion3)
		info["woffMetadataCopyright"] = dict(text=["abc"])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text item unknown key
		info = dict(fontInfoVersion3)
		info["woffMetadataCopyright"] = dict(text=[dict(text="foo", notTheRightKey=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text item missing text
		info = dict(fontInfoVersion3)
		info["woffMetadataCopyright"] = dict(text=[dict(language="foo")])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataCopyright"] = dict(text=[dict(text=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## url not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataCopyright"] = dict(text=[dict(text="foo", url=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## language not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataCopyright"] = dict(text=[dict(text="foo", language=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## dir not ltr or rtl
		info = dict(fontInfoVersion3)
		info["woffMetadataCopyright"] = dict(text=[dict(text="foo", dir="utd")])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## class not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataCopyright"] = dict(text=[{"text"  : "foo", "class" : 1}])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		# woffMetadataTrademark
		## unknown attribute
		info = dict(fontInfoVersion3)
		info["woffMetadataTrademark"] = dict(text=[dict(text="foo")], notTheRightKey=1)
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## no text
		info = dict(fontInfoVersion3)
		info["woffMetadataTrademark"] = dict()
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text not a list
		info = dict(fontInfoVersion3)
		info["woffMetadataTrademark"] = dict(text="abc")
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text item not a dict
		info = dict(fontInfoVersion3)
		info["woffMetadataTrademark"] = dict(text=["abc"])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text item unknown key
		info = dict(fontInfoVersion3)
		info["woffMetadataTrademark"] = dict(text=[dict(text="foo", notTheRightKey=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text item missing text
		info = dict(fontInfoVersion3)
		info["woffMetadataTrademark"] = dict(text=[dict(language="foo")])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## text not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataTrademark"] = dict(text=[dict(text=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## url not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataTrademark"] = dict(text=[dict(text="foo", url=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## language not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataTrademark"] = dict(text=[dict(text="foo", language=1)])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## dir not ltr or rtl
		info = dict(fontInfoVersion3)
		info["woffMetadataTrademark"] = dict(text=[dict(text="foo", dir="utd")])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())
		## class not a string
		info = dict(fontInfoVersion3)
		info["woffMetadataTrademark"] = dict(text=[{"text"  : "foo", "class" : 1}])
		self._writeInfoToPlist(info)
		reader = UFOReader(self.dstDir)
		self.assertRaises(UFOLibError, reader.readInfo, TestInfoObject())


class WriteFontInfoVersion1TestCase(unittest.TestCase):

	def setUp(self):
		self.dstDir = tempfile.mktemp()
		os.mkdir(self.dstDir)

	def tearDown(self):
		shutil.rmtree(self.dstDir)

	def makeInfoObject(self):
		infoObject = TestInfoObject()
		for attr, value in fontInfoVersion2.items():
			setattr(infoObject, attr, value)
		return infoObject

	def readPlist(self):
		path = os.path.join(self.dstDir, "fontinfo.plist")
		return readPlist(path)

	def testWrite(self):
		infoObject = self.makeInfoObject()
		writer = UFOWriter(self.dstDir, formatVersion=1)
		writer.writeInfo(infoObject)
		writtenData = self.readPlist()
		for attr, originalValue in fontInfoVersion1.items():
			newValue = writtenData[attr]
			self.assertEqual(newValue, originalValue)

	def testFontStyleConversion(self):
		fontStyle1To2 = {
			64 : "regular",
			1  : "italic",
			32 : "bold",
			33 : "bold italic"
		}
		for old, new in fontStyle1To2.items():
			infoObject = self.makeInfoObject()
			infoObject.styleMapStyleName = new
			writer = UFOWriter(self.dstDir, formatVersion=1)
			writer.writeInfo(infoObject)
			writtenData = self.readPlist()
			self.assertEqual(writtenData["fontStyle"], old)

	def testWidthNameConversion(self):
		widthName1To2 = {
			"Ultra-condensed" : 1,
			"Extra-condensed" : 2,
			"Condensed"		  : 3,
			"Semi-condensed"  : 4,
			"Medium (normal)" : 5,
			"Semi-expanded"	  : 6,
			"Expanded"		  : 7,
			"Extra-expanded"  : 8,
			"Ultra-expanded"  : 9
		}
		for old, new in widthName1To2.items():
			infoObject = self.makeInfoObject()
			infoObject.openTypeOS2WidthClass = new
			writer = UFOWriter(self.dstDir, formatVersion=1)
			writer.writeInfo(infoObject)
			writtenData = self.readPlist()
			self.assertEqual(writtenData["widthName"], old)


class WriteFontInfoVersion2TestCase(unittest.TestCase):

	def setUp(self):
		self.dstDir = tempfile.mktemp()
		os.mkdir(self.dstDir)

	def tearDown(self):
		shutil.rmtree(self.dstDir)

	def makeInfoObject(self):
		infoObject = TestInfoObject()
		for attr, value in fontInfoVersion2.items():
			setattr(infoObject, attr, value)
		return infoObject

	def readPlist(self):
		path = os.path.join(self.dstDir, "fontinfo.plist")
		return readPlist(path)

	def testWrite(self):
		infoObject = self.makeInfoObject()
		writer = UFOWriter(self.dstDir, formatVersion=2)
		writer.writeInfo(infoObject)
		writtenData = self.readPlist()
		for attr, originalValue in fontInfoVersion2.items():
			newValue = writtenData[attr]
			self.assertEqual(newValue, originalValue)

	def testGenericWrite(self):
		# familyName
		infoObject = self.makeInfoObject()
		infoObject.familyName = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# styleName
		infoObject = self.makeInfoObject()
		infoObject.styleName = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# styleMapFamilyName
		infoObject = self.makeInfoObject()
		infoObject.styleMapFamilyName = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# styleMapStyleName
		## not a string
		infoObject = self.makeInfoObject()
		infoObject.styleMapStyleName = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## out of range
		infoObject = self.makeInfoObject()
		infoObject.styleMapStyleName = "REGULAR"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# versionMajor
		infoObject = self.makeInfoObject()
		infoObject.versionMajor = "1"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# versionMinor
		infoObject = self.makeInfoObject()
		infoObject.versionMinor = "0"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# copyright
		infoObject = self.makeInfoObject()
		infoObject.copyright = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# trademark
		infoObject = self.makeInfoObject()
		infoObject.trademark = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# unitsPerEm
		infoObject = self.makeInfoObject()
		infoObject.unitsPerEm = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# descender
		infoObject = self.makeInfoObject()
		infoObject.descender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# xHeight
		infoObject = self.makeInfoObject()
		infoObject.xHeight = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# capHeight
		infoObject = self.makeInfoObject()
		infoObject.capHeight = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# ascender
		infoObject = self.makeInfoObject()
		infoObject.ascender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# italicAngle
		infoObject = self.makeInfoObject()
		infoObject.italicAngle = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testHeadWrite(self):
		# openTypeHeadCreated
		## not a string
		infoObject = self.makeInfoObject()
		infoObject.openTypeHeadCreated = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## invalid format
		infoObject = self.makeInfoObject()
		infoObject.openTypeHeadCreated = "2000-Jan-01 00:00:00"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeHeadLowestRecPPEM
		infoObject = self.makeInfoObject()
		infoObject.openTypeHeadLowestRecPPEM = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeHeadFlags
		infoObject = self.makeInfoObject()
		infoObject.openTypeHeadFlags = [-1]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testHheaWrite(self):
		# openTypeHheaAscender
		infoObject = self.makeInfoObject()
		infoObject.openTypeHheaAscender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeHheaDescender
		infoObject = self.makeInfoObject()
		infoObject.openTypeHheaDescender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeHheaLineGap
		infoObject = self.makeInfoObject()
		infoObject.openTypeHheaLineGap = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeHheaCaretSlopeRise
		infoObject = self.makeInfoObject()
		infoObject.openTypeHheaCaretSlopeRise = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeHheaCaretSlopeRun
		infoObject = self.makeInfoObject()
		infoObject.openTypeHheaCaretSlopeRun = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeHheaCaretOffset
		infoObject = self.makeInfoObject()
		infoObject.openTypeHheaCaretOffset = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testNameWrite(self):
		# openTypeNameDesigner
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameDesigner = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameDesignerURL
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameDesignerURL = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameManufacturer
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameManufacturer = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameManufacturerURL
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameManufacturerURL = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameLicense
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameLicense = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameLicenseURL
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameLicenseURL = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameVersion
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameVersion = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameUniqueID
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameUniqueID = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameDescription
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameDescription = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNamePreferredFamilyName
		infoObject = self.makeInfoObject()
		infoObject.openTypeNamePreferredFamilyName = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNamePreferredSubfamilyName
		infoObject = self.makeInfoObject()
		infoObject.openTypeNamePreferredSubfamilyName = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameCompatibleFullName
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameCompatibleFullName = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameSampleText
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameSampleText = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameWWSFamilyName
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameWWSFamilyName = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameWWSSubfamilyName
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameWWSSubfamilyName = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testOS2Write(self):
		# openTypeOS2WidthClass
		## not an int
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2WidthClass = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## out or range
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2WidthClass = 15
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2WeightClass
		infoObject = self.makeInfoObject()
		## not an int
		infoObject.openTypeOS2WeightClass = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## out of range
		infoObject.openTypeOS2WeightClass = -50
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2Selection
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2Selection = [-1]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2VendorID
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2VendorID = 1234
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2Panose
		## not an int
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2Panose = [0, 1, 2, 3, 4, 5, 6, 7, 8, str(9)]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too few values
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2Panose = [0, 1, 2, 3]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2Panose = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2FamilyClass
		## not an int
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2FamilyClass = [0, str(1)]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too few values
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2FamilyClass = [1]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2FamilyClass = [1, 1, 1]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## out of range
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2FamilyClass = [1, 20]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2UnicodeRanges
		## not an int
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2UnicodeRanges = ["0"]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## out of range
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2UnicodeRanges = [-1]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2CodePageRanges
		## not an int
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2CodePageRanges = ["0"]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## out of range
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2CodePageRanges = [-1]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2TypoAscender
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2TypoAscender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2TypoDescender
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2TypoDescender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2TypoLineGap
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2TypoLineGap = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2WinAscent
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2WinAscent = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2WinDescent
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2WinDescent = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2Type
		## not an int
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2Type = ["1"]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## out of range
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2Type = [-1]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SubscriptXSize
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SubscriptXSize = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SubscriptYSize
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SubscriptYSize = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SubscriptXOffset
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SubscriptXOffset = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SubscriptYOffset
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SubscriptYOffset = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SuperscriptXSize
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SuperscriptXSize = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SuperscriptYSize
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SuperscriptYSize = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SuperscriptXOffset
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SuperscriptXOffset = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SuperscriptYOffset
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SuperscriptYOffset = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2StrikeoutSize
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2StrikeoutSize = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2StrikeoutPosition
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2StrikeoutPosition = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testVheaWrite(self):
		# openTypeVheaVertTypoAscender
		infoObject = self.makeInfoObject()
		infoObject.openTypeVheaVertTypoAscender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeVheaVertTypoDescender
		infoObject = self.makeInfoObject()
		infoObject.openTypeVheaVertTypoDescender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeVheaVertTypoLineGap
		infoObject = self.makeInfoObject()
		infoObject.openTypeVheaVertTypoLineGap = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeVheaCaretSlopeRise
		infoObject = self.makeInfoObject()
		infoObject.openTypeVheaCaretSlopeRise = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeVheaCaretSlopeRun
		infoObject = self.makeInfoObject()
		infoObject.openTypeVheaCaretSlopeRun = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeVheaCaretOffset
		infoObject = self.makeInfoObject()
		infoObject.openTypeVheaCaretOffset = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testFONDWrite(self):
		# macintoshFONDFamilyID
		infoObject = self.makeInfoObject()
		infoObject.macintoshFONDFamilyID = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# macintoshFONDName
		infoObject = self.makeInfoObject()
		infoObject.macintoshFONDName = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testPostscriptWrite(self):
		# postscriptFontName
		infoObject = self.makeInfoObject()
		infoObject.postscriptFontName = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptFullName
		infoObject = self.makeInfoObject()
		infoObject.postscriptFullName = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptSlantAngle
		infoObject = self.makeInfoObject()
		infoObject.postscriptSlantAngle = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptUniqueID
		infoObject = self.makeInfoObject()
		infoObject.postscriptUniqueID = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptUnderlineThickness
		infoObject = self.makeInfoObject()
		infoObject.postscriptUnderlineThickness = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptUnderlinePosition
		infoObject = self.makeInfoObject()
		infoObject.postscriptUnderlinePosition = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptIsFixedPitch
		infoObject = self.makeInfoObject()
		infoObject.postscriptIsFixedPitch = 2
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptBlueValues
		## not a list
		infoObject = self.makeInfoObject()
		infoObject.postscriptBlueValues = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## uneven value count
		infoObject = self.makeInfoObject()
		infoObject.postscriptBlueValues = [500]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.postscriptBlueValues = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptOtherBlues
		## not a list
		infoObject = self.makeInfoObject()
		infoObject.postscriptOtherBlues = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## uneven value count
		infoObject = self.makeInfoObject()
		infoObject.postscriptOtherBlues = [500]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.postscriptOtherBlues = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptFamilyBlues
		## not a list
		infoObject = self.makeInfoObject()
		infoObject.postscriptFamilyBlues = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## uneven value count
		infoObject = self.makeInfoObject()
		infoObject.postscriptFamilyBlues = [500]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.postscriptFamilyBlues = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptFamilyOtherBlues
		## not a list
		infoObject = self.makeInfoObject()
		infoObject.postscriptFamilyOtherBlues = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## uneven value count
		infoObject = self.makeInfoObject()
		infoObject.postscriptFamilyOtherBlues = [500]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.postscriptFamilyOtherBlues = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptStemSnapH
		## not list
		infoObject = self.makeInfoObject()
		infoObject.postscriptStemSnapH = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.postscriptStemSnapH = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptStemSnapV
		## not list
		infoObject = self.makeInfoObject()
		infoObject.postscriptStemSnapV = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.postscriptStemSnapV = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptBlueFuzz
		infoObject = self.makeInfoObject()
		infoObject.postscriptBlueFuzz = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptBlueShift
		infoObject = self.makeInfoObject()
		infoObject.postscriptBlueShift = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptBlueScale
		infoObject = self.makeInfoObject()
		infoObject.postscriptBlueScale = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptForceBold
		infoObject = self.makeInfoObject()
		infoObject.postscriptForceBold = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptDefaultWidthX
		infoObject = self.makeInfoObject()
		infoObject.postscriptDefaultWidthX = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptNominalWidthX
		infoObject = self.makeInfoObject()
		infoObject.postscriptNominalWidthX = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptWeightName
		infoObject = self.makeInfoObject()
		infoObject.postscriptWeightName = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptDefaultCharacter
		infoObject = self.makeInfoObject()
		infoObject.postscriptDefaultCharacter = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptWindowsCharacterSet
		infoObject = self.makeInfoObject()
		infoObject.postscriptWindowsCharacterSet = -1
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# macintoshFONDFamilyID
		infoObject = self.makeInfoObject()
		infoObject.macintoshFONDFamilyID = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# macintoshFONDName
		infoObject = self.makeInfoObject()
		infoObject.macintoshFONDName = 123
		writer = UFOWriter(self.dstDir, formatVersion=2)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)


class WriteFontInfoVersion3TestCase(unittest.TestCase):

	def setUp(self):
		self.dstDir = tempfile.mktemp()
		os.mkdir(self.dstDir)


	def tearDown(self):
		shutil.rmtree(self.dstDir)

	def makeInfoObject(self):
		infoObject = TestInfoObject()
		for attr, value in fontInfoVersion3.items():
			setattr(infoObject, attr, value)
		return infoObject

	def readPlist(self):
		path = os.path.join(self.dstDir, "fontinfo.plist")
		return readPlist(path)

	def testWrite(self):
		infoObject = self.makeInfoObject()
		writer = UFOWriter(self.dstDir, formatVersion=3)
		writer.writeInfo(infoObject)
		writtenData = self.readPlist()
		for attr, originalValue in fontInfoVersion3.items():
			newValue = writtenData[attr]
			self.assertEqual(newValue, originalValue)

	def testGenericWrite(self):
		# familyName
		infoObject = self.makeInfoObject()
		infoObject.familyName = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# styleName
		infoObject = self.makeInfoObject()
		infoObject.styleName = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# styleMapFamilyName
		infoObject = self.makeInfoObject()
		infoObject.styleMapFamilyName = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# styleMapStyleName
		## not a string
		infoObject = self.makeInfoObject()
		infoObject.styleMapStyleName = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## out of range
		infoObject = self.makeInfoObject()
		infoObject.styleMapStyleName = "REGULAR"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# versionMajor
		infoObject = self.makeInfoObject()
		infoObject.versionMajor = "1"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# versionMinor
		infoObject = self.makeInfoObject()
		infoObject.versionMinor = "0"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# copyright
		infoObject = self.makeInfoObject()
		infoObject.copyright = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# trademark
		infoObject = self.makeInfoObject()
		infoObject.trademark = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# unitsPerEm
		infoObject = self.makeInfoObject()
		infoObject.unitsPerEm = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# descender
		infoObject = self.makeInfoObject()
		infoObject.descender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# xHeight
		infoObject = self.makeInfoObject()
		infoObject.xHeight = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# capHeight
		infoObject = self.makeInfoObject()
		infoObject.capHeight = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# ascender
		infoObject = self.makeInfoObject()
		infoObject.ascender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# italicAngle
		infoObject = self.makeInfoObject()
		infoObject.italicAngle = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testGaspWrite(self):
		# not a list
		infoObject = self.makeInfoObject()
		infoObject.openTypeGaspRangeRecords = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# empty list
		infoObject = self.makeInfoObject()
		infoObject.openTypeGaspRangeRecords = []
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# not a dict
		infoObject = self.makeInfoObject()
		infoObject.openTypeGaspRangeRecords = ["abc"]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# dict not properly formatted
		infoObject = self.makeInfoObject()
		infoObject.openTypeGaspRangeRecords = [dict(rangeMaxPPEM=0xFFFF, notTheRightKey=1)]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		infoObject = self.makeInfoObject()
		infoObject.openTypeGaspRangeRecords = [dict(notTheRightKey=1, rangeGaspBehavior=[0])]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# not an int for ppem
		infoObject = self.makeInfoObject()
		infoObject.openTypeGaspRangeRecords = [dict(rangeMaxPPEM="abc", rangeGaspBehavior=[0]), dict(rangeMaxPPEM=0xFFFF, rangeGaspBehavior=[0])]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# not a list for behavior
		infoObject = self.makeInfoObject()
		infoObject.openTypeGaspRangeRecords = [dict(rangeMaxPPEM=10, rangeGaspBehavior="abc"), dict(rangeMaxPPEM=0xFFFF, rangeGaspBehavior=[0])]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# invalid behavior value
		infoObject = self.makeInfoObject()
		infoObject.openTypeGaspRangeRecords = [dict(rangeMaxPPEM=10, rangeGaspBehavior=[-1]), dict(rangeMaxPPEM=0xFFFF, rangeGaspBehavior=[0])]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# not sorted
		infoObject = self.makeInfoObject()
		infoObject.openTypeGaspRangeRecords = [dict(rangeMaxPPEM=0xFFFF, rangeGaspBehavior=[0]), dict(rangeMaxPPEM=10, rangeGaspBehavior=[-1])]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# no 0xFFFF
		infoObject = self.makeInfoObject()
		infoObject.openTypeGaspRangeRecords = [dict(rangeMaxPPEM=10, rangeGaspBehavior=[0]), dict(rangeMaxPPEM=20, rangeGaspBehavior=[-1])]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testHeadWrite(self):
		# openTypeHeadCreated
		## not a string
		infoObject = self.makeInfoObject()
		infoObject.openTypeHeadCreated = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## invalid format
		infoObject = self.makeInfoObject()
		infoObject.openTypeHeadCreated = "2000-Jan-01 00:00:00"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeHeadLowestRecPPEM
		infoObject = self.makeInfoObject()
		infoObject.openTypeHeadLowestRecPPEM = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeHeadFlags
		infoObject = self.makeInfoObject()
		infoObject.openTypeHeadFlags = [-1]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testHheaWrite(self):
		# openTypeHheaAscender
		infoObject = self.makeInfoObject()
		infoObject.openTypeHheaAscender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeHheaDescender
		infoObject = self.makeInfoObject()
		infoObject.openTypeHheaDescender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeHheaLineGap
		infoObject = self.makeInfoObject()
		infoObject.openTypeHheaLineGap = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeHheaCaretSlopeRise
		infoObject = self.makeInfoObject()
		infoObject.openTypeHheaCaretSlopeRise = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeHheaCaretSlopeRun
		infoObject = self.makeInfoObject()
		infoObject.openTypeHheaCaretSlopeRun = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeHheaCaretOffset
		infoObject = self.makeInfoObject()
		infoObject.openTypeHheaCaretOffset = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testNameWrite(self):
		# openTypeNameDesigner
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameDesigner = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameDesignerURL
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameDesignerURL = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameManufacturer
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameManufacturer = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameManufacturerURL
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameManufacturerURL = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameLicense
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameLicense = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameLicenseURL
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameLicenseURL = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameVersion
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameVersion = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameUniqueID
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameUniqueID = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameDescription
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameDescription = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNamePreferredFamilyName
		infoObject = self.makeInfoObject()
		infoObject.openTypeNamePreferredFamilyName = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNamePreferredSubfamilyName
		infoObject = self.makeInfoObject()
		infoObject.openTypeNamePreferredSubfamilyName = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameCompatibleFullName
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameCompatibleFullName = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameSampleText
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameSampleText = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameWWSFamilyName
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameWWSFamilyName = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameWWSSubfamilyName
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameWWSSubfamilyName = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeNameRecords
		## not a list
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameRecords = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## not a dict
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameRecords = ["abc"]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## invalid dict structure
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameRecords = [dict(foo="bar")]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## incorrect keys
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameRecords = [
			dict(nameID=1, platformID=1, encodingID=1, languageID=1, string="Name Record.", foo="bar")
		]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameRecords = [
			dict(platformID=1, encodingID=1, languageID=1, string="Name Record.")
		]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameRecords = [
			dict(nameID=1, encodingID=1, languageID=1, string="Name Record.")
		]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameRecords = [
			dict(nameID=1, platformID=1, languageID=1, string="Name Record.")
		]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameRecords = [
			dict(nameID=1, platformID=1, encodingID=1, string="Name Record.")
		]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameRecords = [
			dict(nameID=1, platformID=1, encodingID=1, languageID=1)
		]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## invalid values
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameRecords = [
			dict(nameID="1", platformID=1, encodingID=1, languageID=1, string="Name Record.")
		]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameRecords = [
			dict(nameID=1, platformID="1", encodingID=1, languageID=1, string="Name Record.")
		]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameRecords = [
			dict(nameID=1, platformID=1, encodingID="1", languageID=1, string="Name Record.")
		]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameRecords = [
			dict(nameID=1, platformID=1, encodingID=1, languageID="1", string="Name Record.")
		]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameRecords = [
			dict(nameID=1, platformID=1, encodingID=1, languageID=1, string=1)
		]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## duplicate
		infoObject = self.makeInfoObject()
		infoObject.openTypeNameRecords = [
			dict(nameID=1, platformID=1, encodingID=1, languageID=1, string="Name Record."),
			dict(nameID=1, platformID=1, encodingID=1, languageID=1, string="Name Record.")
		]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testOS2Write(self):
		# openTypeOS2WidthClass
		## not an int
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2WidthClass = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## out or range
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2WidthClass = 15
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2WeightClass
		infoObject = self.makeInfoObject()
		## not an int
		infoObject.openTypeOS2WeightClass = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## out of range
		infoObject.openTypeOS2WeightClass = -50
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2Selection
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2Selection = [-1]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2VendorID
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2VendorID = 1234
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2Panose
		## not an int
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2Panose = [0, 1, 2, 3, 4, 5, 6, 7, 8, str(9)]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too few values
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2Panose = [0, 1, 2, 3]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2Panose = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2FamilyClass
		## not an int
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2FamilyClass = [0, str(1)]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too few values
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2FamilyClass = [1]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2FamilyClass = [1, 1, 1]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## out of range
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2FamilyClass = [1, 20]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2UnicodeRanges
		## not an int
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2UnicodeRanges = ["0"]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## out of range
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2UnicodeRanges = [-1]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2CodePageRanges
		## not an int
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2CodePageRanges = ["0"]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## out of range
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2CodePageRanges = [-1]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2TypoAscender
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2TypoAscender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2TypoDescender
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2TypoDescender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2TypoLineGap
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2TypoLineGap = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2WinAscent
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2WinAscent = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2WinAscent = -1
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2WinDescent
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2WinDescent = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2WinDescent = -1
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2Type
		## not an int
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2Type = ["1"]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## out of range
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2Type = [-1]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SubscriptXSize
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SubscriptXSize = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SubscriptYSize
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SubscriptYSize = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SubscriptXOffset
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SubscriptXOffset = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SubscriptYOffset
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SubscriptYOffset = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SuperscriptXSize
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SuperscriptXSize = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SuperscriptYSize
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SuperscriptYSize = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SuperscriptXOffset
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SuperscriptXOffset = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2SuperscriptYOffset
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2SuperscriptYOffset = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2StrikeoutSize
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2StrikeoutSize = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeOS2StrikeoutPosition
		infoObject = self.makeInfoObject()
		infoObject.openTypeOS2StrikeoutPosition = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testVheaWrite(self):
		# openTypeVheaVertTypoAscender
		infoObject = self.makeInfoObject()
		infoObject.openTypeVheaVertTypoAscender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeVheaVertTypoDescender
		infoObject = self.makeInfoObject()
		infoObject.openTypeVheaVertTypoDescender = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeVheaVertTypoLineGap
		infoObject = self.makeInfoObject()
		infoObject.openTypeVheaVertTypoLineGap = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeVheaCaretSlopeRise
		infoObject = self.makeInfoObject()
		infoObject.openTypeVheaCaretSlopeRise = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeVheaCaretSlopeRun
		infoObject = self.makeInfoObject()
		infoObject.openTypeVheaCaretSlopeRun = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# openTypeVheaCaretOffset
		infoObject = self.makeInfoObject()
		infoObject.openTypeVheaCaretOffset = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testFONDWrite(self):
		# macintoshFONDFamilyID
		infoObject = self.makeInfoObject()
		infoObject.macintoshFONDFamilyID = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# macintoshFONDName
		infoObject = self.makeInfoObject()
		infoObject.macintoshFONDName = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testPostscriptWrite(self):
		# postscriptFontName
		infoObject = self.makeInfoObject()
		infoObject.postscriptFontName = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptFullName
		infoObject = self.makeInfoObject()
		infoObject.postscriptFullName = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptSlantAngle
		infoObject = self.makeInfoObject()
		infoObject.postscriptSlantAngle = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptUniqueID
		infoObject = self.makeInfoObject()
		infoObject.postscriptUniqueID = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptUnderlineThickness
		infoObject = self.makeInfoObject()
		infoObject.postscriptUnderlineThickness = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptUnderlinePosition
		infoObject = self.makeInfoObject()
		infoObject.postscriptUnderlinePosition = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptIsFixedPitch
		infoObject = self.makeInfoObject()
		infoObject.postscriptIsFixedPitch = 2
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptBlueValues
		## not a list
		infoObject = self.makeInfoObject()
		infoObject.postscriptBlueValues = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## uneven value count
		infoObject = self.makeInfoObject()
		infoObject.postscriptBlueValues = [500]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.postscriptBlueValues = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptOtherBlues
		## not a list
		infoObject = self.makeInfoObject()
		infoObject.postscriptOtherBlues = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## uneven value count
		infoObject = self.makeInfoObject()
		infoObject.postscriptOtherBlues = [500]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.postscriptOtherBlues = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptFamilyBlues
		## not a list
		infoObject = self.makeInfoObject()
		infoObject.postscriptFamilyBlues = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## uneven value count
		infoObject = self.makeInfoObject()
		infoObject.postscriptFamilyBlues = [500]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.postscriptFamilyBlues = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptFamilyOtherBlues
		## not a list
		infoObject = self.makeInfoObject()
		infoObject.postscriptFamilyOtherBlues = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## uneven value count
		infoObject = self.makeInfoObject()
		infoObject.postscriptFamilyOtherBlues = [500]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.postscriptFamilyOtherBlues = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptStemSnapH
		## not list
		infoObject = self.makeInfoObject()
		infoObject.postscriptStemSnapH = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.postscriptStemSnapH = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptStemSnapV
		## not list
		infoObject = self.makeInfoObject()
		infoObject.postscriptStemSnapV = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## too many values
		infoObject = self.makeInfoObject()
		infoObject.postscriptStemSnapV = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptBlueFuzz
		infoObject = self.makeInfoObject()
		infoObject.postscriptBlueFuzz = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptBlueShift
		infoObject = self.makeInfoObject()
		infoObject.postscriptBlueShift = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptBlueScale
		infoObject = self.makeInfoObject()
		infoObject.postscriptBlueScale = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptForceBold
		infoObject = self.makeInfoObject()
		infoObject.postscriptForceBold = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptDefaultWidthX
		infoObject = self.makeInfoObject()
		infoObject.postscriptDefaultWidthX = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptNominalWidthX
		infoObject = self.makeInfoObject()
		infoObject.postscriptNominalWidthX = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptWeightName
		infoObject = self.makeInfoObject()
		infoObject.postscriptWeightName = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptDefaultCharacter
		infoObject = self.makeInfoObject()
		infoObject.postscriptDefaultCharacter = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# postscriptWindowsCharacterSet
		infoObject = self.makeInfoObject()
		infoObject.postscriptWindowsCharacterSet = -1
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# macintoshFONDFamilyID
		infoObject = self.makeInfoObject()
		infoObject.macintoshFONDFamilyID = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# macintoshFONDName
		infoObject = self.makeInfoObject()
		infoObject.macintoshFONDName = 123
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)

	def testWOFFWrite(self):
		# woffMajorVersion
		infoObject = self.makeInfoObject()
		infoObject.woffMajorVersion = 1.0
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		infoObject = self.makeInfoObject()
		infoObject.woffMajorVersion = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# woffMinorVersion
		infoObject = self.makeInfoObject()
		infoObject.woffMinorVersion = 1.0
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		infoObject = self.makeInfoObject()
		infoObject.woffMinorVersion = "abc"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# woffMetadataUniqueID
		## none
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataUniqueID = None
		writer = UFOWriter(self.dstDir, formatVersion=3)
		writer.writeInfo(TestInfoObject())
		## not a dict
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataUniqueID = 1
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## unknown key
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataUniqueID = dict(id="foo", notTheRightKey=1)
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## no id
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataUniqueID = dict()
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## not a string for id
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataUniqueID = dict(id=1)
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## empty string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataUniqueID = dict(id="")
		writer = UFOWriter(self.dstDir, formatVersion=3)
		writer.writeInfo(TestInfoObject())
		# woffMetadataVendor
		## no name
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataVendor = dict(url="foo")
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## name not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataVendor = dict(name=1, url="foo")
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## name an empty string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataVendor = dict(name="", url="foo")
		writer = UFOWriter(self.dstDir, formatVersion=3)
		writer.writeInfo(TestInfoObject())
		## no URL
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataVendor = dict(name="foo")
		writer = UFOWriter(self.dstDir, formatVersion=3)
		writer.writeInfo(TestInfoObject())
		## url not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataVendor = dict(name="foo", url=1)
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## url empty string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataVendor = dict(name="foo", url="")
		writer = UFOWriter(self.dstDir, formatVersion=3)
		writer.writeInfo(TestInfoObject())
		## have dir
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataVendor = dict(name="foo", url="bar", dir="ltr")
		writer = UFOWriter(self.dstDir, formatVersion=3)
		writer.writeInfo(TestInfoObject())
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataVendor = dict(name="foo", url="bar", dir="rtl")
		writer = UFOWriter(self.dstDir, formatVersion=3)
		writer.writeInfo(TestInfoObject())
		## dir not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataVendor = dict(name="foo", url="bar", dir=1)
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## dir not ltr or rtl
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataVendor = dict(name="foo", url="bar", dir="utd")
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## have class
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataVendor = {"name"  : "foo", "url" : "bar", "class" : "hello"}
		writer = UFOWriter(self.dstDir, formatVersion=3)
		writer.writeInfo(TestInfoObject())
		## class not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataVendor = {"name"  : "foo", "url" : "bar", "class" : 1}
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## class empty string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataVendor = {"name"  : "foo", "url" : "bar", "class" : ""}
		writer = UFOWriter(self.dstDir, formatVersion=3)
		writer.writeInfo(TestInfoObject())
		# woffMetadataCredits
		## no credits attribute
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCredits = {}
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## unknown attribute
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCredits = dict(credits=[dict(name="foo")], notTheRightKey=1)
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## not a list
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCredits = dict(credits="abc")
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## no elements in credits
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCredits = dict(credits=[])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## credit not a dict
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCredits = dict(credits=["abc"])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## unknown key
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCredits = dict(credits=[dict(name="foo", notTheRightKey=1)])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## no name
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCredits = dict(credits=[dict(url="foo")])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## name not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCredits = dict(credits=[dict(name=1)])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## url not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCredits = dict(credits=[dict(name="foo", url=1)])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## role not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCredits = dict(credits=[dict(name="foo", role=1)])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## dir not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCredits = dict(credits=[dict(name="foo", dir=1)])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## dir not ltr or rtl
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCredits = dict(credits=[dict(name="foo", dir="utd")])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## class not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCredits = dict(credits=[{"name"  : "foo", "class" : 1}])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# woffMetadataDescription
		## no url
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataDescription = dict(text=[dict(text="foo")])
		writer.writeInfo(TestInfoObject())
		## url not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataDescription = dict(text=[dict(text="foo")], url=1)
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## no text
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataDescription = dict(url="foo")
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text not a list
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataDescription = dict(text="abc")
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text item not a dict
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataDescription = dict(text=["abc"])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text item unknown key
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataDescription = dict(text=[dict(text="foo", notTheRightKey=1)])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text item missing text
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataDescription = dict(text=[dict(language="foo")])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataDescription = dict(text=[dict(text=1)])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## url not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataDescription = dict(text=[dict(text="foo", url=1)])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## language not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataDescription = dict(text=[dict(text="foo", language=1)])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## dir not ltr or rtl
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataDescription = dict(text=[dict(text="foo", dir="utd")])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## class not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataDescription = dict(text=[{"text"  : "foo", "class" : 1}])
		writer = UFOWriter(self.dstDir, formatVersion=3)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# woffMetadataLicense
		## no url
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataLicense = dict(text=[dict(text="foo")])
		writer.writeInfo(TestInfoObject())
		## url not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataLicense = dict(text=[dict(text="foo")], url=1)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## id not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataLicense = dict(text=[dict(text="foo")], id=1)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## no text
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataLicense = dict(url="foo")
		writer.writeInfo(TestInfoObject())
		## text not a list
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataLicense = dict(text="abc")
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text item not a dict
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataLicense = dict(text=["abc"])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text item unknown key
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataLicense = dict(text=[dict(text="foo", notTheRightKey=1)])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text item missing text
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataLicense = dict(text=[dict(language="foo")])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataLicense = dict(text=[dict(text=1)])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## url not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataLicense = dict(text=[dict(text="foo", url=1)])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## language not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataLicense = dict(text=[dict(text="foo", language=1)])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## dir not ltr or rtl
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataLicense = dict(text=[dict(text="foo", dir="utd")])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## class not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataLicense = dict(text=[{"text"  : "foo", "class" : 1}])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# woffMetadataCopyright
		## unknown attribute
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCopyright = dict(text=[dict(text="foo")], notTheRightKey=1)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## no text
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCopyright = dict()
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text not a list
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCopyright = dict(text="abc")
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text item not a dict
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCopyright = dict(text=["abc"])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text item unknown key
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCopyright = dict(text=[dict(text="foo", notTheRightKey=1)])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text item missing text
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCopyright = dict(text=[dict(language="foo")])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCopyright = dict(text=[dict(text=1)])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## url not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCopyright = dict(text=[dict(text="foo", url=1)])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## language not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCopyright = dict(text=[dict(text="foo", language=1)])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## dir not ltr or rtl
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCopyright = dict(text=[dict(text="foo", dir="utd")])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## class not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataCopyright = dict(text=[{"text"  : "foo", "class" : 1}])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		# woffMetadataTrademark
		## unknown attribute
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataTrademark = dict(text=[dict(text="foo")], notTheRightKey=1)
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## no text
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataTrademark = dict()
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text not a list
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataTrademark = dict(text="abc")
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text item not a dict
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataTrademark = dict(text=["abc"])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text item unknown key
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataTrademark = dict(text=[dict(text="foo", notTheRightKey=1)])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text item missing text
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataTrademark = dict(text=[dict(language="foo")])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## text not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataTrademark = dict(text=[dict(text=1)])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## url not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataTrademark = dict(text=[dict(text="foo", url=1)])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## language not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataTrademark = dict(text=[dict(text="foo", language=1)])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## dir not ltr or rtl
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataTrademark = dict(text=[dict(text="foo", dir="utd")])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)
		## class not a string
		infoObject = self.makeInfoObject()
		infoObject.woffMetadataTrademark = dict(text=[{"text"  : "foo", "class" : 1}])
		self.assertRaises(UFOLibError, writer.writeInfo, info=infoObject)


class UFO3ReadDataTestCase(unittest.TestCase):

	def getFontPath(self):
		import robofab
		path = os.path.dirname(robofab.__file__)
		path = os.path.dirname(path)
		path = os.path.dirname(path)
		path = os.path.join(path, "TestData", "UFO3-Read Data.ufo")
		return path

	def testUFOReaderDataDirectoryListing(self):
		reader = UFOReader(self.getFontPath())
		found = reader.getDataDirectoryListing()
		# filter out the .svn
		found = [path for path in found if ".svn" not in path]
		found = list(sorted(found))
		expected = [
			'data/org.unifiedfontobject.directory/bar/lol.txt',
			'data/org.unifiedfontobject.directory/foo.txt',
			'data/org.unifiedfontobject.file.txt'
		]
		expected = list(sorted(expected))
		self.assertEqual(found, expected)

	def testUFOReaderBytesFromPath(self):
		reader = UFOReader(self.getFontPath())
		found = reader.readBytesFromPath("data/org.unifiedfontobject.file.txt")
		expected = "file.txt"
		self.assertEqual(found, expected)
		found = reader.readBytesFromPath("data/org.unifiedfontobject.directory/bar/lol.txt")
		expected = "lol.txt"
		self.assertEqual(found, expected)
		found = reader.readBytesFromPath("data/org.unifiedfontobject.doesNotExist")
		expected = None
		self.assertEqual(found, expected)

	def testUFOReaderReadFileFromPath(self):
		reader = UFOReader(self.getFontPath())
		fileObject = reader.getReadFileForPath("data/org.unifiedfontobject.file.txt")
		self.assertNotEqual(fileObject, None)
		hasRead = hasattr(fileObject, "read")
		self.assertEqual(hasRead, True)
		fileObject.close()
		fileObject = reader.getReadFileForPath("data/org.unifiedfontobject.doesNotExist")
		self.assertEqual(fileObject, None)


class UFO3WriteDataTestCase(unittest.TestCase):

	def setUp(self):
		self.dstDir = tempfile.mktemp()
		os.mkdir(self.dstDir)

	def tearDown(self):
		shutil.rmtree(self.dstDir)

	def testUFOWriterWriteBytesToPath(self):
		# basic file
		path = "data/org.unifiedfontobject.writebytesbasicfile.txt"
		bytes = "test"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		writer.writeBytesToPath(path, bytes)
		path = os.path.join(self.dstDir, path)
		self.assertEqual(os.path.exists(path), True)
		f = open(path, "rb")
		written = f.read()
		f.close()
		self.assertEqual(bytes, written)
		# basic file with unicode text
		path = "data/org.unifiedfontobject.writebytesbasicunicodefile.txt"
		bytes = u"tëßt"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		writer.writeBytesToPath(path, bytes, encoding="utf8")
		path = os.path.join(self.dstDir, path)
		self.assertEqual(os.path.exists(path), True)
		f = codecs.open(path, "rb")
		written = f.read().decode("utf8")
		f.close()
		self.assertEqual(bytes, written)
		# basic directory
		path = "data/org.unifiedfontobject.writebytesdirectory/level1/level2/file.txt"
		bytes = "test"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		writer.writeBytesToPath(path, bytes)
		path = os.path.join(self.dstDir, path)
		self.assertEqual(os.path.exists(path), True)
		f = open(path, "rb")
		written = f.read()
		f.close()
		self.assertEqual(bytes, written)

	def testUFOWriterWriteFileToPath(self):
		# basic file
		path = "data/org.unifiedfontobject.getwritefile.txt"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		fileObject = writer.getFileObjectForPath(path)
		self.assertNotEqual(fileObject, None)
		hasRead = hasattr(fileObject, "read")
		self.assertEqual(hasRead, True)
		fileObject.close()

	def testUFOWriterRemoveFile(self):
		path1 = "data/org.unifiedfontobject.removefile/level1/level2/file1.txt"
		path2 = "data/org.unifiedfontobject.removefile/level1/level2/file2.txt"
		path3 = "data/org.unifiedfontobject.removefile/level1/file3.txt"
		writer = UFOWriter(self.dstDir, formatVersion=3)
		writer.writeBytesToPath(path1, "test")
		writer.writeBytesToPath(path2, "test")
		writer.writeBytesToPath(path3, "test")
		self.assertEqual(os.path.exists(os.path.join(self.dstDir, path1)), True)
		self.assertEqual(os.path.exists(os.path.join(self.dstDir, path2)), True)
		self.assertEqual(os.path.exists(os.path.join(self.dstDir, path3)), True)
		writer.removeFileForPath(path1)
		self.assertEqual(os.path.exists(os.path.join(self.dstDir, path1)), False)
		self.assertEqual(os.path.exists(os.path.dirname(os.path.join(self.dstDir, path1))), True)
		self.assertEqual(os.path.exists(os.path.join(self.dstDir, path2)), True)
		self.assertEqual(os.path.exists(os.path.join(self.dstDir, path3)), True)
		writer.removeFileForPath(path2)
		self.assertEqual(os.path.exists(os.path.dirname(os.path.join(self.dstDir, path1))), False)
		self.assertEqual(os.path.exists(os.path.join(self.dstDir, path2)), False)
		self.assertEqual(os.path.exists(os.path.join(self.dstDir, path3)), True)
		writer.removeFileForPath(path3)
		self.assertEqual(os.path.exists(os.path.join(self.dstDir, path3)), False)
		self.assertEqual(os.path.exists(os.path.dirname(os.path.join(self.dstDir, path2))), False)
		self.assertEqual(os.path.exists(os.path.join(self.dstDir, "data/org.unifiedfontobject.removefile")), False)
		self.assertRaises(UFOLibError, writer.removeFileForPath, path="metainfo.plist")
		self.assertRaises(UFOLibError, writer.removeFileForPath, path="data/org.unifiedfontobject.doesNotExist.txt")


class ConversionFunctionsTestCase(unittest.TestCase):

	def tearDown(self):
		path = self.getFontPath("TestFont1 (UFO1) converted.ufo")
		if os.path.exists(path):
			shutil.rmtree(path)
		path = self.getFontPath("TestFont1 (UFO2) converted.ufo")
		if os.path.exists(path):
			shutil.rmtree(path)

	def getFontPath(self, fileName):
		import robofab
		path = os.path.dirname(robofab.__file__)
		path = os.path.dirname(path)
		path = os.path.dirname(path)
		path = os.path.join(path, "TestData", fileName)
		return path

	def compareFileStructures(self, path1, path2, expectedInfoData, testFeatures):
		# result
		metainfoPath1 = os.path.join(path1, "metainfo.plist")
		fontinfoPath1 = os.path.join(path1, "fontinfo.plist")
		kerningPath1 = os.path.join(path1, "kerning.plist")
		groupsPath1 = os.path.join(path1, "groups.plist")
		libPath1 = os.path.join(path1, "lib.plist")
		featuresPath1 = os.path.join(path1, "features.plist")
		glyphsPath1 = os.path.join(path1, "glyphs")
		glyphsPath1_contents = os.path.join(glyphsPath1, "contents.plist")
		glyphsPath1_A = os.path.join(glyphsPath1, "A_.glif")
		glyphsPath1_B = os.path.join(glyphsPath1, "B_.glif")
		# expected result
		metainfoPath2 = os.path.join(path2, "metainfo.plist")
		fontinfoPath2 = os.path.join(path2, "fontinfo.plist")
		kerningPath2 = os.path.join(path2, "kerning.plist")
		groupsPath2 = os.path.join(path2, "groups.plist")
		libPath2 = os.path.join(path2, "lib.plist")
		featuresPath2 = os.path.join(path2, "features.plist")
		glyphsPath2 = os.path.join(path2, "glyphs")
		glyphsPath2_contents = os.path.join(glyphsPath2, "contents.plist")
		glyphsPath2_A = os.path.join(glyphsPath2, "A_.glif")
		glyphsPath2_B = os.path.join(glyphsPath2, "B_.glif")
		# look for existence
		self.assertEqual(os.path.exists(metainfoPath1), True)
		self.assertEqual(os.path.exists(fontinfoPath1), True)
		self.assertEqual(os.path.exists(kerningPath1), True)
		self.assertEqual(os.path.exists(groupsPath1), True)
		self.assertEqual(os.path.exists(libPath1), True)
		self.assertEqual(os.path.exists(glyphsPath1), True)
		self.assertEqual(os.path.exists(glyphsPath1_contents), True)
		self.assertEqual(os.path.exists(glyphsPath1_A), True)
		self.assertEqual(os.path.exists(glyphsPath1_B), True)
		if testFeatures:
			self.assertEqual(os.path.exists(featuresPath1), True)
		# look for aggrement
		data1 = readPlist(metainfoPath1)
		data2 = readPlist(metainfoPath2)
		self.assertEqual(data1, data2)
		data1 = readPlist(fontinfoPath1)
		self.assertEqual(sorted(data1.items()), sorted(expectedInfoData.items()))
		data1 = readPlist(kerningPath1)
		data2 = readPlist(kerningPath2)
		self.assertEqual(data1, data2)
		data1 = readPlist(groupsPath1)
		data2 = readPlist(groupsPath2)
		self.assertEqual(data1, data2)
		data1 = readPlist(libPath1)
		data2 = readPlist(libPath2)
		if "UFO1" in libPath1:
			for key in removeFromFormatVersion1Lib:
				if key in data1:
					del data1[key]
		if "UFO1" in libPath2:
			for key in removeFromFormatVersion1Lib:
				if key in data2:
					del data2[key]
		self.assertEqual(data1, data2)
		data1 = readPlist(glyphsPath1_contents)
		data2 = readPlist(glyphsPath2_contents)
		self.assertEqual(data1, data2)
		data1 = readPlist(glyphsPath1_A)
		data2 = readPlist(glyphsPath2_A)
		self.assertEqual(data1, data2)
		data1 = readPlist(glyphsPath1_B)
		data2 = readPlist(glyphsPath2_B)
		self.assertEqual(data1, data2)

	def test1To2(self):
		path1 = self.getFontPath("TestFont1 (UFO1).ufo")
		path2 = self.getFontPath("TestFont1 (UFO1) converted.ufo")
		path3 = self.getFontPath("TestFont1 (UFO2).ufo")
		convertUFOFormatVersion1ToFormatVersion2(path1, path2)
		self.compareFileStructures(path2, path3, expectedFontInfo1To2Conversion, False)

	def test2To1(self):
		path1 = self.getFontPath("TestFont1 (UFO2).ufo")
		path2 = self.getFontPath("TestFont1 (UFO2) converted.ufo")
		path3 = self.getFontPath("TestFont1 (UFO1).ufo")
		convertUFOFormatVersion2ToFormatVersion1(path1, path2)
		self.compareFileStructures(path2, path3, expectedFontInfo2To1Conversion, False)


if __name__ == "__main__":
	from robofab.test.testSupport import runTests
	runTests()
