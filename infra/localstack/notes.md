docker-compose up -d
sudo apt install awscli
aws configure


AWS Access Key ID [None]: test
AWS Secret Access Key [None]: test
Default region name [None]: us-east-1
Default output format [None]: json


aws --endpoint-url=http://localhost:4566 s3 mb s3://my-local-bucket

Create Bucket
--------------
aws --endpoint-url=http://localhost:4566 s3 mb s3://mybucket
