#!/usr/bin/bash
# script to run as a cronjob the host machine, needs to aws cli installed
# and an user with access to a s3 bucket

source /home/ubuntu/.profile
database_name=rdv2
database_user=postgres
database_password=example
database_port=5432

backup_path=/home/ubuntu/setup/database-backups
bash_profile=/home/ubuntu/.profile

bucket_name=my-bucket
aws_access_key_id=
aws_secret_access_key=

file_name=dump_$(date +``%Y-%m-%d_%H_%M_%S'').sql.gz
#PGPASSWORD=$database_password pg_dump -h 127.0.0.1 -p $database_port -U $database_user -d $database_name | gzip > $backup_path/$file_name
#AWS_ACCESS_KEY_ID=$aws_access_key_id AWS_SECRET_ACCESS_KEY=$aws_secret_access_key aws s3 cp $backup_path/$file_name s3://$bucket_name
#rm $backup_path/$file_name
