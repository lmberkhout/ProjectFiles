#! /usr/bin/env python
from __future__ import print_function
import six
import sys
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


def make_nice(s):
    return s.replace('~', ' ')


class Authors:
    """
    Read in and format author lists for papers, or other purposes like NSF annual reports.

    Parameters
    ----------
    epoch : str
        The epoch(s) to use.  It is a csv string.
    output_type : str
        Output type to use.  Other tex or csv
    """
    def __init__(self, epoch='H1C', output_type='tex'):
        epoch = epoch.split(',')
        self.filesin = []
        self.fileout = 'out'
        for e in epoch:
            self.filesin.append('builders_{}.txt'.format(e.upper()))
            self.fileout = self.fileout + '_{}'.format(e.upper())
        self.fileout = self.fileout + '.' + output_type

    def getAuthors(self):
        self.authors = {}
        self.affiliationList = []
        self.fileOrder = []

        for filein in self.filesin:
            print("Reading " + filein)
            with open(filein, 'r') as f:
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
                                              'nice': [make_nice(firstName), make_nice(middleName), make_nice(lastName)],
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
            print('\n-----' + aff)
            for au in self.alphaOrder:
                for auaff in self.authors[au]['affiliations']:
                    if auaff == aff:
                        print("{} {} {}".format(self.authors[au]['nice'][0], self.authors[au]['nice'][0], self.authors[au]['nice'][0]))

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

    def match_emails(self, contact_csv_file=None):
        import csv
        if contact_csv_file is None or not contact_csv_file.endswith('csv'):
            print("Not matching e-mails [{}]".format(contact_csv_file))
            return

        print("Matching e-mails with {}".format(contact_csv_file))
        contacts = {}
        with open(contact_csv_file) as f:
            ac = csv.reader(f, delimiter='\t')
            for row in ac:
                try:
                    key = row[0][0].lower() + row[1].lower()
                except IndexError:
                    continue
                contacts[key] = row[4]
        filast = list(contacts.keys())

        for au in self.alphaOrder:
            this_filast = self.authors[au]['nice'][0][0].lower() + self.authors[au]['nice'][2].lower()
            if this_filast in filast:
                self.authors[au]['email'] = contacts[this_filast]

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
        print("Writing tex {}".format(self.fileout))
        with open(self.fileout, 'w') as f:
            f.write(s)

    def write_csv(self):
        print("Writing csv {}".format(self.fileout))
        with open(self.fileout, 'w') as f:
            for au in self.alphaOrder:
                first = self.authors[au]['nice'][0]
                middle = self.authors[au]['nice'][1]
                last = self.authors[au]['nice'][2]
                if 'email' in self.authors[au].keys():
                    email = self.authors[au]['email']
                else:
                    email = ''
                print("{},{},{},{}\n".format(first, middle, last, email), file=f, end='')

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


tex_version_types = ['aas', 'footnote']
csv_version_types = ['nsf']
epochs = ['H0C', 'H1C', 'H2C']
if __name__ == '__main__':
    import argparse
    import sys

    ap = argparse.ArgumentParser()
    ap.add_argument('-s', '--screen-only', dest='screen_only', help="Print list to screen.", action='store_true')
    ap.add_argument('-e', '--epoch', help="Epoch of builders list [H2C].  Can be a csv-list.", default='H2C')
    ap.add_argument('-v', '--version', help="Version type [aas]", choices=tex_version_types + csv_version_types, default='aas')
    ap.add_argument('--contact-csv-file', dest='contact_csv_file', help="A csv file containing e-mail addresses [None]", default=None)
    ap.add_argument('--orcid', help="Just show known ORCID IDs", action='store_true')
    args = ap.parse_args()

    if args.version in tex_version_types:
        output_type = 'tex'
    else:
        output_type = 'csv'

    h = Authors(epoch=args.epoch, output_type=output_type)
    h.getAuthors()
    if args.screen_only:
        h.niceList()
        sys.exit()
    if args.orcid:
        h.show_id()
        sys.exit()

    if args.version == 'footnote':
        h.setAffiliationNumbers()
    h.group_ordered_list()
    h.match_emails(contact_csv_file=args.contact_csv_file)
    if args.version == 'footnote':
        s = h.get_latex_footnote()
    elif args.version == 'aas':
        s = h.get_latex_affiliation()

    if output_type == 'tex':
        h.write_affil_tex(s)
    else:
        h.write_csv()
