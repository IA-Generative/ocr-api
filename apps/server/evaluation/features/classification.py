from PIL import Image
from typing import Generator
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from business.features.models.features_extraction import FeatureCreator
import uuid


class Dataset:
    def __init__(self, images_paths: list[str], labels: list[str]):
        self.data = list(zip(images_paths, labels))

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, index: int) -> tuple[Image.Image, str]:
        image_path, label = self.data[index]
        image = Image.open(image_path)
        return image, label

    def __iter__(self) -> Generator[tuple[Image.Image, str], None, None]:
        for image_path, label in self.data:
            image = Image.open(image_path)
            yield image, label


class Evaluator:
    def __init__(self):
        self.train_data: Dataset | None = None
        self.test_data: Dataset | None = None
        self.vector_store = QdrantClient(":memory:")
        self.vector_dim: int | None = None
        self.encoder: FeatureCreator | None = None

    def set_encoder(self, encoder: FeatureCreator):
        """Définir le modèle d'encodage des images en vecteurs"""
        self.encoder = encoder
        self.vector_dim = encoder.model_size
        # Créer la collection avec la configuration des vecteurs
        self.vector_store.create_collection(
            collection_name="train",
            vectors_config=VectorParams(
                size=self.vector_dim,
                distance=Distance.COSINE,  # ou Distance.EUCLIDEAN
            ),
        )

    def _encode_image(self, image: Image.Image) -> list[float]:
        """Encoder une image en vecteur"""
        if not self.encoder:
            raise ValueError("Encoder is not set. Use set_encoder() first.")

        # Ici vous utilisez votre modèle pour encoder l'image
        # Exemple avec un modèle hypothétique
        vector = self.encoder.get_vector_from_image(image)
        return vector

    def set_train_data(self, train_data: Dataset):
        self.train_data = train_data
        self._add_vectors_to_store()

    def _add_vectors_to_store(self):
        """Ajouter tous les vecteurs du dataset d'entraînement à Qdrant"""
        if not self.train_data or not self.encoder:
            raise ValueError("Train data and encoder must be set.")

        points = []
        for idx, (image, label) in enumerate(self.train_data):
            # Encoder l'image en vecteur
            vector = self._encode_image(image)

            # Créer un point avec le vecteur et les métadonnées
            point = PointStruct(
                id=str(uuid.uuid4()),  # ID unique
                vector=vector,
                payload={
                    "label": label,
                    "train_index": idx,
                    "image_path": self.train_data.data[idx][0],  # Chemin de l'image
                },
            )
            points.append(point)

        # Insérer tous les points en une fois
        self.vector_store.upsert(collection_name="train", points=points)

    def set_test_data(self, test_data: Dataset):
        self.test_data = test_data

    def get_topk_from_train(self, image: Image.Image, k: int) -> list[tuple[str, float]]:
        """Récupérer les k plus proches voisins avec leurs labels et scores"""
        if not self.train_data:
            raise ValueError("Train data is not set.")

        # Encoder l'image de requête
        query_vector = self._encode_image(image)

        # Rechercher les k plus proches voisins
        search_result = self.vector_store.search(
            collection_name="train",
            query_vector=query_vector,
            limit=k,
            with_payload=True,
            with_vectors=False,  # Pas besoin des vecteurs en retour
        )

        # Extraire les labels et scores
        results = []
        for hit in search_result:
            label = hit.payload["label"]
            score = hit.score
            results.append((label, score))

        return results

    def get_topk_labels_only(self, image: Image.Image, k: int) -> list[str]:
        """Récupérer seulement les labels des k plus proches voisins"""
        topk_results = self.get_topk_from_train(image, k)
        return [label for label, _ in topk_results]

    def top_k_accuracy(self, k: int) -> float:
        if not self.test_data:
            raise ValueError("Test data is not set.")

        correct = 0
        total = 0

        for image, true_label in self.test_data:
            # Récupérer les k plus proches voisins
            top_k_labels = self.get_topk_labels_only(image, k)

            if true_label in top_k_labels:
                correct += 1
            total += 1

        return correct / total if total > 0 else 0.0

    def top_k_accuracy_per_class(self, k: int) -> dict[str, float]:
        if not self.test_data:
            raise ValueError("Test data is not set.")

        class_correct = {}
        class_total = {}

        for image, true_label in self.test_data:
            # Récupérer les k plus proches voisins
            top_k_labels = self.get_topk_labels_only(image, k)

            if true_label in top_k_labels:
                class_correct[true_label] = class_correct.get(true_label, 0) + 1
            class_total[true_label] = class_total.get(true_label, 0) + 1

        # Calculer la précision par classe
        class_accuracies = {
            label: correct / total if total > 0 else 0.0
            for label, (correct, total) in zip(class_correct.keys(), zip(class_correct.values(), class_total.values()))
        }

        return class_accuracies

    def top_k_precision(self, k: int) -> float:
        if not self.test_data:
            raise ValueError("Test data is not set.")

        true_positives = 0
        false_positives = 0

        for image, true_label in self.test_data:
            # Récupérer les k plus proches voisins
            top_k_labels = self.get_topk_labels_only(image, k)

            if true_label in top_k_labels:
                true_positives += 1
            false_positives += len(top_k_labels)

        return true_positives / false_positives if false_positives > 0 else 0.0

    def top_k_recall(self, k: int) -> float:
        if not self.test_data:
            raise ValueError("Test data is not set.")

        true_positives = 0
        false_negatives = 0

        for image, true_label in self.test_data:
            # Récupérer les k plus proches voisins
            top_k_labels = self.get_topk_labels_only(image, k)

            if true_label in top_k_labels:
                true_positives += 1
            else:
                false_negatives += 1

        return true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0

    def top_k_f1_score(self, k: int) -> float:
        precision = self.top_k_precision(k)
        recall = self.top_k_recall(k)
        return 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    def top_k_precision_per_class(self, k: int) -> dict[str, float]:
        if not self.test_data:
            raise ValueError("Test data is not set.")

        class_true_positives = {}
        class_false_positives = {}

        for image, true_label in self.test_data:
            # Récupérer les k plus proches voisins
            top_k_labels = self.get_topk_labels_only(image, k)

            if true_label in top_k_labels:
                class_true_positives[true_label] = class_true_positives.get(true_label, 0) + 1
            for label in top_k_labels:
                class_false_positives[label] = class_false_positives.get(label, 0) + 1

        # Calculer la précision par classe
        class_precisions = {
            label: true_positives / false_positives if false_positives > 0 else 0.0
            for label, (true_positives, false_positives) in zip(
                class_true_positives.keys(),
                zip(class_true_positives.values(), class_false_positives.values()),
            )
        }

        return class_precisions

    def top_k_recall_per_class(self, k: int) -> dict[str, float]:
        if not self.test_data:
            raise ValueError("Test data is not set.")

        class_true_positives = {}
        class_false_negatives = {}

        for image, true_label in self.test_data:
            # Récupérer les k plus proches voisins
            top_k_labels = self.get_topk_labels_only(image, k)

            if true_label in top_k_labels:
                class_true_positives[true_label] = class_true_positives.get(true_label, 0) + 1
            else:
                class_false_negatives[true_label] = class_false_negatives.get(true_label, 0) + 1

        # Calculer le rappel par classe
        class_recalls = {
            label: (
                true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
            )
            for label, (true_positives, false_negatives) in zip(
                class_true_positives.keys(),
                zip(class_true_positives.values(), class_false_negatives.values()),
            )
        }

        return class_recalls

    def top_k_f1_score_per_class(self, k: int) -> dict[str, float]:
        if not self.test_data:
            raise ValueError("Test data is not set.")

        class_precisions = self.top_k_precision_per_class(k)
        class_recalls = self.top_k_recall_per_class(k)

        class_f1_scores = {
            label: (2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0)
            for label, (precision, recall) in zip(
                class_precisions.keys(),
                zip(class_precisions.values(), class_recalls.values()),
            )
        }

        return class_f1_scores

    def get_class_distribution(self) -> dict[str, int]:
        """Obtenir la distribution des classes dans les données d'entraînement"""
        if not self.train_data:
            raise ValueError("Train data is not set.")

        distribution = {}
        for _, label in self.train_data:
            distribution[label] = distribution.get(label, 0) + 1

        return distribution

    def get_metrics_from_test(self, k_values: list[int] = [1, 3, 5, 10]):
        """Obtenir toutes les métriques à partir des données de test"""
        if not self.test_data:
            raise ValueError("Test data is not set.")

        metrics = {}

        # Métriques Top-K Accuracy pour différentes valeurs de K
        for k in k_values:
            metrics[f"top_{k}_accuracy"] = self.top_k_accuracy(k=k)

        # Métriques Top-K Accuracy par classe
        for k in k_values:
            metrics[f"top_{k}_accuracy_per_class"] = self.top_k_accuracy_per_class(k=k)

        # Métriques de Precision globales
        for k in k_values:
            metrics[f"top_{k}_precision"] = self.top_k_precision(k=k)

        # Métriques de Precision par classe
        for k in k_values:
            metrics[f"top_{k}_precision_per_class"] = self.top_k_precision_per_class(k=k)

        # Métriques de Recall globales
        for k in k_values:
            metrics[f"top_{k}_recall"] = self.top_k_recall(k=k)

        # Métriques de Recall par classe
        for k in k_values:
            metrics[f"top_{k}_recall_per_class"] = self.top_k_recall_per_class(k=k)

        # Métriques de F1-Score globales
        for k in k_values:
            metrics[f"top_{k}_f1_score"] = self.top_k_f1_score(k=k)

        # Métriques de F1-Score par classe
        for k in k_values:
            metrics[f"top_{k}_f1_score_per_class"] = self.top_k_f1_score_per_class(k=k)

        # Distribution des classes
        metrics["class_distribution"] = self.get_class_distribution()

        # Métriques additionnelles utiles
        metrics["total_test_samples"] = len(self.test_data)
        metrics["total_train_samples"] = len(self.train_data) if self.train_data else 0
        metrics["number_of_classes"] = len(self.get_class_distribution())

        return metrics

    def mean_reciprocal_rank(self, k: int = 10) -> float:
        """Calculer le Mean Reciprocal Rank"""
        if not self.test_data:
            raise ValueError("Test data is not set.")

        total_rr = 0.0
        total_queries = 0

        for image, true_label in self.test_data:
            # Récupérer les k plus proches voisins avec leurs labels
            top_k_results = self.get_topk_from_train(image, k)

            # Trouver le rang du premier résultat correct
            for rank, (label, _) in enumerate(top_k_results, 1):
                if label == true_label:
                    total_rr += 1.0 / rank
                    break

            total_queries += 1

        return total_rr / total_queries if total_queries > 0 else 0.0

    def get_metrics_from_test_complete(self, k_values: list[int] = [1, 3, 5, 10]):
        """Obtenir toutes les métriques complètes à partir des données de test"""
        if not self.test_data:
            raise ValueError("Test data is not set.")

        metrics = {}

        # Métriques Top-K Accuracy pour différentes valeurs de K
        for k in k_values:
            metrics[f"top_{k}_accuracy"] = self.top_k_accuracy(k=k)

        # Métriques Top-K Accuracy par classe
        for k in k_values:
            metrics[f"top_{k}_accuracy_per_class"] = self.top_k_accuracy_per_class(k=k)

        # Métriques de Precision globales
        for k in k_values:
            metrics[f"top_{k}_precision"] = self.top_k_precision(k=k)

        # Métriques de Precision par classe
        for k in k_values:
            metrics[f"top_{k}_precision_per_class"] = self.top_k_precision_per_class(k=k)

        # Métriques de Recall globales
        for k in k_values:
            metrics[f"top_{k}_recall"] = self.top_k_recall(k=k)

        # Métriques de Recall par classe
        for k in k_values:
            metrics[f"top_{k}_recall_per_class"] = self.top_k_recall_per_class(k=k)

        # Métriques de F1-Score globales
        for k in k_values:
            metrics[f"top_{k}_f1_score"] = self.top_k_f1_score(k=k)

        # Métriques de F1-Score par classe
        for k in k_values:
            metrics[f"top_{k}_f1_score_per_class"] = self.top_k_f1_score_per_class(k=k)

        # Mean Reciprocal Rank
        for k in k_values:
            metrics[f"mrr_at_{k}"] = self.mean_reciprocal_rank(k=k)

        # Distribution des classes
        metrics["class_distribution"] = self.get_class_distribution()

        # Métriques de résumé
        metrics["summary"] = {
            "total_test_samples": len(self.test_data),
            "total_train_samples": len(self.train_data) if self.train_data else 0,
            "number_of_classes": len(self.get_class_distribution()),
            "vector_dimension": self.vector_dim,
            "encoder_model": (getattr(self.encoder, "model_name", "unknown") if self.encoder else None),
        }

        return metrics
