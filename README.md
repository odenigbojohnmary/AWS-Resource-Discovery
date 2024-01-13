This is an enhanced version for the script described in this [Doc](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/publish-amazon-cloudwatch-metrics-to-a-csv-file.html) with multiple region support and generating report for all available regions. 

I have also updated the script to include additional information like `region`, `tags`, `Approximate Costs`, and `Max values` for stats of EC2 Instances. 

### Pre-requisites Installation

1. Install latest version of python

1. Install packages: 
    1. Extract the attached zip file
    2. Open a terminal in project root directory
    2. Create a virtual environment in project directory and activate it. [Documentation](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)
    1. Run following command to install packages  
    ```pip3 install -r requirements.txt```

2. Configure the AWS CLI: ```aws configure```
3. Or we can use Profile declared in `~/.aws/credentials`

### Script Configuration:

Script configuration can be found in metrics.yaml.

1. period - This is the period of the metrics to fetch. The default period is 5 minutes (300 seconds). This can be modified but note the below API limitations when modifying this value

    - If hours specified below is between 3 hours and 15 days ago - Use a multiple of 60 seconds for the period (1 minute) else no datapoint will be returned by the API.
    - If hours specified below is between 15 and 63 days ago - Use a multiple of 300 seconds (5 minutes) else no datapoint will be returned by the API.
    - If hours specified below is greater than 63 days ago - Use a multiple of 3600 seconds (1 hour) else no datapoint will be returned by the API

2. hours - This is the amount of hours prior worth of metrics you want to fetch. The default is 1hour, you can modify this to signify days but it must be specified in hours. For example 48 signifies 2 days

3. statistics - This is the global statistics that will be used when fetching metrics that do not have specific statistics assigned. For any metric that has statistics configured, this configuration will not be used.

### Script Usage
1. Open terminal the project root directory
3. Activate the virtual environment [Documentation](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)
2. Run `Python cwreport.py <service> -p <profile>`

Example syntax: `python cwreport.py <service> <--region=Optional Region> <--profile=<Optional credential profile>`

Parameters:
1. service (required) - This is the service you want to run the script against. The services currently supported are AWS Lambda, Amazon EC2, Amazon RDS, Application Load Balancer, Network Load Balancer and Amazon API Gateway, EC2 Snapshots, EC2 Volumes, RDS Snapshots. Here are the available options list for services
    1. lambda
    1. ec2
    1. rds
    1. alb
    1. nlb
    1. apigateway
    1. ec2_snapshots
    1. ec2_volumes
    1. rds_snapshots

2. region (optional) - This is the region to fetch metrics from. By default the report will be generated for all available region
3. profile (optional) - This is the AWS CLI named profile to use. If specified, the default configured credential is not used

Examples:
1) Using default configured credentials to fetch Amazon EC2 metrics for all regions: `python cwreport.py ec2`
1) With Region Specified and fetching Amazon API Gateway metrics: `python cwreport.py apigateway --region us-east-1`
1) With multiple region Specified and fetching ec2 metrics: `python cwreport.py apigateway --region us-east-1 --region us-west-1`
3) With AWS profile specified: `python cwreport.py ec2 --profile testprofile`
4) With both region and profile specified: `python cwreport.py ec2 --region us-east-1 --profile testprofile`

### Known Issues
1) Currently we are showing hard coded value for the approximate costs. We will integrate boto3 cost explorer to get more accurate cost in future
2) If older version of python is installed in your environment as well as latest version, try to replace `python` with `python3` in all the commands 
3) The script is still significantly slow as boto3 APIs doesn’t support asyncio. Any suggestion is appreciated. You can additionally update the `metrics.yaml` and remove metrics that you don't need to make the scripts faster.
