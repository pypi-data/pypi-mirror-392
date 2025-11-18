from uuid import uuid4


def agent_group_id():
    return f"agent_group-{uuid4().hex}"
