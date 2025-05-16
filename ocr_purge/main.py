from typing import List
import datetime
from itertools import islice
from sqlalchemy import select, and_
from src.connector.s3_connector import S3Connector
from src.schemas.task import Task, TaskStatus, TaskModel
from src.connector.db_connector import get_db

# --- CONFIGURATION ---
DAYS_TO_KEEP = 7
BATCH_SIZE = 500
DRY_RUN = False

# --- STATUTS SUPPRIMABLES ---
STATUTS_SUPPRIMABLES = {
    TaskStatus.FAILED.value,
    TaskStatus.CANCELED.value,
    TaskStatus.TIMEOUT.value,
    TaskStatus.COMPLETED.value,
}


# --- S3 CONNECTOR ---
s3 = S3Connector()


# --- UTILS ---
def get_cutoff_timestamp(days: int) -> int:
    """Renvoie le timestamp UNIX pour aujourd'hui - N jours (en UTC)."""
    return int((datetime.datetime.now() - datetime.timedelta(days=days)).timestamp())


def chunked(iterable, size):
    """Découpe un iterable en chunks."""
    it = iter(iterable)
    return iter(lambda: list(islice(it, size)), [])


def fetch_eligible_tasks(cutoff_ts: int) -> List[TaskModel]:
    """Récupère les tâches à supprimer."""
    with get_db() as db:
        query = select(Task.id, Task.s3_key).where(
            and_(Task.updated_at <= cutoff_ts, Task.status.in_(STATUTS_SUPPRIMABLES))
        )
        return db.execute(query).fetchall()


def delete_s3_objects(keys: list[str]) -> tuple[set, list]:
    """Supprime les objets S3 et renvoie (deleted_keys, errors)."""
    response = s3.client.delete_objects(
        Bucket=s3.bucket_name,
        Delete={"Objects": [{"Key": k} for k in keys], "Quiet": False},
    )
    deleted = set(obj["Key"] for obj in response.get("Deleted", []))
    errors = response.get("Errors", [])
    return deleted, errors


def process_batch(batch, dry_run: bool, report: dict):
    ids = [row[0] for row in batch]
    keys = [row[1] for row in batch]

    if dry_run:
        for id, key in zip(ids, keys):
            print(f"[DRY RUN] ID: {id}, Key: {key}")
            report["dry_run"].append((id, key))
        return

    # Suppression S3
    try:
        deleted_keys, s3_errors = delete_s3_objects(keys)

        for id, key in zip(ids, keys):
            if key in deleted_keys:
                report["deleted"].append((id, key))
            elif any(e["Key"] == key and e["Code"] == "NoSuchKey" for e in s3_errors):
                report["not_found"].append((id, key))
            else:
                msg = next(
                    (e["Message"] for e in s3_errors if e["Key"] == key),
                    "Erreur inconnue",
                )
                report["errors"].append((id, key, msg))
    except Exception as e:
        for id, key in zip(ids, keys):
            report["errors"].append((id, key, f"Exception S3: {e}"))
        return
    with get_db() as db:
        # Suppression DB
        try:
            db.query(Task).filter(Task.id.in_(ids)).delete(synchronize_session=False)
            db.commit()
        except Exception as e:
            db.rollback()
            for id, key in zip(ids, keys):
                report["errors"].append((id, key, f"Exception DB: {e}"))


def print_report(report):
    print("\n=== RAPPORT FINAL ===")
    print(f"✔️ Supprimés       : {len(report['deleted'])}")
    print(f"❗ Introuvables    : {len(report['not_found'])}")
    print(f"❌ Erreurs         : {len(report['errors'])}")
    print(f"🧪 Dry run         : {len(report['dry_run'])}")

    for title, entries in report.items():
        if entries:
            print(f"\n-- {title.upper()} --")
            for entry in entries:
                print(" -", entry)


def main():
    cutoff_ts = get_cutoff_timestamp(DAYS_TO_KEEP)

    try:
        results = fetch_eligible_tasks(cutoff_ts)
        print(
            f"{'DRY RUN' if DRY_RUN else 'SUPPRESSION'} : {len(results)} objets à traiter"
        )

        report = {"deleted": [], "not_found": [], "errors": [], "dry_run": []}

        for batch in chunked(results, BATCH_SIZE):
            process_batch(batch, DRY_RUN, report)

        print_report(report)

    finally:
        pass


if __name__ == "__main__":
    main()
