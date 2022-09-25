# Application to Access S3 with boto3

## create access and secret token
run command "aws configure" and provide below details
1. AWS Access Key ID [None]: accesskey
2. AWS Secret Access Key [None]: secretkey
3. Default region name [None]: us-west-2
4. Default output format [None]:

## Steps to create Virtual Environment
1. python3 -m venv <path>
2.	source venv/bin/activate
3.	python -m pip install <package-name>
4.	deactivate

## Steps to run application on ubuntu
1. Run init.sh to install required packages
2. Provide your bucket name in configuration.toml file
3. Run run.sh -p to start the application
