#! /usr/bin/env python
import argparse

import requests
from lxml import etree
from slugify import UniqueSlugify

ioos_template = """
<dataset type="EDDTableFromNcCFFiles" datasetID="{slug}">
    <reloadEveryNMinutes>60</reloadEveryNMinutes>
    <fileDir>{folder}</fileDir>
    <fileNameRegex>{file}</fileNameRegex>
    <addAttributes>
        <att name="title">{title}</att>
    </addAttributes>
    <dataVariable><sourceName>trajectory</sourceName><destinationName>trajectory</destinationName><dataType>String</dataType></dataVariable>
    <dataVariable><sourceName>wmo_id</sourceName><destinationName>wmo_id</destinationName><dataType>String</dataType></dataVariable>
    <dataVariable><sourceName>time</sourceName><destinationName>time</destinationName><dataType>double</dataType></dataVariable>
    <dataVariable><sourceName>latitude</sourceName><destinationName>latitude</destinationName><dataType>double</dataType></dataVariable>
    <dataVariable><sourceName>longitude</sourceName><destinationName>longitude</destinationName><dataType>double</dataType></dataVariable>
    <dataVariable><sourceName>profile_id</sourceName><destinationName>profile_id</destinationName><dataType>short</dataType></dataVariable>
    <dataVariable><sourceName>time_uv</sourceName><destinationName>time_uv</destinationName><dataType>double</dataType></dataVariable>
    <dataVariable><sourceName>lat_uv</sourceName><destinationName>lat_uv</destinationName><dataType>double</dataType></dataVariable>
    <dataVariable><sourceName>lon_uv</sourceName><destinationName>lon_uv</destinationName><dataType>double</dataType></dataVariable>
    <dataVariable><sourceName>u</sourceName><destinationName>u</destinationName><dataType>double</dataType></dataVariable>
    <dataVariable><sourceName>v</sourceName><destinationName>v</destinationName><dataType>double</dataType></dataVariable>
    <dataVariable><sourceName>latitude_qc</sourceName><destinationName>latitude_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>longitude_qc</sourceName><destinationName>longitude_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>time_qc</sourceName><destinationName>time_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>depth</sourceName><destinationName>depth</destinationName><dataType>float</dataType></dataVariable>
    <dataVariable><sourceName>depth_qc</sourceName><destinationName>depth_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>pressure</sourceName><destinationName>pressure</destinationName><dataType>double</dataType></dataVariable>
    <dataVariable><sourceName>pressure_qc</sourceName><destinationName>pressure_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>conductivity</sourceName><destinationName>conductivity</destinationName><dataType>float</dataType></dataVariable>
    <dataVariable><sourceName>conductivity_qc</sourceName><destinationName>conductivity_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>density</sourceName><destinationName>density</destinationName><dataType>float</dataType></dataVariable>
    <dataVariable><sourceName>density_qc</sourceName><destinationName>density_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>precise_lat</sourceName><destinationName>precise_lat</destinationName><dataType>double</dataType></dataVariable>
    <dataVariable><sourceName>precise_lon</sourceName><destinationName>precise_lon</destinationName><dataType>double</dataType></dataVariable>
    <dataVariable><sourceName>precise_time</sourceName><destinationName>precise_time</destinationName><dataType>double</dataType></dataVariable>
    <dataVariable><sourceName>precise_lat_qc</sourceName><destinationName>precise_lat_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>precise_lon_qc</sourceName><destinationName>precise_lon_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>precise_time_qc</sourceName><destinationName>precise_time_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>salinity</sourceName><destinationName>salinity</destinationName><dataType>float</dataType></dataVariable>
    <dataVariable><sourceName>salinity_qc</sourceName><destinationName>salinity_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>temperature</sourceName><destinationName>temperature</destinationName><dataType>float</dataType></dataVariable>
    <dataVariable><sourceName>temperature_qc</sourceName><destinationName>temperature_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>time_uv_qc</sourceName><destinationName>time_uv_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>lat_uv_qc</sourceName><destinationName>lat_uv_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>lon_uv_qc</sourceName><destinationName>lon_uv_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>u_qc</sourceName><destinationName>u_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>v_qc</sourceName><destinationName>v_qc</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>platform_meta</sourceName><destinationName>platform_meta</destinationName><dataType>byte</dataType></dataVariable>
    <dataVariable><sourceName>instrument_ctd</sourceName><destinationName>instrument_ctd</destinationName><dataType>byte</dataType></dataVariable>
</dataset>
"""


def main(ztype, outfile, names, highlight_title):

    url = 'http://platforms.axds.co/platforms/byclass/ioosgliderdac/'
    lst = requests.get(url).json()

    datafile = '{name}.enhanced.nc'
    datafolder = '/mnt/gluster/data/platforms/prod/IoosGliderDac/{uuid}/download/'
    slug = UniqueSlugify(separator='_', to_lower=True)

    datasets = []
    for n in sorted(names):

        try:
            gd = next(x for x in lst if x['slug'].lower() == n.lower())
            assert 'Enhanced NetCDF' in [ y['name'] for y in gd['datafiles'] ]
        except StopIteration:
            print('No glider {} found!'.format(n))
            continue
        except AssertionError:
            print('No enhanced.nc file for {} found!'.format(n))
            continue

        xml = ioos_template.format(
            slug=slug(n),
            file=datafile.format(name=n),
            folder=datafolder.format(uuid=gd['id']),
            title='{} - {}'.format(highlight_title, n)
        )
        datasets.append(etree.fromstring(xml))

    with open(outfile, 'wt') as f:
        for d in datasets:
            try:
                f.write(etree.tostring(d, encoding='ISO-8859-1', pretty_print=True, xml_declaration=False).decode('iso-8859-1'))
                f.write('\n')
            except UnicodeDecodeError:
                print("ERROR WITH: {}\n\n".format(etree.tostring(d)))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument('type',
                        help="Type of glider",
                        choices=['ioos'],
                        nargs='?')
    parser.add_argument('-o', '--output',
                        help="File to output XML to",
                        default='output.xml',
                        nargs='?')
    parser.add_argument('-n', '--names',
                        help="Construct XML from these gliders",
                        default=[],
                        nargs='*')
    parser.add_argument('-t', '--highlight_title',
                        help="Use this for the highlight title",
                        default='*',
                        nargs='?')
    args = parser.parse_args()

    main(args.type, args.output, args.names, args.highlight_title)
