#! /usr/bin/env python
# ######################################################################
# Customize output here by                                             #
#    1 - defining group symbols and provide listing order              #
#    2 - stating whether that group should be listed in either         #
#           'fileorder' or                                             #
#           'alphaorder'                                               #
#    Note that the '_' group is the one with no explicit label         #
GROUP_ORDER = ['*', '@', '_']
LISTING_ORDER = {'*': 'fileorder', '@': 'alphaorder', '_': 'alphaorder'}
#                                                                      #
# Next step is to edit 'builders.txt' to add the group symbols and     #
#      reorder to suit.                                                #
# ######################################################################


class Authors:
    """Read in and format author lists for papers."""
    def __init__(self, filein='builders.txt'):
        self.filein = filein

    def getAuthors(self, filein=None):
        if filein is not None:
            self.filein = filein
        print 'Reading ' + self.filein
        self.authors = {}
        self.affiliationList = []
        self.fileOrder = []

        with open(self.filein, 'r') as f:
            for line in f:
                data = line.split(':')
                if line.strip()[0] == '#' or len(data) != 2:
                    continue
                # Affiliations
                affiliation = data[0].strip()
                self.affiliationList.append(affiliation)
                # Names
                nameslist = data[1].strip()
                names = nameslist.split(',')
                for name in names:
                    n = name.strip().split()
                    if len(n) != 2 and len(n) != 3:
                        print "Invalid name format:  ", name.strip(), len(n)
                        continue
                    firstName = n[0]
                    lastName = n[-1]
                    middleName = ''
                    if len(n) == 3:
                        middleName = n[1]
                    group = '_'
                    for sym in GROUP_ORDER:
                        if sym in firstName:
                            group = sym
                            firstName = firstName.strip(sym)
                            break
                    akey = lastName.lower() + firstName.lower()
                    if akey in self.authors.keys():
                        self.authors[akey]['affiliations'].append(affiliation)
                    else:
                        self.authors[akey] = {'first': firstName,
                                              'middle': middleName,
                                              'last': lastName,
                                              'affiliations': [affiliation],
                                              'group': group}
                        self.fileOrder.append(akey)
        self.alphaOrder = sorted(self.authors.keys())

    def setAffiliationNumbers(self):
        self.affilNums = {}
        i = 1
        for a in self.affiliationList:
            if a not in self.affilNums.keys():
                self.affilNums[a] = i
                if i == 1:
                    self.affilOrdered = a + ', '
                else:
                    self.affilOrdered += '$^{' + str(i) + '}$' + a + ', '
                i += 1
        self.affilOrdered = self.affilOrdered.strip().strip(',')

    def getAffiliationNumbers(self, key):
        affil = self.authors[key]['affiliations']
        nums = []
        for a in affil:
            nums.append(self.affilNums[a])
        return nums

    def niceList(self):
        for aff in self.affiliationList:
            print '\n' + aff
            for au in self.alphaOrder:
                for auaff in self.authors[au]['affiliations']:
                    if auaff == aff:
                        niceFirst = self.authors[au]['first'].replace('~', ' ')
                        niceMiddle = self.authors[au]['middle'].replace('~', ' ')
                        niceLast = self.authors[au]['last'].replace('~', ' ')
                        print "\t%s %s %s" % (niceFirst, niceMiddle, niceLast)

    def group_ordered_list(self):
        self.authororder = []
        for symbol in GROUP_ORDER:
            if LISTING_ORDER[symbol] == 'fileorder':
                ordering = self.fileOrder
            else:
                ordering = self.alphaOrder
            for n in ordering:
                if self.authors[n]['group'] == symbol:
                    self.authororder.append(n)
        return self.authororder

    def get_latex(self):
        print("This doesn't handle the first affiliation number reliably, unless the first author is from the first affiliation")
        print("Need to fix it (or can reorder in builders.txt in the meantime)")
        s = '\\documentstyle{article}\n\\title{Authors}\n'
        s += '\\author{'
        for i, a in enumerate(self.authororder):
            author_name = "%s %s %s" % (self.authors[a]['first'], self.authors[a]['middle'], self.authors[a]['last'])
            affilstr = str(self.getAffiliationNumbers(a)).strip('[').strip(']')
            # ##This assumes that author 1 is in the first listed affiliation ==> not a good assumption...
            if i == 0:
                atxt = '\\footnote{%s}' % (self.affilOrdered)
                a0 = self.getAffiliationNumbers(a)
                if len(a0) > 1:
                    atxt += '~$^{'
                    for j in range(1, len(a0)):
                        atxt += ',' + str(a0[j])
                    atxt += '}$'
            else:
                atxt = '$^{' + affilstr + '}$'
            s += "%s%s, " % (author_name, atxt)
        s = s.strip().strip(',') + '}\n\n'
        s += '\\begin{document}\n\\maketitle\n\\setcounter{footnote}{0}\n\n\\end{document}\n'
        return s


if __name__ == '__main__':
    import argparse
    import sys

    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--screen_only', help="Print list to screen.", action='store_true')
    args = ap.parse_args()

    h = Authors()
    h.getAuthors()
    if args.screen_only:
        h.niceList()
        sys.exit()
    h.setAffiliationNumbers()
    h.group_ordered_list()
    s = h.get_latex()

    print "Writing authors.tex"
    with open('authors.tex', 'w') as f:
        f.write(s)
