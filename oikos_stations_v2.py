#! /usr/bin/env python
import argparse
import os
import sys

import requests
import yaml
from lxml import etree


def make_from_service(station, region):
    dataset_type = 'EDDTableFromAxiomStationV2'

    dataset = etree.Element("dataset", type=dataset_type, datasetID=str(station['uuid']))

    st = etree.SubElement(dataset, "stationId")
    st.text = str(station['id'])

    source = etree.SubElement(dataset, "sourceUrl")
    source.text = 'https://sensors.axds.co/api/'

    add_attribute_overrides(dataset, station, region)

    # once a week, full reload no matter what
    rl = etree.SubElement(dataset, "reloadEveryNMinutes")
    rl.text = '10080'

    return dataset


def add_attribute_overrides(dataset, station, region):
    station_id = station['id']
    title = station['label']

    override_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 'sensor_station_overrides',
                                 f'{station_id}.yml')

    if not os.path.isfile(override_file):
        return

    print(f'Loading {override_file}')

    with open(override_file, 'r') as ymlfile:
        settings = yaml.load(ymlfile, Loader=yaml.BaseLoader)

    # Attributes
    atts = etree.SubElement(dataset, "addAttributes")
    if 'global_attributes' in settings:
        global_atts = settings['global_attributes']
        for k, v in global_atts.items():
            if 'title' == k:
                title = v
            else:
                ele = etree.SubElement(atts, "att", name=k)
                ele.text = v

    # Title
    try:
        if settings['region_settings'][region]['highlight_in_erddap']:
            title = '* ' + title
    except KeyError:
        pass
    title_elem = etree.SubElement(atts, "att", name="title")
    title_elem.text = title

    return dataset


def determine_filter_uuid(region):
    if 'aoos' == region:
        return '66b2e570-59ae-11e1-b91b-0019b9dae22b'
    if 'cencoos' == region:
        return '8f65624e-6790-11e3-a1d4-00219bfe5678'
    if 'global' == region:
        return '00000000-0000-0000-0000-000000000000'
    if 'ioos' == region:
        return '00000000-0000-0000-0000-000000000000'
    if 'secoora' == region:
        return '1695aa00-c779-11e4-8447-00265529168c'
    if 'sensorsv2' == region:
        return '00000000-0000-0000-0000-000000000000'
    if 'usgs-cmg' == region:
        # TODO need to verify this
        return '853bc4c4-b61e-11e4-a180-00265529168c'

    raise ValueError(f'Region {region} not configured!')


def main(outfile, region):
    # TODO: for now, we return only v2 stations
    # Once things are tested and working well, this service can return both v1 and v2 stations and we can get rid
    # of the old oikos_stations.py
    filter_uuid = determine_filter_uuid(region)
    print(f'Region: {region}, filter uuid: {filter_uuid}')
    r = requests.get(f'https://sensors.axds.co/api/metadata/filter/{filter_uuid}?includeStationVersions=v2',
                     timeout=300)
    r.raise_for_status()

    try:
        r = r.json()
    except BaseException:
        print(f'No stations available for the filter with uuid {filter_uuid}')
        return 1

    datasets = []

    stations = r['data']['stations']
    stations = sorted(stations, key=lambda x: x['id'])

    print(f'Exporting {len(stations)} stations from filter {filter_uuid} to {outfile}')
    for station in stations:
        dataset = make_from_service(station, region)
        datasets.append(dataset)

    with open(outfile, 'wt') as f:
        for d in datasets:
            try:
                f.write(etree.tostring(d, encoding='ISO-8859-1', pretty_print=True, xml_declaration=False).decode(
                    'iso-8859-1'))
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
                        help="Regional ID subset (defaults to 'sensorsv2')",
                        default='sensorsv2',
                        nargs='?')
    args = parser.parse_args()

    sys.exit(main(args.output, args.region))
