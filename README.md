# VTC Backup
Python script to copy VTC backup files generated on the server to an S3 bucket (cubl-vtc). The VTC server manager generates a backup of the database at the end of each day. Only the last three backup files are retained on the server. The script copies the latest backup file to an S3 bucket. Backup files are retained for 30 days.

### Installation
The Python file is located at C:\Users\Public\Documents\Scripts on the VTC server.

### Usage
The script is executed daily at 2:15 AM using a Windows Scheduler task.

### Credits
The script was written by Fred Schumacher (@fwschumacher).
