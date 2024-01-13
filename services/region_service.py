from services.service_util.boto3_session import Boto3Session

class RegionService:
    def __init__(self, region_name, profile_name=None):
        self.session = Boto3Session(profile_name).get_for_region(region_name)
    
    def get_all_by_service(self, service="ec2"):
        ec2_client = self.session.client(service)
        return [region.get("RegionName") for region in ec2_client.describe_regions().get("Regions", [])]