# vtc-backup.py
#
# Copies latest VTC backup file from AWS EC2 instance to S3 storage.
#
# Usage: python vtc-backup.py
#
# Revision History
# -------------------------------------------------------------------
# 1.0 2019-02-12 FS Original version
# 2.0 2019-05-17 FS Update code structure
# 3.0 2019-12-19 FS Change to multipart upload

import boto3
from datetime import date
import glob
import io, os, sys

UPLOAD_PART_SIZE = 5 * 1024 * 1024

def copy_backup_to_s3(f):

    # Do a multipart upload.
    try:
        
        client = boto3.client('s3')
        
        # First step is to initiate the multipart upload. Note that the storage
        # class must be ONEZONE_IA.
        create_response = client.create_multipart_upload(
            Bucket='cubl-vtc',
            Key=os.path.basename(f),
            StorageClass='ONEZONE_IA')

        # Second step is to upload the individual parts of the file. Parts are
        # arbitrarily sized at 5MB -- if the size of the file is less than an
        # even multiple of 5MB, the last part will be < 5MB.
        #
        # Note that for each part upload, the part number and corresponding ETag
        # must be saved for the last step of the multipart upload process.
        file_size = os.lstat(f).st_size
        file_position = file_size
        part_number = 1
        parts = []

        fio = io.FileIO(f)
        while file_position > 0:
            part = fio.read(UPLOAD_PART_SIZE)
            upload_response = client.upload_part(
                Body=part,
                Bucket='cubl-vtc',
                Key=os.path.basename(f),
                PartNumber=part_number,
                UploadId=create_response['UploadId'])
            parts.append({'ETag': upload_response['ETag'], 'PartNumber': part_number})
            part_number += 1
            file_position -= UPLOAD_PART_SIZE
        fio.close()

        # Finally, complete the multipart upload
        client.complete_multipart_upload(
            Bucket='cubl-vtc',
            Key=os.path.basename(f),
            MultipartUpload={'Parts': parts},
            UploadId=create_response['UploadId'])
            
    except:
        
        # If any problems are encountered along the way, publish an alert
        sns = boto3.client('sns')
        sns.publish(TopicArn='arn:aws:sns:us-west-2:735677975035:VTCBackupStatus',
            Message='Error: Unable to copy backup file to S3',
            Subject='VTC Notification - Backup Status')
        
if __name__ == "__main__":
    
    # Get the latest backup file from the backup directory. The latest backup
    # is the one with a create date-time stamp of today.
    backup_dir = sys.argv[1]
    flist = glob.glob('{}/*.vtcbackup'.format(os.path.normcase(backup_dir)))
    for f in flist:
        stat_info = os.stat(f)
        if date.fromtimestamp(stat_info.st_ctime) == date.today():
            break
    
    copy_backup_to_s3(f)

# EOF