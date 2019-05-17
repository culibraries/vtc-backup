# vtc-backup.py
#
# Copies latest VTC backup file from AWS EC2 instance to S3 storage.
#
# Usage: python vtc-backup.py
#
# Revision History
# -------------------------------------------------------------------
# 1.0 2019-02-12 FS Original version
# 2.0 2019-05-17 FS Updated code structure

import boto3
from datetime import date
import glob
import os

VTC_BACKUP = 'C:\\Users\\Public\\Documents\\TimeClock Data\\Backup\\'

def copy_backup_to_s3(f):

    # Using aws boto library, instantiate a bucket object and stream
    # VTC backup file to the bucket
    #
    # If an I/O error is encountered, invoke sns message which will
    # be routed to libnotify@colorado.edu
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('cubl-vtc')
    try:
        with open(f, 'rb') as data:
            bucket.upload_fileobj(data, os.path.basename(f))
    except IOError:
        sns = boto3.client('sns')
        sns.publish(TopicArn='arn:aws:sns:us-west-2:735677975035:VTCBackupStatus',
            Message='IOError: Unable to copy backup file to S3.',
            Subject='VTC Notification - Backup Status')

if __name__ == "__main__":

    # Get the latest backup file from the backup directory
    # The latest backup is the one with today's date-time stamp
    flist = glob.glob(VTC_BACKUP + '*.vtcBackup')
    if len(flist) <> 0:

        # Find the backup file with today's date
        for f in flist:
            fstat = os.stat(f)
            if date.fromtimestamp(fstat.st_ctime) == date.today():
                break
    
        copy_backup_to_s3(f)

# EOF