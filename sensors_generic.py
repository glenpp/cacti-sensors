#!/usr/bin/env python3
# Copyright (C) 2021  Glen Pitt-Pladdy
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#
#
# See: https://www.pitt-pladdy.com/blog/_20091031-160232_0000_LM_Sensors_stats_on_Cacti_via_SNMP_/

import sys
import subprocess
import json
import re


# absolute path is safer
SENSORS = '/usr/bin/sensors'


def usage():
    print("Usage: {} <temps|voltages|fans> <index|labels|readings|min|max|crit>".format(sys.argv[0]))
    sys.exit(1)

def main():
    try:
        sensor_type = sys.argv[1]
        output_mode = sys.argv[2]
    except IndexError:
        usage()
    # run in json mode
    proc = subprocess.run(
        [SENSORS, '-j'],
        capture_output=True,
        check=True,
    )
    sensors = json.loads(proc.stdout)
    # pick out by 
    readings = {}
    for chip, chip_sensors in sensors.items():
        adapter = chip_sensors.get('Adapter')
        del chip_sensors['Adapter']
        for label, data in chip_sensors.items():
            if sensor_type == 'temps':
                prefix_pattern = r'^temp(\d+)_'
            elif sensor_type == 'voltages':
                prefix_pattern = r'^in(\d+)_'
            elif sensor_type == 'fans':
                prefix_pattern = r'^fan(\d+)_'
            else:
                raise ValueError("BUG! Unhanled sensor type: {}".format(sensor_type))
            index = None
            prefix = None
            for metric, value in data.items():
                match = re.fullmatch(prefix_pattern + 'input$', metric)
                if not match:
                    continue
                # matching item - generate index
                index = '{}.{}.{:02d}'.format(chip, sensor_type, int(match.group(1)))
                prefix = metric.rsplit('_', 1)[0]
                break
            if not index:
                continue
            # 
            readings[index] = {
                'chip': chip,
                'adapter': adapter,
                'label': label,
                'metrics': {
                    'value': data.get(prefix + '_input', 'U'),
                    'min': data.get(prefix + '_min', 'U'),
                    'max': data.get(prefix + '_max', 'U'),
                    'crit': data.get(prefix + '_crit', 'U'),
                },
            }
    # output
    for index in sorted(readings):
        if output_mode == 'index':
            print(index)
        elif output_mode == 'labels':
            print(readings[index]['label'])
        elif output_mode in readings[index]['metrics']:
                print(readings[index]['metrics'][output_mode])
        else:
            raise ValueError("BUG! Unhanled mode: {}".format(sensor_mode))


if __name__ == '__main__':
    main()
