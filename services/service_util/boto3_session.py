import boto3

class Boto3Session:
    def __init__(self, profile_name = None):
        self.profile_name = profile_name

    def get_for_region(self, region_name):
        if self.profile_name:
            session = boto3.session.Session(region_name=region_name, profile_name=self.profile_name)
        else:
            session = boto3.session.Session(region_name=region_name)
        
        return session
