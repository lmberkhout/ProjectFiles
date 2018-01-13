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
        return self.affilOrdered

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


if __name__ == '__main__':
    import argparse
    import sys

    ap = argparse.ArgumentParser()
    ap.add_argument('printout_style', nargs='?', help='cryptic printout style', default='all')
    ap.add_argument('-s', '--screen_only', help="Print list to screen.", action='store_true')
    args = ap.parse_args()

    h = Authors()
    h.getAuthors()
    if args.screen_only:
        h.niceList()
        sys.exit()
    affilList = h.setAffiliationNumbers()
    authororder = []
    for symbol in GROUP_ORDER:
        if LISTING_ORDER[symbol] == 'fileorder':
            ordering = h.fileOrder
        else:
            ordering = h.alphaOrder
        for n in ordering:
            if h.authors[n]['group'] == symbol:
                authororder.append(n)

    s = '\\documentstyle{article}\n\\title{Authors}\n'
    s += '\\author{'
    if args.printout_style == 'all':
        # ##This assumes that author 1 is in the first listed affiliation
        for i, a in enumerate(authororder):
            affilstr = str(h.getAffiliationNumbers(a)).strip('[').strip(']')
            if i == 0:
                atxt = '\\footnote{%s}' % (affilList)
                a0 = h.getAffiliationNumbers(a)
                if len(a0) > 1:
                    atxt += '~$^{'
                    for j in range(1, len(a0)):
                        atxt += ',' + str(a0[j])
                    atxt += '}$'
            else:
                atxt = '$^{' + affilstr + '}$'
            s += "%s %s %s%s, " % (h.authors[a]['first'], h.authors[a]['middle'], h.authors[a]['last'], atxt)
        s = s.strip().strip(',') + '}\n\n'
        s += '\\begin{document}\n\\maketitle\n\\setcounter{footnote}{0}\n\n\\end{document}\n'
        affil0 = h.getAffiliationNumbers(authororder[0])[0] - 1
    elif args.printout_style == 'collab':
        for i, a in enumerate(authororder):
            affilstr = str(h.getAffiliationNumbers(a)).strip('[').strip(']')
            atxt = '\\altaffilmark{%s}' % (affilstr)
            s += "%s %s %s%s, " % (h.authors[a]['first'], h.authors[a]['middle'], h.authors[a]['last'], atxt)
        s = s.strip().strip(',') + '}\n\n'
        s += '\\affil{HERA Collaboration}'
        for i, a in enumerate(h.affilNums):
            s += '\\altaffiltext{%d}{%s}\n' % (h.affilNums[a], a)
        s += '\\begin{document}\n\\maketitle\n\n\\end{document}\n'

    print "Writing authors.tex"
    fpout = open('authors.tex', 'w')
    fpout.write(s)
    fpout.close()
