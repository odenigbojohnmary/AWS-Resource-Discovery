import datetime
import yaml


class CloudWatchClient:
    def __init__(self, session, service_name):
        self.cloud_watch_client = session.client('cloudwatch')
        self.service_name = service_name
        self.metrics = self.load_metrics_config()

    def load_metrics_config(self):
        with open("metrics.yaml", 'r') as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    def get_metrics_for_resource(self, resource_id):
        datapoints = {}
        now = datetime.datetime.now()
        for metric in self.metrics['metrics_to_be_collected'][self.service_name]:
            if 'statistics' in metric.keys():
                statistics = metric['statistics']
            else:
                statistics = self.metrics['statistics']
            result = self.cloud_watch_client.get_metric_statistics(
                Namespace=metric['namespace'],
                MetricName=metric['name'],
                Dimensions=[{
                    'Name': metric['dimension_name'],
                    'Value': resource_id
                }],
                Unit=metric['unit'],
                Period=self.metrics['period'],
                StartTime=now - datetime.timedelta(hours=self.metrics['hours']),
                EndTime=now,
                Statistics=[statistics]
            )
            actual_datapoint = []
            for datapoint in result['Datapoints']:
                actual_datapoint.append(float(datapoint[statistics]))
            if len(actual_datapoint) == 0:
                actual_datapoint.append(0)
            datapoints[metric['name']] = actual_datapoint

        return datapoints