import logging
from botocore.exceptions import ClientError

from services.region_service import RegionService
from services.cloud_watch_service import CloudWatchClient
from services.service_util.boto3_session import Boto3Session


class AWSService:
    def __init__(self, service_name, profile_name=None, regions=[]):
        self.service_name = service_name
        self.profile_name = profile_name
        self._regions = regions
        self.boto3_session = Boto3Session(self.profile_name)

        if not self._regions:
            self._set_regions()

    def create_service_client(self, region):
        session = self.boto3_session.get_for_region(region)
        service_name = self.service_name.split("_")[0]
        if self.service_name == "ec2":
            return session.resource(service_name)
        else:
            return session.client(service_name)

    def create_cloud_watch_client(self, region):
        session = self.boto3_session.get_for_region(region)
        return CloudWatchClient(session, self.service_name)

    def get_all_resources(self, service_client):
        if self.service_name == "ec2":
            # return service_client.instances.filter(
            #     Filters=[
            #         {'Name': 'instance-state-name', 'Values': ['running']}])
            return service_client.instances.all()
        elif self.service_name == "rds":
            result = service_client.describe_db_instances()
            return result["DBInstances"]
        elif self.service_name == "lambda":
            result = service_client.list_functions()
            return result["Functions"]
        elif self.service_name == "alb":
            alb_list = []
            result = service_client.describe_load_balancers()
            for lb in result["LoadBalancers"]:
                if lb["Type"] == "application":
                    alb_list.append(lb)
            return alb_list
        elif self.service_name == "nlb":
            nlb_list = []
            result = service_client.describe_load_balancers()
            for lb in result["LoadBalancers"]:
                if lb["Type"] == "network":
                    nlb_list.append(lb)
            return nlb_list
        elif self.service_name == "apigateway":
            result = service_client.get_rest_apis()
            return result["items"]
        elif self.service_name == "ec2_snapshots":
            return service_client.describe_snapshots(OwnerIds=["self"])["Snapshots"]
        elif self.service_name == "ec2_volumes":
            response = service_client.describe_volumes()
            return response.get("Volumes", [])
        elif self.service_name == "rds_snapshots":
            snapshots = []
            marker = None
            while True:
                if marker:
                    response = service_client.describe_db_snapshots(Marker=marker)
                else:
                    response = service_client.describe_db_snapshots()
                snapshots.extend(response.get("DBSnapshots", []) or [])

                if "Marker" in response:
                    marker = response["Marker"]
                else:
                    break

            return snapshots
        

    def get_service_name(self):
        return self.service_name

    def get_all_regions(self):
        return self._regions

    def get_profile_name(self):
        return self.profile_name

    def get_resource_id(self, resource):
        resource_id = None
        if self.service_name == "ec2":
            resource_id = resource.id
        elif self.service_name == "ec2_snapshots":
            return resource["SnapshotId"]
        elif self.service_name == "ec2_volumes":
            return resource["VolumeId"]
        elif self.service_name == "rds":
            resource_id = resource["DBInstanceIdentifier"]
        elif self.service_name == "rds_snapshots":
            resource_id = resource["DBSnapshotIdentifier"]
        elif self.service_name == "lambda":
            resource_id = resource["FunctionName"]
        elif self.service_name == "alb":
            lb_arn_split = resource["LoadBalancerArn"].split("loadbalancer/")
            resource_id = lb_arn_split[1]
        elif self.service_name == "nlb":
            lb_arn_split = resource["LoadBalancerArn"].split("loadbalancer/")
            resource_id = lb_arn_split[1]
        elif self.service_name == "apigateway":
            resource_id = resource["name"]

        return resource_id

    def _set_regions(self):
        try:
            self._regions = RegionService(
                "us-west-2", self.profile_name
            ).get_all_by_service()
        except ClientError as e:
            logging.error("Credential expired of unauthorized to access resource")
            logging.error(e)
            exit(1)
        except Exception as e:
            logging.error(e, exc_info=e)
            exit(2)
