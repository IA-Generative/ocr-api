"""Backfill : chiffre au repos les `Task.output` écrits avant l'activation du
chiffrement (colonne `output_encrypted=False`, cf. src/schemas/task.py).

Idempotent et rejouable : ne touche que les lignes marquées `output_encrypted=False` et
s'arrête quand il n'en reste plus. Peut être relancé sans risque à tout moment (ex: après
une interruption), les lignes déjà migrées ne sont jamais retraitées.
"""

from src.logger import logger
from src.schemas.task import task_table

DEFAULT_BATCH_SIZE = 500


def main(batch_size: int = DEFAULT_BATCH_SIZE) -> int:
    total = 0
    while True:
        processed = task_table.encrypt_pending_output(batch_size=batch_size)
        total += processed
        logger.info(f"{processed} tâche(s) traitée(s) dans ce batch (total: {total})")
        if processed < batch_size:
            break

    logger.info(f"Terminé : {total} tâche(s) traitée(s) au total.")
    return total


if __name__ == "__main__":
    main()
