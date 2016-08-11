#! /usr/bin/env python
import argparse

from lxml import etree


def main(oldxml, newxml, outfile):

    oldtree = etree.parse(oldxml)
    newtree = etree.parse(newxml)

    # Find removed datasets
    datasetids = etree.XPath(
        "//erddapDatasets/dataset/@datasetID",
        smart_strings=False
    )

    oldids = set(list(datasetids(oldtree)))
    newids = set(list(datasetids(newtree)))
    removedids = list(oldids.difference(newids))

    find_dataset = etree.XPath("//erddapDatasets/dataset[@datasetID=$name]")
    for r in removedids:
        # **** NOTE ****
        # This won't handle a dataset that was marked as active=false
        # and then came back into the picture. It won't remove active=false
        # and the datasets will be in a state of purgatory. This shouldn't
        # happen often, if ever.
        dnode = find_dataset(oldtree, name=r)[0]
        if dnode.get('active') == 'false':
            # Don't do anything, it's ready to be removed from the datasets.xml
            pass
        else:
            # Deactivate the dataset
            dnode.set('active', 'false')
            ds = newtree.getroot()
            ds.append(dnode)

    with open(outfile, 'wt') as f:
        f.write(etree.tostring(newtree, encoding='ISO-8859-1', pretty_print=True, xml_declaration=True).decode('iso-8859-1'))
        f.write('\n')


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('oldxml',
                        help="Old datasets.xml file",
                        nargs='?')
    parser.add_argument('newxml',
                        help="New datasets.xml file",
                        nargs='?')
    parser.add_argument('outfile',
                        help="File to write the final datasets.xml",
                        nargs='?')
    args = parser.parse_args()

    main(args.oldxml, args.newxml, args.outfile)
