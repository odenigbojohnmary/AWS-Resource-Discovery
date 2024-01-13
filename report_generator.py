import os
import datetime
import csv
import csvconfig
from services.aws_service import AWSService


class ReportGenerator:
    def __init__(self, aws_service):
        self.aws_service: AWSService = aws_service

    def create_file_dir(self, file_name):
        output_file_dir = os.path.dirname(os.path.abspath(file_name))
        os.makedirs(output_file_dir, exist_ok=True)

    def generate_report(self):
        timestamp = str(datetime.datetime.now())
        file_name = f"reports/{self.aws_service.get_profile_name()}/{self.aws_service.get_service_name()}/report_{timestamp}.csv"
        self.create_file_dir(file_name)
        with open(file_name, "w") as csvfile:
            csvwriter = csv.writer(
                csvfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
            )

            csv_headers = csvconfig.make_csv_header(self.aws_service.get_service_name())
            csvwriter.writerow(csv_headers)

            for region in self.aws_service.get_all_regions():
                print(f"Running script for region: {region}")
                service_client = self.aws_service.create_service_client(region)
                cw_client = self.aws_service.create_cloud_watch_client(region)
                for resource in self.aws_service.get_all_resources(service_client):
                    resource_id = self.aws_service.get_resource_id(resource)
                    print(
                        f"Processing metrics for {self.aws_service.get_service_name()}: {resource_id} ..."
                    )
                    metrics_info = cw_client.get_metrics_for_resource(resource_id)
                    csvconfig.write_to_csv(
                        self.aws_service.get_service_name(),
                        csvwriter,
                        resource,
                        metrics_info,
                        region=region,
                        resource_id=resource_id,
                    )

            print("CSV file %s created." % file_name)
