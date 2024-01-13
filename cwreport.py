"""
AWS Disclaimer.

(c) 2020 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
This AWS Content is provided subject to the terms of the AWS Customer
Agreement available at https://aws.amazon.com/agreement/ or other written
agreement between Customer and Amazon Web Services, Inc.

This Python Script fetches Amazon CloudWatch metrics for a given AWS service in a given
region and generates a CSV report for the metrics information

"""

import sys
import os
import logging
import argparse
from botocore.exceptions import ClientError

from services.aws_service import AWSService
from report_generator import ReportGenerator

# make sure we are running with python 3
if sys.version_info < (3, 0):
    print("Sorry, this script requires Python 3 to run")
    sys.exit(1)


# setup logging function
def setup_logging():
    """
    Logging Function.

    Creates a global log object and sets its level.
    """
    global log
    log = logging.getLogger()
    log_levels = {"INFO": 20, "WARNING": 30, "ERROR": 40}

    if "logging_level" in os.environ:
        log_level = os.environ["logging_level"].upper()
        if log_level in log_levels:
            log.setLevel(log_levels[log_level])
        else:
            log.setLevel(log_levels["ERROR"])
            log.error(
                "The logging_level environment variable is not set to INFO, WARNING, or \
                    ERROR.  The log level is set to ERROR"
            )
    else:
        log.setLevel(log_levels["ERROR"])
        log.warning(
            "The logging_level environment variable is not set. The log level is set to \
                    ERROR"
        )
        log.info(
            "Logging setup complete - set to \
            log level "
            + str(log.getEffectiveLevel())
        )


setup_logging()

# Retrieve argument
parser = argparse.ArgumentParser()
parser.add_argument(
    "service",
    choices=[
        "lambda",
        "ec2",
        "rds",
        "alb",
        "nlb",
        "apigateway",
        "ec2_snapshots",
        "ec2_volumes",
        "rds_snapshots",
    ],
    help="The AWS Service to pull metrics for. Supported services are lambda, ec2, rds, alb, nlb and apigateway",
)
parser.add_argument(
    "-r",
    "--region",
    action="append",
    help="The AWS Region to pull metrics from, the default is ap-southeast-1",
)
parser.add_argument(
    "-p",
    "--profile",
    help="The credential profile to use if not using default credentials",
)

args = parser.parse_args()


# Retrieve script arguments
service_name = args.service
regions = args.region if args.region else None
profile = args.profile


aws_service: AWSService = AWSService(service_name, profile, regions)
report_generator: ReportGenerator = ReportGenerator(aws_service)
try:
    report_generator.generate_report()
except ClientError as error:
    logging.error("Your credentials is expired or unauthorized to access the resource")
    logging.error(error, exc_info=error)
    exit(1)
except Exception as error:
    logging.error(error, exc_info=error)
    exit(2)
