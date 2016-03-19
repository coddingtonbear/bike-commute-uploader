from __future__ import print_function

import os
import subprocess
import sys
from xml.etree import ElementTree

from dateutil.parser import parse
import pytz


def get_media_info(path):
    output = subprocess.check_output(
        [
            '/usr/bin/mediainfo',
            '--Output=XML',
            path,
        ]
    )

    return ElementTree.fromstring(output)


def upload_video(path, title, recording_date, secrets, credentials):
    subprocess.check_call(
        [
            '/usr/local/bin/youtube-upload',
            '--title', title,
            '--tags', 'commute, autoupload',
            '--recording-date', (
                recording_date.astimezone(pytz.UTC).strftime(
                    '%Y-%m-%dT%H:%M:%S.0Z'
                )
            ),
            '--privacy', 'unlisted',
            '--client-secrets', secrets,
            '--credentials', credentials,
            path,
        ]
    )


def main():
    path = sys.argv[1]
    secrets = sys.argv[2]
    credentials = sys.argv[3]

    files = os.listdir(path)

    gopro_tz = pytz.timezone('Japan')
    local_tz = pytz.timezone('America/Los_Angeles')

    for filename in files:
        full_path = os.path.join(path, filename)
        basename, ext = os.path.splitext(filename)
        if ext != '.MP4':
            continue

        try:
            info = get_media_info(full_path)

            date_string = info.find(
                ".//File/track[@type='General']/Encoded_date"
            ).text
            encoded_date = parse(
                date_string[date_string.find(' ')+1:]
            )
            encoded_date = encoded_date.replace(tzinfo=gopro_tz)

            upload_video(
                full_path,
                "{date} Bike Commute (auto-uploaded)".format(
                    date=encoded_date.astimezone(local_tz).strftime(
                        '%A, %d %B %Y, %I:%M %p',
                    )
                ),
                encoded_date,
                secrets,
                credentials,
            )
        except Exception as e:
            print("Error encountered: " + e)

        print("OK")
