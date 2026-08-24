"""Example of using the synchronous OCR SDK client."""

from pathlib import Path
from ocr_sdk import SyncOCRClient, TaskOperation, TaskStatus
from ocr_sdk.exceptions import OCRAPIError, OCRTimeoutError


def main():
    # Configuration
    api_url = "http://localhost:5000"
    file_path = "path/to/your/document.pdf"  # Changez ceci vers votre fichier

    print("=== OCR SDK - Exemple Synchrone ===\n")

    # Créer le client avec context manager
    with SyncOCRClient(api_url) as client:
        # 1. Vérifier l'état de santé de l'API
        print("1. Vérification de l'état de l'API...")
        try:
            health = client.get_health()
            print(f"   ✓ API Status: {health.status}")
            print(f"   ✓ Version: {health.version}")
            print(f"   ✓ Uptime: {health.up_time}\n")
        except OCRAPIError as e:
            print(f"   ✗ Erreur API: {e}\n")
            return

        # 2. Créer un job OCR
        print("2. Création d'un job OCR...")
        if not Path(file_path).exists():
            print(f"   ✗ Fichier non trouvé: {file_path}")
            print("   Note: Modifiez la variable 'file_path' avec un chemin valide\n")
            return

        try:
            task = client.create_job(
                file_path,
                group_id="EXAMPLE_GROUP",
                task_operation=TaskOperation.DEFAULT,
            )
            print(f"   ✓ Tâche créée: {task.id}")
            print(f"   ✓ Status: {task.status}")
            print(f"   ✓ Position dans la queue: {task.position}\n")
        except OCRAPIError as e:
            print(f"   ✗ Erreur lors de la création du job: {e}\n")
            return

        # 3. Attendre la fin du traitement
        print("3. Attente de la fin du traitement...")
        print("   (Cela peut prendre quelques secondes...)")
        try:
            completed_task = client.wait_for_task(
                task.id, poll_interval=2.0, max_wait_time=300.0
            )
            print("   ✓ Tâche terminée!")
            print(f"   ✓ Status final: {completed_task.status}")
            print(f"   ✓ Pourcentage: {completed_task.percentage}%\n")
        except OCRTimeoutError as e:
            print(f"   ✗ Timeout: {e}\n")
            return
        except OCRAPIError as e:
            print(f"   ✗ Erreur: {e}\n")
            return

        # 4. Récupérer le texte extrait
        if completed_task.status == TaskStatus.COMPLETED.value:
            print("4. Récupération du texte extrait...")
            try:
                text = client.get_task_text(task.id)
                print(f"   ✓ Texte extrait ({len(text)} caractères):")
                print("   " + "-" * 60)
                # Afficher les 500 premiers caractères
                preview = text[:500] + "..." if len(text) > 500 else text
                for line in preview.split("\n"):
                    print(f"   {line}")
                print("   " + "-" * 60 + "\n")
            except OCRAPIError as e:
                print(f"   ✗ Erreur lors de la récupération du texte: {e}\n")

        # 5. Récupérer les détails de la tâche
        print("5. Détails de la tâche...")
        task_details = client.get_task(task.id)
        print(f"   ✓ ID: {task_details.id}")
        print(f"   ✓ Type: {task_details.type}")
        print(f"   ✓ Status: {task_details.status}")
        if task_details.output:
            print(f"   ✓ Nombre de pages: {task_details.output.total_pages}")
            print(f"   ✓ Modèle utilisé: {task_details.output.model_name}")
        print()

        # 6. Lister les tâches de l'utilisateur
        print("6. Liste des tâches récentes...")
        try:
            tasks = client.get_user_tasks(page=1, page_size=5)
            print(f"   ✓ {len(tasks)} tâches trouvées:")
            for t in tasks:
                print(f"     - {t.id[:8]}... | {t.status} | {t.type}")
        except OCRAPIError as e:
            print(f"   ✗ Erreur: {e}")

        print("\n=== Exemple terminé avec succès! ===")


def example_process_document():
    """Exemple simplifié avec process_document."""
    print("\n=== Exemple avec process_document (simplifié) ===\n")

    api_url = "http://localhost:5000"
    file_path = "path/to/your/document.pdf"

    if not Path(file_path).exists():
        print(f"Fichier non trouvé: {file_path}")
        return

    with SyncOCRClient(api_url) as client:
        try:
            # Cette méthode fait tout en une seule étape
            results = client.process_document(
                file_path, max_wait_time=300, poll_interval=2
            )

            print(f"✓ Document traité! {len(results)} pages trouvées\n")

            for i, result in enumerate(results, 1):
                print(f"Page {i}:")
                print(f"  Contenu: {result.page_content[:100]}...")
                print(f"  Metadata: {result.metadata}\n")

        except Exception as e:
            print(f"✗ Erreur: {e}")


if __name__ == "__main__":
    main()

    # Décommentez pour tester l'exemple simplifié
    # example_process_document()
