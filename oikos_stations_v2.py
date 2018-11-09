#! /usr/bin/env python
import sys
import argparse

import requests
from lxml import etree


def make_from_service(station_id):
    dataset_type = 'EDDTableFromAxiomStation'

    dataset = etree.Element("dataset", type=dataset_type, datasetID=f'station-{station_id}')

    st = etree.SubElement(dataset, "stationId")
    st.text = station_id

    source = etree.SubElement(dataset, "sourceUrl")
    source.text = 'https://sensors.axds.co/api/'

    # dataset is backed by a file, so don't need reloadEveryNMinutes

    return dataset


def main(outfile, filter_uuid):

    # TODO: for now, we return only v2 stations
    # Once things are tested and working well, this service can return both v1 and v2 stations and we can get rid
    # of the old oikos_stations.py
    r = requests.get(f'https://sensors.axds.co/api/metadata/filter/{filter_uuid}?includeStationVersions=v2', timeout=300)
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
    for s in stations:

        station_id = str(s['id'])
        dataset = make_from_service(station_id)
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
    parser.add_argument('-f', '--filter',
                        help="Filter UUID (defaults to EVERYTHING (00000000-0000-0000-0000-000000000000))",
                        default='00000000-0000-0000-0000-000000000000',
                        nargs='?')
    args = parser.parse_args()

    sys.exit(main(args.output, args.filter))
