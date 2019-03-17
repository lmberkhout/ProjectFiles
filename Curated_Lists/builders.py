#! /usr/bin/env python
from __future__ import print_function
import six
# ######################################################################
# Customize output here by                                             #
#    1 - defining group symbols and provide listing order              #
#    2 - stating whether that group should be listed in either         #
#           'fileorder' or                                             #
#           'alphaorder'                                               #
#    Note that the '_' group is the one with no explicit label         #
GROUP_ORDER = ['*', '$', '!', '_']
LISTING_ORDER = {'*': 'fileorder', '$': 'alphaorder',
                 '!': 'alphaorder', '_': 'alphaorder'}
#                                                                      #
# Next step is to edit 'builders.txt' to add the group symbols and     #
#      reorder to suit.                                                #
# ######################################################################


class Authors:
    """Read in and format author lists for papers."""
    def __init__(self, epoch='H1C'):
        self.filein = 'builders_{}.txt'.format(epoch.upper())
        self.fileout = self.filein.split('.')[0] + '.tex'

    def getAuthors(self, filein=None):
        if filein is not None:
            self.filein = filein
        print('Reading ' + self.filein)
        self.authors = {}
        self.affiliationList = []
        self.fileOrder = []

        with open(self.filein, 'r') as f:
            for line in f:
                if len(line.strip()) < 2 or line.strip()[0] == '#':
                    continue
                if line.strip()[0] == '&':
                    data = line.strip()[1:].split()
                    if len(data) == 1:
                        id_type = data[0]
                    elif len(data) == 2:
                        for k in self.authors.keys():
                            if data[0].lower() in k:
                                self.authors[k]['ID'][id_type] = data[1]
                    continue
                # Affiliations
                if line[0] == '@':
                    affiliation = line[1:].strip()
                    self.affiliationList.append(affiliation)
                    continue
                # Names
                name = line.strip().split()
                if len(name) != 2 and len(name) != 3:
                    print("Invalid name format:  {}".format(name))
                    continue
                if name[0][0] in GROUP_ORDER:
                    group = name[0][0]
                    firstName = name[0][1:]
                else:
                    group = '_'
                    firstName = name[0]
                lastName = name[-1]
                middleName = ''
                if len(name) == 3:
                    middleName = name[1]
                akey = lastName.lower() + firstName.lower()
                if akey in self.authors.keys():
                    self.authors[akey]['affiliations'].append(affiliation)
                else:
                    self.authors[akey] = {'first': firstName, 'middle': middleName, 'last': lastName,
                                          'affiliations': [affiliation], 'group': group, 'ID': {}}
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

    def show_id(self):
        for a in self.authororder:
            for i, v in six.iteritems(self.authors[a]['ID']):
                print("{} {}:  {}".format(i, self.authors[a]['last'], v))

    def niceList(self):
        for aff in self.affiliationList:
            print('\n' + aff)
            for au in self.alphaOrder:
                for auaff in self.authors[au]['affiliations']:
                    if auaff == aff:
                        niceFirst = self.authors[au]['first'].replace('~', ' ')
                        niceMiddle = self.authors[au]['middle'].replace('~', ' ')
                        niceLast = self.authors[au]['last'].replace('~', ' ')
                        print("\t{} {} {}".format(niceFirst, niceMiddle, niceLast))

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

    def get_latex_affiliation(self):
        s = ''
        for k in self.authororder:
            author = '{} {} {}'.format(self.authors[k]['first'], self.authors[k]['middle'], self.authors[k]['last'])
            s += '\\author{{{}}}\n'.format(author)
            for affil in self.authors[k]['affiliations']:
                s += '\\affiliation{{{}}}\n'.format(affil)
            s += '\n'
        return s

    def write_affil_tex(self, s):
        print("Writing {}".format(self.fileout))
        with open(self.fileout, 'w') as f:
            f.write(s)

    def get_latex_footnote(self):
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
    ap.add_argument('-e', '--epoch', help="Epoch of builders list (H0C, H1C) [H1C]", default='H1C')
    ap.add_argument('-v', '--version', help="Version type (aas, footnote) [aas]", default='aas')
    args = ap.parse_args()

    h = Authors(args.epoch)
    h.getAuthors()
    if args.screen_only:
        h.niceList()
        sys.exit()
    if args.version == 'footnote':
        h.setAffiliationNumbers()
    h.group_ordered_list()
    if args.version == 'footnote':
        s = h.get_latex_footnote()
    else:
        s = h.get_latex_affiliation()
    h.write_affil_tex(s)
    h.show_id()
