import os
from typing import List, Sequence
import datetime
from itertools import islice

import boto3

from src.schemas import Task
from src.schemas.task import TaskStatus, TaskModel
from src.connector.db_connector import get_db
from sqlalchemy import and_

# --- CONFIGURATION ---
DAYS_TO_KEEP = 7

# --- STATUTS SUPPRIMABLES ---
STATUTS_SUPPRIMABLES = {
    TaskStatus.FAILED.value,
    TaskStatus.CANCELED.value,
    TaskStatus.TIMEOUT.value,
    TaskStatus.COMPLETED.value,
}

# --- S3 CONNECTOR ---
s3_client = boto3.client("s3")
bucket_name = os.environ["S3_BUCKET_NAME"]


# --- UTILS ---
def get_cutoff_timestamp(days: int, hours: int = 0, minutes: int = 0, seconds: int = 0) -> int:
    """Renvoie le timestamp UNIX pour aujourd'hui - N jours (en UTC)."""
    return int(
        (
            datetime.datetime.now() - datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        ).timestamp()
    )


def chunked(iterable: Sequence, size: int) -> Sequence:
    """Découpe un iterable en chunks."""
    it = iter(iterable)
    return iter(lambda: list(islice(it, size)), [])


def fetch_eligible_tasks(cutoff_ts: int) -> List[TaskModel]:
    """Récupère les tâches à supprimer."""
    with get_db() as db:
        tasks = db.query(Task).filter(and_(Task.status.in_(STATUTS_SUPPRIMABLES), Task.created_at <= cutoff_ts)).all()

        return [TaskModel.model_validate(task) for task in tasks]


def delete_s3_objects(keys: list[str]) -> tuple[set, list]:
    """Supprime les objets S3 et renvoie (deleted_keys, errors)."""
    response = s3_client.delete_objects(
        Bucket=bucket_name,
        Delete={"Objects": [{"Key": k} for k in keys], "Quiet": False},
    )
    deleted = set(obj["Key"] for obj in response.get("Deleted", []))
    errors = response.get("Errors", [])
    return deleted, errors


def process_batch(batch: List[TaskModel], dry_run: bool):
    ids = []
    keys = []
    for task in batch:
        ids.append(task.id)
        if task.input and task.input.storage_file_path:
            keys.append(task.input.storage_file_path)

    if dry_run:
        for id in ids:
            print(f"[DRY RUN] ID: {id}")
        return

    # Suppression S3
    if len(keys) > 0:
        try:
            delete_s3_objects(keys)
            print(f"Storage : {keys} deleted")
        except Exception:
            print(f"Deleted error storage keys: {keys}")

    with get_db() as db:
        # Suppression DB
        try:
            db.query(Task).filter(Task.id.in_(ids)).delete(synchronize_session=False)
            db.commit()
            print(f"Deleted : {ids}")
        except Exception as e:
            db.rollback()
            print(e)
            print(f"Deleted error task ids : {ids}")


def main(
    days: int = 7,
    batch_size: int = 5,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
):
    cutoff_ts = get_cutoff_timestamp(days=days, hours=hours, minutes=minutes, seconds=seconds)
    results = fetch_eligible_tasks(cutoff_ts)
    print(f"{len(results)} objets à traiter")

    for batch in chunked(results, batch_size):
        process_batch(batch, dry_run=False)


if __name__ == "__main__":
    main()
