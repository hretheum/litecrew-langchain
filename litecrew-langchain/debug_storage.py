from fastapi.testclient import TestClient
from litecrew.api import create_app

app = create_app()
client = TestClient(app)

# Create crew
crew_data = {
    'name': 'Test Crew',
    'agents': [{'role': 'Worker', 'goal': 'Work', 'backstory': 'Worker'}],
    'tasks': [{'description': 'Work task', 'agent_role': 'Worker'}]
}
create_response = client.post('/api/v1/crews', json=crew_data)
print('Crew response:', create_response.json())

crew_id = create_response.json()['crew_id']

# Submit task
task_data = {'description': 'Test task', 'expected_output': 'Test output'}
task_response = client.post(f'/api/v1/crews/{crew_id}/tasks', json=task_data)
print('Task response:', task_response.json())

task_id = task_response.json()['task_id']

# Try to get task
get_response = client.get(f'/api/v1/tasks/{task_id}')
print('Get task status:', get_response.status_code)
if get_response.status_code != 200:
    print('Error:', get_response.text)
else:
    print('Task data:', get_response.json())