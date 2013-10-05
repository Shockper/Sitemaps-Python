# -*- coding: utf-8 -*-

#
#	Updated: 2013/06/26
#	Author: Sergi Rodríguez (contact@shockper.com)
#	Better with Python 3, (it works for Python 2 too)
#

import sys, os, datetime
import xml.etree.cElementTree as ET
import xml.dom.minidom as Dom

#Returns true if the string is a number, if not it returns false
def isNumber(string):
	try:
		float(string)
		return True
	except ValueError:
		return False

#Indent generated xml to make it easier to work with it
def reindent(fileDir):
	xml = Dom.parse(fileDir)
	xmlIndent = xml.toprettyxml(encoding="utf-8").decode("utf-8") #Workaround to have xml header with utf-8 declaration

	f = open(fileDir, 'w')
	f.write(xmlIndent)
	f.close()

#Main method
def main():

	#Checking arguments
	if len(sys.argv) < 3:
		sys.exit("Usage: [generate / parse / add] [input.txt / sitemap.xml] (output.txt)")

	if sys.argv[1] == "generate" or sys.argv[1] == "parse" or sys.argv[1] == "add":
		if sys.argv[1] == "generate":
			mode = 0
		elif sys.argv[1] == "parse":
			mode = 1
		elif sys.argv[1] == "add":
			mode = 2
	else:
		sys.exit("Mode should be 'generate', 'parse' or 'add'")

	#Setting up file in and out directions
	fileIn = sys.argv[2]
	fileOut = ''

	if mode == 0 or mode == 1:

		if len(sys.argv) > 3:
			fileOut = sys.argv[3]
		
		if mode == 0:
			if fileOut == '':
				fileOut = "sitemap.xml"
			#Call generate method
			generate(fileIn, fileOut)
	
		elif mode == 1:
			if fileOut == '':
				fileOut = "parsedSitemap.txt"
			#Call parse method
			parse(fileIn, fileOut)
	else:

		if len(sys.argv) < 4:
			sys.exit("Usage: add [input.txt] [sitemap.xml] (output.txt)")
		
		elif sys.argv[3][-3:] != 'xml':
			sys.exit("Usage: add [input.txt] [sitemap.xml] (output.txt)")


		if len(sys.argv) > 4:
			fileOut = sys.argv[4]
		else:
			fileOut = "sitemap.xml"

		xmlIn = sys.argv[3]

		#Call add method
		add(fileIn, xmlIn, fileOut)

#
#	Given a file with priority numbers and URL's on each line,
#	it generates a completed sitemap with current date as lastmod and a monthly changefreq.	
#
#	Arguments: 
#		
#		[1] file.txt with URL's and priority
#		
#		Format example:
#
#		0.9
#		http://www.campingbungalowmaresme.com/
#
#		0.8
#		http://www.campingbungalowmaresme.com/ca.html
#		http://www.campingbungalowmaresme.com/es.html
#
#		0.9
#		http://www.campingbungalowmaresme.com/ca/allotjaments.html
#		http://www.campingbungalowmaresme.com/es/alojamiento.html
#		(empty line)
#
#		IMPORTANT! Last URL must have a newline char (one empty line below)
#
#		[2] (Optional) file output, if not given it's created as "sitemap.xml"
#

def generate(fileIn, fileOut):

	source = open(fileIn, "r")

	#Setup XML
	root = ET.Element("urlset")
	root.set("xmlns","http://www.sitemaps.org/schemas/sitemap/0.9")

	#Prepare priority and date variables
	currentPriority = 0
	now = datetime.datetime.now()
	date = now.strftime("%Y-%m-%d")

	#Start reading the file
	print ("Reading input file...")
	line = source.readline()
	
	if not isNumber(line):
		sys.exit("Error: Input text not correctly formatted, read the README file!")

	while line :

		#If line is empty we do not add it to the sitemap
		if line == '\n':
			line = source.readline()
			continue

		#If its a number we change the priority
		if isNumber(line):
			currentPriority = line[:-1] #Escape new line char
			line = source.readline()
			continue

		#Generate XML structure
		urlTag = ET.SubElement(root, "url")

		urlField = ET.SubElement(urlTag, "loc")
		urlField.text = line[:-1]

		lastMod = ET.SubElement(urlTag, "lastmod")
		lastMod.text = date

		changeFreq = ET.SubElement(urlTag, "changefreq")
		changeFreq.text = "monthly"

		priority = ET.SubElement(urlTag, "priority")
		priority.text = currentPriority

		#Read next line
		line = source.readline()

	#Generate XML and write it
	print("Generating XML file...")
	tree = ET.ElementTree(root)
	tree.write(fileOut, encoding="utf-8", xml_declaration=True)

	#Reindent XML
	print("Reindenting...")
	reindent(fileOut)
	print("Done! Saved at " + fileOut + ".")

#
#	Given an XML file containing a sitemap, it will generate a file ready to pass as 
#	an argument to the generate() function, it doesn't save changefreq or lastmod.
#
#	Arguments: 
#		
#		[1] file.xml containing a sitemap
#		
#
#		[2] (Optional) file output, if not given it's created as "parsedSitemap.txt"
#

def parse(fileIn, fileOut):

	currentPriority = 0
	stringOut = ''

	#Get XML file
	print("Reading XML file...")
	try:
		tree = ET.parse(fileIn)
	except:
		sys.exit("Error: XML not correctly parsed, aborting!")

	root = tree.getroot()

	# Note to anyone who uses this code in the future:
	#	All the tags have the sitemap declaration attached, in example:
	#
	#	print(root.tag)
	#
	#	Returns: {http://www.sitemaps.org/schemas/sitemap/0.9}urlset instead of just 'urlset'
	#	
	#	In order to fix it, we declarate a "tagFix" variable with the declaration,
	#	So to use the find() method we add the real tag to this variable.
	
	tagFix = root.tag[:-6] #Declaration url without 'urlset' text

	#Generate content
	print("Generating new file...")
	for url in root.findall(tagFix + 'url'):

		loc = url.find(tagFix + 'loc').text
		lastMod = url.find(tagFix + 'lastmod').text
		changeFreq = url.find(tagFix + 'changefreq').text
		priority = url.find(tagFix + 'priority').text

		#If priority changes, we write it to the file
		if priority != currentPriority:
			currentPriority = priority
			stringOut += currentPriority + '\n'

		#Write url + new line
		stringOut += loc + '\n'

	#Save the file
	f = open(fileOut, 'w')
	f.write(stringOut)
	f.close()
	print("Done! Saved at " + fileOut + ".")

#
#	Given a file with priority numbers and URL's on each line, and a sitemap in XML,
#	it will add the URL's to the sitemap, with current date as lastmod and a monthly changefreq.
#
#	Arguments: 
#
#		[1] file.txt with URL's and priority
#
#		[2] file.xml containing a sitemap
#		
#		[3] (Optional) file output, if not given it's created as "parsedSitemap.txt"
#

def add(fileIn, xmlIn, fileOut):

	#First, parse the XML file and create an 
	#input file for the generate() method
	parse(xmlIn, "tmp")

	f1 = open("tmp", 'a')
	f2 = open(fileIn, 'r')

	#Then read the input file and append it's content
	#to the temporal file.
	line = f2.readline()
	while line:
		f1.write(line)
		line = f2.readline()

	f1.close()
	f2.close()

	#Call the generate function with the new file
	generate("tmp", fileOut)
	os.remove("tmp")

#Init with main function
if __name__ == '__main__':
	main()