from __future__ import print_function

import argparse
import os
import subprocess
import time
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
    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs=1)
    parser.add_argument('secrets', nargs=1)
    parser.add_argument('credentials', nargs=1)
    parser.add_argument(
        '--limit',
        default=0,
        type=int,
        help='Process only this number of videos.'
    )
    parser.add_argument(
        '--delay',
        default=0,
        type=int,
        help='Delay this number of seconds between videos.'
    )

    args = parser.parse_args()

    path = args.path[0]
    secrets = args.secrets[0]
    credentials = args.credentials[0]

    files = os.listdir(path)

    local_tz = pytz.timezone('America/Los_Angeles')
    gopro_tz = local_tz

    count = 0
    for filename in files:
        if args.delay and count != 0:
            time.sleep(args.delay)

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
            print("Error encountered: " + str(e))

        os.unlink(full_path)
        print("OK")

        count += 1
        if args.limit and count >= args.limit:
            break
