"""
FROM MULTIPLE PDB FILES, SUCH AS ONE PDB FILE PER TIMEPOINT, EXTRACT PDB FILES WITH A SPECIFIC WINDOW SIZE (e.g. 9)
MINIMUM RESIDUE NUMBER IS 1 (see samples folder for usage example)
"""

import os, sys, shutil

def printUsage(err=''):
	print("ERROR: %s" % err)
	print("USAGE: %s srcpath windowsize [trgPath]" % sys.argv[0])
	sys.exit(1)

# Parse directory name containing pdb's with all residues
origdir = sys.argv[1]
if not os.path.exists(origdir):
	printUsage("Path %s does not exist" % origdir)

# Parse window size as second argument
windowsize = sys.argv[2]
try:
	int(windowsize)
except:
	printUsage("Window size %s is not valid" % windowsize)

# Parse output directory name as third (optional) argument
if len(sys.argv) > 3:
	outputdir = sys.argv[3]
else:
	outputdir = '.'

# Get number of residues from first file
pdbs = os.listdir(origdir)
# Expand relative paths to absolute
pdbs = [os.path.realpath(os.path.join(origdir,pdb)) for pdb in pdbs]

# Get first pdb to check number of residues
firstpdb = pdbs[0]

# Open the pdb file and get all lines as text
fp = open(firstpdb, 'r')
lines = fp.readlines()
fp.close()
# Reverse the lines to get residue number from the top
lines.reverse()
numres = 0
for l in lines:
	if l.startswith('ATOM'):
		numres = filter(None,l.split(' '))[4]
		break

# If there was a problem with parsing, exit and print error
if not numres:
	print("Could not get the number of residues from file %s" % firstpdb)
	sys.exit(1)


# Output each window into a separate directory
i = int(numres)
j = i - int(windowsize) + 1

overwriteall = False

if not os.path.exists(outputdir):
	os.makedirs(outputdir)
os.chdir(outputdir)

while j > 0:
	# Directory name of the window
	dname = '%d_%d' % (j, i)
	# Check if it already exists, if it does, ask the user what they want to do if they didn't already tell us to overwrite all
	if os.path.exists(dname):
		if overwriteall:
			shutil.rmtree(dname)
		else:
			answer = raw_input("Overwrite %s? (Y)es (N)o (A)ll: " % dname)
			answer = answer.lower()
			if answer == 'y':
				shutil.rmtree(dname)
			elif answer == 'n':
				j-=1
				i-=1
				continue
			elif answer == 'a':
				overwriteall = True
				continue

	# Make the directory
	os.makedirs(dname)

	for pdb in pdbs:
		trgpath = os.path.join(dname, os.path.basename(pdb))
		src = open(pdb, 'r')
		trg = open(trgpath, 'w')

		lines = src.readlines()
		src.close()
		for l in lines:
			splitl = filter(None,l.split(' '))
			if l.startswith("ATOM") and (int(splitl[4]) > i or int(splitl[4]) < j):
				continue
			trg.write(l)

		trg.close()

	j-=1
	i-=1

print("Done")
