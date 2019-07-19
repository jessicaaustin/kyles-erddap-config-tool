#! /usr/bin/env python
import argparse
import os
import sys
from datetime import datetime, timedelta

import requests
import yaml
from lxml import etree

MASTER_ERDDAP_BASE_URL = 'http://erddap.sensors.axds.co'


def make_from_service(station, region):
    station_version = int(station['version'])

    dataset_type = 'EDDTableFromAxiomStationV2'
    if station_version == 1:
        # this dataset type pulls metadata from sensors.axds.co/api, and data from sensors.axds.co/stationsensorservice
        dataset_type = 'EDDTableFromAxiomStationV1'

    dataset = etree.Element("dataset", type=dataset_type, datasetID=str(station['datasetId']))

    st = etree.SubElement(dataset, "stationId")
    st.text = str(station['id'])

    source = etree.SubElement(dataset, "sourceUrl")
    source.text = 'https://sensors.axds.co/api/'
    if station_version == 1:
        v1_data_source = etree.SubElement(dataset, "v1DataSourceUrl")
        v1_data_source.text = 'http://sensors.axds.co/stationsensorservice/'

    # once a week, full reload no matter what
    # erddap-dataset-updater should handle intermediate reloads as data comes in
    rl = etree.SubElement(dataset, "reloadEveryNMinutes")
    rl.text = '10080'
    if station_version == 1:
        # v1 stations don't have a refresh system, so just manually reload throughout the day
        try:
            most_recent_data = station['feedStats']['endDate']
            end_date = datetime.strptime(most_recent_data, "%Y-%m-%dT%H:%M:%SZ")
            if end_date > (datetime.now() - timedelta(days=30)):
                # this station has realtime data, so load more frequently
                rl.text = '360'
        except Exception:
            pass

    return dataset


def link_to_master_erddap(station):
    dataset_type = 'EDDTableFromErddap'
    dataset_id = str(station['datasetId'])

    dataset = etree.Element("dataset", type=dataset_type, datasetID=dataset_id)

    dataset.append(etree.Comment(f"station_id={str(station['id'])}"))

    source = etree.SubElement(dataset, "sourceUrl")
    source.text = f'{MASTER_ERDDAP_BASE_URL}/erddap/tabledap/{dataset_id}'

    rl = etree.SubElement(dataset, "reloadEveryNMinutes")
    rl.text = '120'

    su = etree.SubElement(dataset, "subscribeToRemoteErddapDataset")
    su.text = 'false'

    rd = etree.SubElement(dataset, "redirect")
    rd.text = 'false'

    return dataset


def add_attribute_overrides(dataset, station, region):
    station_id = station['id']

    station_override_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                         'sensor_station_overrides',
                                         f'{station_id}.yml')

    region_override_file = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                        'sensor_region_overrides',
                                        f'{region}.yml')

    if not os.path.isfile(station_override_file) and not os.path.isfile(region_override_file):
        return

    atts = etree.SubElement(dataset, "addAttributes")

    def add_atts(settings):
        if 'global_attributes' in settings:
            global_atts = settings['global_attributes']
            for k, v in global_atts.items():
                ele = etree.SubElement(atts, "att", name=k)
                ele.text = v

    if os.path.isfile(region_override_file):
        # print(f'Loading {region_override_file}')
        with open(region_override_file, 'r') as ymlfile:
            region_settings = yaml.load(ymlfile, Loader=yaml.BaseLoader)
            add_atts(region_settings)
            # Info url override per region
            try:
                info_url_template = region_settings['settings']['info_url_template']
                info_url = info_url_template.replace('STATION_ID_PLACEHOLDER', str(station_id))
                info_url_elem = etree.SubElement(atts, "att", name="info_url")
                info_url_elem.text = info_url
                infoUrl_elem = etree.SubElement(atts, "att", name="infoUrl")
                infoUrl_elem.text = info_url
            except KeyError:
                pass

    if os.path.isfile(station_override_file):
        print(f'Loading {station_override_file}')

        with open(station_override_file, 'r') as ymlfile:
            station_settings = yaml.load(ymlfile, Loader=yaml.BaseLoader)

        # Attributes
        add_atts(station_settings)

        # Title
        try:
            title = station_settings['global_attributes']['title']
        except KeyError:
            title = station['label']
        try:
            if station_settings['region_settings'][region]['highlight_in_erddap']:
                title = '* ' + title
                title_elem = etree.SubElement(atts, "att", name="title")
                title_elem.text = title
        except KeyError:
            pass

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
    if 'usgs-cmg' == region:
        # TODO need to verify this
        return '853bc4c4-b61e-11e4-a180-00265529168c'

    raise ValueError(f'Region {region} not configured!')


def main(outfile, region, link):
    filter_uuid = determine_filter_uuid(region)
    print(f'Region: {region}, filter uuid: {filter_uuid}')
    r = requests.get(f'https://sensors.axds.co/api/metadata/filter/{filter_uuid}?includeStationVersions=merged',
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

        if link is True:
            dataset = link_to_master_erddap(station)
        else:
            dataset = make_from_service(station, region)

        add_attribute_overrides(dataset, station, region)
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
                        help="Content region name (defaults to 'global')",
                        default='global',
                        nargs='?')
    parser.add_argument('-l', '--link',
                        help='Should the datasets be created as links to the master (global) ERDDAP server',
                        action='store_true',
                        default=False)
    args = parser.parse_args()

    sys.exit(main(args.output, args.region, args.link))
