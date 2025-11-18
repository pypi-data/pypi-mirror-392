# Exakt wie vorher:
from processcube_client.core.api.client import Client, ProcessInstanceQueryRequest

client = Client("http://localhost:56100")
result = client.process_instance_query(ProcessInstanceQueryRequest(
    limit=1,
    correlation_id="037f337b-2855-4a36-86bc-a298a3ab873b"
))
print(result[0].end_token)