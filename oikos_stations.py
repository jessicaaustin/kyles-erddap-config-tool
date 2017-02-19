#! /usr/bin/env python
import argparse

import requests
from lxml import etree
from assetid.urn import IoosUrn
from slugify import UniqueSlugify


def main(outfile, region_id):

    params = {}
    # Either a name or integer
    try:
        params['region_id'] = int(region_id)
    except ValueError:
        params['region_name'] = region_id

    r = requests.get('http://sensors.axds.co/stationsensorservice/getRegionMetadata', params=params)
    r.raise_for_status()

    try:
        r = r.json()
    except BaseException:
        print("No stations available for the '{}' region".format(region_id))
        return

    slug = UniqueSlugify(separator='_', to_lower=True)

    datasets = []

    stats = r[0].get("stations")
    stats = [ x for x in stats if x.get('add_to_erddap') is True ]
    stats = sorted(stats, key=lambda x: x['id'])

    print("Exporting {} {} stations to ERDDAP XML".format(len(stats), region_id))
    for s in stats:
        # Compute the Station URN
        # Precedence:
        #  1.) 'urn' global_attribute
        #  2.) 'id'  and 'naming_authority' global_attributes
        #  3.) Station URN from sensor service
        gas = s.get('global_attributes', {})
        if 'urn' in gas:
            iurn = IoosUrn.from_string(gas['urn'].lower())
            gas['id'] = iurn.label
            gas['naming_authority'] = iurn.authority
        if 'naming_authority' in gas and 'id' in gas:
            station_urn = '{}.{}'.format(gas['naming_authority'], gas['id']).lower()
        else:
            station_urn = s['urn'].lower()

        station_urn = station_urn.replace('urn:ioos:station:', '')
        dataset = etree.Element("dataset", type="EDDTableFromAxiomStation", datasetID=slug(station_urn))

        source = etree.SubElement(dataset, "sourceUrl")
        source.text = 'http://sensors.axds.co/stationsensorservice/'

        station = etree.SubElement(dataset, "stationId")
        station.text = str(s.get('id'))

        reload = etree.SubElement(dataset, "reloadEveryNMinutes")
        reload.text = '360'

        # Attributes
        atts = etree.SubElement(dataset, "addAttributes")

        # Title
        label = gas.get('title', s.get('label'))
        label = label.replace('(', '').replace(')', '')
        if s.get('highlight_in_erddap') is True:
            label = '* ' + label
        title = etree.SubElement(atts, "att", name="title")
        title.text = label

        # Institution
        owner = gas.get('institution', s.get('owner_label'))
        owner = owner.replace('(', '').replace(')', '')
        own = etree.SubElement(atts, "att", name="institution")
        own.text = owner

        # All other attributes
        for k, v in gas.items():
            ele = etree.SubElement(atts, "att", name=k)
            ele.text = v

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
                        help="Regional ID subset (defaults to 'all')",
                        default='all',
                        nargs='?')
    args = parser.parse_args()

    main(args.output, args.region)
