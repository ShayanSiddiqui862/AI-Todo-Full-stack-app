import aiohttp
import json
import logging
from typing import Dict, Any
from backend.src.config import DAPR_HTTP_PORT, DAPR_API_TOKEN

# Set up logging
logger = logging.getLogger(__name__)

async def dapr_publish_event(pubsub_name: str, topic: str, data: Dict[str, Any]):
    """Publish an event to Dapr pub/sub."""
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{pubsub_name}/{topic}"

    headers = {
        "Content-Type": "application/json"
    }

    if DAPR_API_TOKEN:
        headers["dapr-api-token"] = DAPR_API_TOKEN

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps(data)) as resp:
                if resp.status != 200:
                    # Log error but don't fail the operation
                    error_text = await resp.text()
                    logger.error(f"Failed to publish event to {topic}: {resp.status} - {error_text}")
                    return False
                else:
                    logger.info(f"Successfully published event to {topic}")
                    return True
    except aiohttp.ClientError as e:
        logger.error(f"Network error while publishing event to {topic}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while publishing event to {topic}: {str(e)}")
        return False

async def dapr_schedule_job(job_id: str, due_time: str, data: Dict[str, Any]):
    """Schedule a job using Dapr Jobs API."""
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/{job_id}"

    payload = {
        "dueTime": due_time,
        "data": data
    }

    headers = {
        "Content-Type": "application/json"
    }

    if DAPR_API_TOKEN:
        headers["dapr-api-token"] = DAPR_API_TOKEN

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps(payload)) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"Failed to schedule job {job_id}: {resp.status} - {error_text}")
                    return False
                else:
                    logger.info(f"Successfully scheduled job {job_id}")
                    return True
    except aiohttp.ClientError as e:
        logger.error(f"Network error while scheduling job {job_id}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while scheduling job {job_id}: {str(e)}")
        return False

async def dapr_get_secret(store_name: str, key: str) -> str:
    """Retrieve a secret from Dapr secret store."""
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/secrets/{store_name}/{key}"

    headers = {}
    if DAPR_API_TOKEN:
        headers["dapr-api-token"] = DAPR_API_TOKEN

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    logger.info(f"Successfully retrieved secret {key}")
                    return result.get(key)
                else:
                    error_text = await resp.text()
                    logger.error(f"Failed to get secret {key}: {resp.status} - {error_text}")
                    return None
    except aiohttp.ClientError as e:
        logger.error(f"Network error while retrieving secret {key}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while retrieving secret {key}: {str(e)}")
        return None

async def dapr_save_state(key: str, value: Any, store_name: str = "statestore"):
    """Save state using Dapr state management."""
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{store_name}"

    state_item = {
        "key": key,
        "value": value
    }

    headers = {
        "Content-Type": "application/json"
    }

    if DAPR_API_TOKEN:
        headers["dapr-api-token"] = DAPR_API_TOKEN

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=json.dumps([state_item])) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logger.error(f"Failed to save state for key {key}: {resp.status} - {error_text}")
                    return False
                else:
                    logger.info(f"Successfully saved state for key {key}")
                    return True
    except aiohttp.ClientError as e:
        logger.error(f"Network error while saving state for key {key}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error while saving state for key {key}: {str(e)}")
        return False

async def dapr_get_state(key: str, store_name: str = "statestore") -> Any:
    """Get state using Dapr state management."""
    url = f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{store_name}/{key}"

    headers = {}
    if DAPR_API_TOKEN:
        headers["dapr-api-token"] = DAPR_API_TOKEN

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    logger.info(f"Successfully retrieved state for key {key}")
                    return result
                else:
                    error_text = await resp.text()
                    logger.error(f"Failed to get state for key {key}: {resp.status} - {error_text}")
                    return None
    except aiohttp.ClientError as e:
        logger.error(f"Network error while retrieving state for key {key}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while retrieving state for key {key}: {str(e)}")
        return None