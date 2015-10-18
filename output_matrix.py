#! /usr/bin/env python3
import sys, os, numpy

# Check that a map file was passed as an argument
if len(sys.argv) < 3:
	print("Program Usage: Python <map file> <dump file>")
	print("Exiting...")
	exit()
	
# Define module class
class Module:
	
	def __init__(self, p_name):
	
		# The name of the root node of the module
		self.name = p_name
		
		# All of the other nodes in this module
		self.members = []
	
	def addNode(self, p_node):
		self.members.append(p_node)
		
# Returns the node name from a line in the map file
def getNodeName(line):
	nodeName = ""
	startIndex = line.find("\"") + 1
	endIndex = line.find("\"", startIndex + 1)
	nodeName = line[startIndex:endIndex]
	return nodeName
	
# Returns the module number from a line in the map file
def getModuleNumber(line):
	moduleNumber = ""
	startIndex = 0
	endIndex = line.find(":")
	moduleNumber = line[startIndex:endIndex]
	return moduleNumber

	
# Load file
print("Loading file: ", sys.argv[1])
textFile = open(os.getcwd() + "/" + sys.argv[1], "r")
textFileData = textFile.readlines()

# Parse file and build up a list of modules
modules = [] # List of modules
currentModule = "-1" # number of the current module as a string
for line in textFileData:

	# Searching for the start in the map file
	if currentModule == "-1":
		if line.find("*Nodes") != -1:
			currentModule = "0"
	
	# Building modules
	else:
	
		# Finish searching
		if line.find("*Links") != -1:
			break
			
		# Get current module number
		moduleNumber = getModuleNumber(line)
		
		# Start a new module
		if currentModule != moduleNumber:
			currentModule = moduleNumber
			newModule = Module(getNodeName(line))
			modules = modules + [newModule]
			
		# Add node to module
		else:
			modules[len(modules)-1].addNode(getNodeName(line))
	
# Calculate matrix rows and cols
nTopics = len(modules)
nWords = 0
for module in modules:
	nWords += 1
	nWords += len(module.members)
print("nTopics: " + str(nTopics) + ", nWords: " + str(nWords))

# Build matrix data
print("Building matrix data...")
matrixData = ""
r = 0
c = 0
while r < nTopics:
    while c < nWords:
        matrixData += str(1) + " "
        c += 1
    if r != nTopics - 1:
        matrixData += "; "
    c = 0
    r += 1
    
# Create matrix
print("Making matrix...")
matrix = numpy.matrix(matrixData)

# Dump matrix
print("Dumping matrix...")
matrix.dump(sys.argv[2])
print("Finished!")
    
	
