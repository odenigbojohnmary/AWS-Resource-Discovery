"""
AWS Disclaimer.

(c) 2020 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
This AWS Content is provided subject to the terms of the AWS Customer
Agreement available at https://aws.amazon.com/agreement/ or other written
agreement between Customer and Amazon Web Services, Inc.

This script is a module called by cwreport.py, it creates the csv file
"""
import yaml
import numpy

# Open the metrics configuration file metrics.yaml and retrive settings
with open("metrics.yaml", "r") as f:
    metrics = yaml.load(f, Loader=yaml.FullLoader)

with open("ec2_costs.yaml", "r") as f:
    costs = yaml.load(f, Loader=yaml.FullLoader)

cost_map = {cost.get("type"): cost for cost in costs["costs"]}


# Construct csv headers and return
def make_csv_header(service):
    if service == "ec2":
        csv_headers = [
            "Name",
            "Instance",
            "Region",
            "VPC ID",
            "Subnet ID",
            "Private Ip Address",
            "AMI ID",
            "Launch Time",
            "Type",
            "State",
            "Approximate Cost",
            "Core Counts",
            "Threads Per Core",
            "Tags",
            "Hypervisor",
            "Virtualization Type",
            "Architecture",
            "EBS Optimized",
            "Public DNS name",
            "Public IP",
        ]
        for metric in metrics["metrics_to_be_collected"][service]:
            csv_headers.append(metric["name"] + " (" + metric["unit"] + ")")
            csv_headers.append("Max" + metric["name"] + " (" + metric["unit"] + ")")
        return csv_headers
    elif service == "ec2_snapshots":
        return [
            "Name",
            "Description",
            "SnapshotId",
            "Region",
            "Encrypted",
            "OwnerId",
            "StartTime",
            "VolumeId",
            "VolumeSize",
            "StorageTier",
            "RestoreExpiryTime",
            "Tags",
        ]
    elif service == "ec2_volumes":
        return [
            "Name",
            "Volume ID",
            "Region",
            "Volume Type",
            "Volume Size",
            "Volume State",
            "Create Time",
            "Tags",
        ]
    elif service == "rds_snapshots":
        return [
            "DBSnapshotIdentifier",
            "DBInstanceIdentifier",
            "Region",
            "SnapshotCreateTime",
            "Engine",
            "AllocatedStorage",
            "Status",
            "Tags",
        ]
    else:
        csv_headers = ["Resource Identifier", "Region"]
        for metric in metrics["metrics_to_be_collected"][service]:
            csv_headers.append(metric["name"] + " (" + metric["unit"] + ")")

        return csv_headers


def get_tag_string(tags):
    if tags:
        return ", ".join([f'"{item["Key"]}": "{item["Value"]}"' for item in tags or []])
    else:
        return ""


def get_resource_name(tags):
    if tags:
        name_dict = next((i for i in tags if i["Key"] == "Name"), None)
    else:
        name_dict = None
    return "" if name_dict is None else name_dict.get("Value")


# function to write to csv
def write_to_csv(
    service, csvwriter, resource, metrics_info, region=None, resource_id=None
):
    if service == "ec2":
        type = resource.instance_type
        cost = (
            cost_map.get(type).get("windows")
            if resource.platform == "Windows"
            else cost_map.get(type).get("linux")
        )
        tags_string = get_tag_string(resource.tags)
        launch_time_string = str(resource.launch_time)
        row_data = [
            get_resource_name(resource.tags),
            resource.id,
            "" if region is None else region,
            resource.vpc_id,
            resource.subnet_id,
            resource.private_ip_address,
            resource.image_id,
            launch_time_string,
            type,
            resource.state.get("Name"),
            cost,
            resource.cpu_options.get("CoreCount", 0),
            resource.cpu_options.get("ThreadsPerCore", 0),
            tags_string,
            resource.hypervisor,
            resource.virtualization_type,
            resource.architecture,
            resource.ebs_optimized,
            resource.public_dns_name,
            resource.public_ip_address,
        ]

        for metric in metrics["metrics_to_be_collected"][service]:
            row_data.append(numpy.round(numpy.average(metrics_info[metric["name"]]), 2))
            row_data.append(numpy.round(numpy.max(metrics_info[metric["name"]]), 2))
        csvwriter.writerow(row_data)
    elif service == "ec2_snapshots":
        row_data = [
            get_resource_name(resource.get("Tags", None)),
            resource["Description"],
            resource["SnapshotId"],
            "" if region is None else region,
            resource["Encrypted"],
            resource["OwnerId"],
            resource["StartTime"],
            resource["VolumeId"],
            resource["VolumeSize"],
            resource["StorageTier"],
            resource.get("RestoreExpiryTime", ""),
            get_tag_string(resource.get("Tags", None)),
        ]
        csvwriter.writerow(row_data)
    elif service == "ec2_volumes":
        row_data = [
            get_resource_name(resource.get("Tags", None)),
            resource["VolumeId"],
            "" if region is None else region,
            resource["VolumeType"],
            resource["Size"],
            resource["State"],
            resource["CreateTime"],
            get_tag_string(resource.get("Tags", None)),
        ]
        csvwriter.writerow(row_data)
    elif service == "rds_snapshots":
        row_data = [
            resource["DBSnapshotIdentifier"],
            resource["DBInstanceIdentifier"],
            "" if region is None else region,
            resource["SnapshotCreateTime"],
            resource["Engine"],
            resource["AllocatedStorage"],
            resource["Status"],
            get_tag_string(resource.get("TagList", None)),
        ]
        csvwriter.writerow(row_data)
    else:
        row_data = [resource_id, region]
        for metric in metrics["metrics_to_be_collected"][service]:
            row_data.append(numpy.round(numpy.average(metrics_info[metric["name"]]), 2))
        csvwriter.writerow(row_data)
