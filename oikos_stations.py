#! /usr/bin/env python
import argparse

from slugify import UniqueSlugify
import requests
from lxml import etree


def main(outfile, region, publisher, publisher_email, institution, publishers, highlight, highlight_title):

    # Convert highlight list to ints
    if highlight:
        highlight = [ int(x) for x in highlight ]

    if publishers:
        publishers = [ int(x) for x in publishers ]

    params = {
        'appregion': region,
        'realtimeonly': 'false',
        'verbose': 'true',
        'jsoncallback': 'false',
        'method': 'GetStationsResultSetRowsJSON',
        'version': 3
    }
    r = requests.get('http://pdx.axiomalaska.com/stationsensorservice/getDataValues', params=params)
    r.raise_for_status()
    r = r.json()

    sources = r.get('sources')

    slug = UniqueSlugify(separator='_', to_lower=True)

    datasets = []
    for s in sorted(r.get("stations"), key=lambda x: x['id']):

        if publishers and s.get('publisherId') not in publishers:
            continue

        urn = slug(s.get('urn').replace('urn:ioos:station:', ''))
        dataset = etree.Element("dataset", type="EDDTableFromAxiomStation", datasetID=urn)

        source = etree.SubElement(dataset, "sourceUrl")
        source.text = 'http://pdx.axiomalaska.com/stationsensorservice/'

        sid = s.get('id')
        station = etree.SubElement(dataset, "stationId")
        station.text = str(sid)

        reload = etree.SubElement(dataset, "reloadEveryNMinutes")
        reload.text = '60'

        # Attributes
        atts = etree.SubElement(dataset, "addAttributes")

        label = s.get('label')
        label = label.replace('(', '').replace(')', '')
        if sid in highlight:
            label = '{} {}'.format(highlight_title, label)
        title = etree.SubElement(atts, "att", name="title")
        title.text = label

        source_id = s.get('sourceId')
        institution = sources[str(source_id)]['label']
        instit = etree.SubElement(atts, "att", name="institution")
        instit.text = institution

        try:
            url = sources[str(source_id)]['url']
            infourl = etree.SubElement(atts, "att", name="infoUrl")
            infourl.text = url
        except KeyError:
            pass

        pubname = etree.SubElement(atts, "att", name="publisher_name")
        pubname.text = publisher

        pubemail = etree.SubElement(atts, "att", name="publisher_email")
        pubemail.text = publisher_email

        datasets.append(dataset)

    with open(outfile, 'wt') as f:
        for d in datasets:
            try:
                f.write(etree.tostring(d, encoding='ISO-8859-1', pretty_print=True, xml_declaration=False).decode('iso-8859-1'))
                f.write('\n')
            except UnicodeDecodeError:
                print("ERROR WITH: {}\n\n".format(etree.tostring(d)))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '--output',
                        help="File to output XML to",
                        default='output.xml',
                        nargs='?')
    parser.add_argument('-r', '--region',
                        help="Regional subset (defaults to 'all')",
                        default='all',
                        nargs='?')
    parser.add_argument('-p', '--publisher',
                        help="Publisher (defaults to 'Axiom Data Science')",
                        default='Axiom Data Science',
                        nargs='?')
    parser.add_argument('-e', '--publisher_email',
                        help="Publisher Email (defaults to 'axiom+sensors@axiomdatascience.com')",
                        default='axiom+sensors@axiomdatascience.com',
                        nargs='?')
    parser.add_argument('-i', '--institution',
                        help="Default Institution (defaults to 'Axiom Data Science') if one can't be found",
                        default='Axiom Data Science',
                        nargs='?')
    parser.add_argument('-d', '--publishers',
                        help="Subset by these provider IDs",
                        default=[],
                        nargs='*')
    parser.add_argument('-l', '--highlight',
                        help="Put these stations at the top",
                        default=[],
                        nargs='*')
    parser.add_argument('-t', '--highlight_title',
                        help="Use this for the highlight title",
                        default='*',
                        nargs='?')
    args = parser.parse_args()

    main(args.output, args.region, args.publisher, args.publisher_email, args.institution, args.publishers, args.highlight, args.highlight_title)
