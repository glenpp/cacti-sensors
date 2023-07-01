#!/usr/bin/env python3
"""
Copyright (C) 2021-2023  Glen Pitt-Pladdy

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.



See: https://github.com/glenpp/cacti-sensors

Version: 20230701
"""

import sys
import subprocess
import json
import re


# absolute path is safer
SENSORS_COMMAND = [
    '/usr/bin/sensors',
    '-j',
]


def usage():
    print(f"Usage: {sys.argv[0]} <temps|voltages|fans> <index|labels|value|min|max|crit>", file=sys.stderr)
    sys.exit(1)


def main():
    try:
        sensor_type = sys.argv[1]
        output_mode = sys.argv[2]
    except IndexError:
        usage()
    # capture sensors data
    proc = subprocess.run(
        SENSORS_COMMAND,
        capture_output=True,
        check=True,
    )
    sensors = json.loads(proc.stdout)
    # pick out by sensor
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
                raise ValueError(f"BUG! Unhanled sensor type: {sensor_type}")
            index = None
            prefix = None
            for metric in data.keys():
                match = re.fullmatch(prefix_pattern + 'input$', metric)
                if not match:
                    continue
                # matching item - generate index
                index = f'{chip}.{sensor_type}.{int(match.group(1)):02d}'
                prefix = metric.rsplit('_', 1)[0]
                break
            if not index:
                continue
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
            raise ValueError(f"BUG! Unhanled mode: {output_mode}")


if __name__ == '__main__':
    main()
