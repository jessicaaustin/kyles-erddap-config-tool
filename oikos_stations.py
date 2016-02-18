#! /usr/bin/env python
import argparse

import requests
from lxml import etree


def main(outfile, region, publisher, publisher_email, institution):

    params = {
        'appregion': region,
        'realtimeonly': 'false',
        'verbose': 'true',
        'jsoncallback': 'false',
        'method': 'GetStationsResultSetRowsJSON',
        'version': 2
    }
    r = requests.get('http://pdx.axiomalaska.com/stationsensorservice/getDataValues', params=params)
    r.raise_for_status()

    datasets = []
    for s in sorted(r.json().get("stations"), key=lambda x: x['id']):

        sid = s.get('id')

        dataset = etree.Element("dataset", type="EDDTableFromAxiomStation", datasetID="station_{}".format(sid))

        source = etree.SubElement(dataset, "sourceUrl")
        source.text = 'http://pdx.axiomalaska.com/stationsensorservice/'

        station = etree.SubElement(dataset, "stationId")
        station.text = str(sid)

        reload = etree.SubElement(dataset, "reloadEveryNMinutes")
        reload.text = '60'

        # Attributes
        atts = etree.SubElement(dataset, "addAttributes")
        title = etree.SubElement(atts, "att", name="title")
        title.text = s.get('label')

        instit = etree.SubElement(atts, "att", name="institution")
        instit.text = institution

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
                        help="Institution (defaults to 'Axiom Data Science')",
                        default='Axiom Data Science',
                        nargs='?')
    args = parser.parse_args()

    main(args.output, args.region, args.publisher, args.publisher_email, args.institution)
