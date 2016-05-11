#! /usr/bin/env python
#################################################################
###Customize output via the script at the bottom of this file.###
#################################################################

class Authors:
    """Read in and format author lists for papers"""
    def __init__(self,filein='builders.txt'):
        self.filein = filein
        self.authors = {}
        self.affiliationList = []
        self.fileOrder = []
        self.groupSymbols = ['*','@','#','%']
    def getAuthors(self,filein=None):
        if filein is not None:
            self.filein = filein
            print 'Setting input file to '+filein
        print
        print 'Reading '+self.filein
        fpin = open(self.filein,'r')
        for line in fpin:
            if line.strip()[0] == '#' or len(line.strip())==0:
                continue
            data = line.split(':')
            if len(data)==2:  #Process valid data line
                affiliation = data[0].strip()
                self.affiliationList.append(affiliation)
                nameslist = data[1].strip()
                names = nameslist.split(',')
                for name in names:
                    n = name.split()
                    firstName = n[0]
                    group = False
                    for sym in self.groupSymbols:
                        if sym in firstName:
	                    group = sym
                            firstName = firstName.strip(sym)
                            break
                    if len(n) == 1:
                        middleInitial = ''
                        lastName = ''
                    elif len(n) == 2:
                        middleInitial = ''
                        lastName = n[1]
                    elif len(n) == 3:
                        middleInitial = n[1]
                        lastName = n[2]
                    else:
                        print line
                        lastName = 'null'
                    if lastName != 'null':
                        akey = lastName.lower()+firstName.lower()
                        if akey in self.authors.keys():
                            print 'Another entry for %s %s now at %s' % (firstName,lastName,affiliation)
                            self.authors[akey][3].append(affiliation)
                        else:
      		            self.authors[akey] = [firstName,middleInitial,lastName,[affiliation],group]
      		            self.fileOrder.append(akey)
      		        if group:
      		            print 'Found group '+group+':  '+akey
      	print
        fpin.close()
        self.alphaOrder = sorted(self.authors.keys())
    def firstName(self,name):
        return self.authors[name][0]
    def middleName(self,name):
        return self.authors[name][1]
    def lastName(self,name):
        return self.authors[name][2]
    def affiliations(self,name):
        return self.authors[name][3]
    def isGroup(self,name):
        return self.authors[name][4]
    def setAffiliationNumbers(self):
        self.affilNums = {}
        i = 1
        for a in self.affiliationList:
            if a not in self.affilNums.keys():
                self.affilNums[a] = i
                if i==1:
                    self.affilOrdered=a+', '
                else:
	            self.affilOrdered+='$^{'+str(i)+'}$'+a+', '
                i+=1
        self.affilOrdered = self.affilOrdered.strip().strip(',')
        return self.affilOrdered
    def affiliationNumbers(self,name):
        affil = self.affiliations(name)
        nums = []
        for a in affil:
            nums.append(self.affilNums[a])
        return nums

#################################################################
###Customize output via this script.                          ###
#################################################################
if __name__ == '__main__':
    h = Authors()
    h.getAuthors()
    affilList = h.setAffiliationNumbers()
    #############################Get order	
    authororder = []
    #######HERE'S WHERE YOU ADD THE LOGIC TO SORT THE AUTHORS IN DESIRED ORDER######
    ###h.fileOrder has the list as they appeared in the document
    ###h.alphaOrder has the list in alphabetical order
    ###
    for n in h.fileOrder:
        if h.isGroup(n) == '*':
            authororder.append(n)
    for n in h.alphaOrder:
        if h.isGroup(n) == '@':
            authororder.append(n)
    for n in h.alphaOrder:
        if not h.isGroup(n):
   	    authororder.append(n)
    ################################################################################
        
    ##############################Write out
    ###This assumes that author 1 is in the first listed affiliation
    s = '\\author{'
    for i,a in enumerate(authororder):
        affilstr = str(h.affiliationNumbers(a)).strip('[').strip(']')
        if i==0:
            atxt = '\\footnote{%s}' % (affilList)
            a0 = h.affiliationNumbers(a)
            if len(a0)>1:
                atxt+='~$^{'
                for j in range(1,len(a0)):
                    atxt+=','+str(a0[j])
                atxt+='}$'
        else:
            atxt = '$^{'+affilstr+'}$'
        s+= "%s %s %s%s, " % (h.firstName(a),h.middleName(a), h.lastName(a), atxt)
    s=s.strip().strip(',')+'}\n\n'
    affil0 = h.affiliationNumbers(authororder[0])[0]-1
    s+='\\begin{document}\n\\maketitle\n\\setcounter{footnote}{0}\n\n'
    
    fpout= open('authors.tex','w')
    fpout.write(s)
    fpout.close()
    
    print s

