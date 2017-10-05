#! /usr/bin/env python
import sys
import argparse

import requests
from lxml import etree
from assetid.urn import IoosUrn
from slugify import UniqueSlugify


def make_from_service(dataset_id):
    dataset_type = 'EDDTableFromAxiomStation'

    dataset = etree.Element("dataset", type=dataset_type, datasetID=dataset_id)

    st = etree.SubElement(dataset, "stationId")
    st.text = dataset_id

    source = etree.SubElement(dataset, "sourceUrl")
    source.text = 'http://sensors.axds.co/stationsensorservice/'

    rl = etree.SubElement(dataset, "reloadEveryNMinutes")
    rl.text = '360'

    return dataset


def make_from_erddap(dataset_id, remote_dataset_id):
    dataset_type = 'EDDTableFromErddap'
    dataset = etree.Element("dataset", type=dataset_type, datasetID=dataset_id)

    source = etree.SubElement(dataset, "sourceUrl")
    source.text = 'http://erddap.axds.co/erddap/tabledap/{}'.format(remote_dataset_id)

    rl = etree.SubElement(dataset, "reloadEveryNMinutes")
    rl.text = '60'

    su = etree.SubElement(dataset, "subscribeToRemoteErddapDataset")
    su.text = 'false'

    rd = etree.SubElement(dataset, "redirect")
    rd.text = 'false'

    return dataset


def add_global_attributes(dataset, station, global_atts):
    # Attributes
    atts = etree.SubElement(dataset, "addAttributes")

    # Title
    label = global_atts.get('title', station.get('label'))
    label = label.replace('(', '').replace(')', '')
    if station.get('highlight_in_erddap') is True:
        label = '* ' + label
    title = etree.SubElement(atts, "att", name="title")
    title.text = label

    # Institution
    owner = global_atts.get('institution', station.get('owner_label'))
    owner = owner.replace('(', '').replace(')', '')
    own = etree.SubElement(atts, "att", name="institution")
    own.text = owner

    # All other attributes
    for k, v in global_atts.items():
        ele = etree.SubElement(atts, "att", name=k)
        ele.text = v

    return dataset


def main(outfile, region_id, link):

    params = {}
    # Either a name or integer
    if region_id == 'global':
        params['global_region'] = 'true'
    else:
        try:
            params['region_id'] = int(region_id)
        except ValueError:
            params['region_name'] = region_id

    r = requests.get('http://sensors.axds.co/stationsensorservice/getRegionMetadata', params=params, timeout=300)
    r.raise_for_status()

    try:
        r = r.json()
    except BaseException:
        print("No stations available for the '{}' region".format(region_id))
        return 1

    slug = UniqueSlugify(separator='_', to_lower=True)

    datasets = []

    stats = r[0].get("stations")
    stats = [ x for x in stats if x.get('add_to_erddap') is True ]
    stats = sorted(stats, key=lambda x: x['id'])

    print("Exporting {} stations (linked: {}) from region '{}' to {}".format(
        len(stats), link, region_id, outfile)
    )
    for s in stats:

        remote_dataset_id = str(s['id'])
        gas = s.get('global_attributes', {})

        if link is False:
            dataset = make_from_service(remote_dataset_id)
        else:
            # Compute the Station URN
            # Precedence:
            #  1.) 'urn' global_attribute
            #  2.) 'id'  and 'naming_authority' global_attributes
            #  3.) Station URN from sensor service
            if 'urn' in gas:
                iurn = IoosUrn.from_string(gas['urn'].lower())
                gas['id'] = iurn.label
                gas['naming_authority'] = iurn.authority
            if 'naming_authority' in gas and 'id' in gas:
                station_urn = '{}.{}'.format(gas['naming_authority'], gas['id']).lower()
            else:
                station_urn = s['urn'].lower()

            station_urn = station_urn.replace('urn:ioos:station:', '')
            dataset_id = slug(station_urn)
            dataset = make_from_erddap(dataset_id, remote_dataset_id)

        dataset = add_global_attributes(dataset, s, gas)
        datasets.append(dataset)

    with open(outfile, 'wt') as f:
        for d in datasets:
            try:
                f.write(etree.tostring(d, encoding='ISO-8859-1', pretty_print=True, xml_declaration=False).decode('iso-8859-1'))
                f.write('\n')
            except UnicodeDecodeError:
                print("ERROR WITH: {}\n\n".format(etree.tostring(d)))
                return 1

    return 0


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('-o', '--output',
                        help="File to output XML to",
                        default='output.xml',
                        nargs='?')
    parser.add_argument('-r', '--region',
                        help="Regional ID subset (defaults to 'global')",
                        default='global',
                        nargs='?')
    parser.add_argument('-l', '--link',
                        help='Should the datasets be created as links to the master ERDDAP server',
                        action='store_true',
                        default=False)
    args = parser.parse_args()

    sys.exit(main(args.output, args.region, args.link))
