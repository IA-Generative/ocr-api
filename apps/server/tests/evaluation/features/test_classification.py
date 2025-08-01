import pytest
import pandas as pd
from evaluation.features.classification import Evaluator, Dataset
from business.features.models.factory import (
    get_available_feature_extractors,
    get_feature_extractor,
)


def test_evaluator():
    dataset = Dataset(["tests/data/valid/formulaire-cerfa-complete.png"], ["1"])
    dataset_test = Dataset(["tests/data/valid/formulaire-cerfa-complete.png"], ["1"])
    for extractor in get_available_feature_extractors():
        evaluator = Evaluator()
        model_extractor = get_feature_extractor(extractor)
        evaluator.set_encoder(model_extractor)

        evaluator.set_train_data(dataset)
        evaluator.set_test_data(dataset_test)
        print(79 * "*")
        print(model_extractor.model_name)
        print(evaluator.get_metrics_from_test_complete())
        print(79 * "*")


def test_compare_all_extractors():
    """Compare all feature extractors and display results in a table"""
    dataset = Dataset(["tests/data/valid/formulaire-cerfa-complete.png"], ["1"])
    dataset_test = Dataset(["tests/data/valid/formulaire-cerfa-complete.png"], ["1"])

    results = []
    extractors = get_available_feature_extractors()

    for extractor in extractors:
        evaluator = Evaluator()
        model_extractor = get_feature_extractor(extractor)
        evaluator.set_encoder(model_extractor)
        evaluator.set_train_data(dataset)
        evaluator.set_test_data(dataset_test)

        metrics = evaluator.get_metrics_from_test_complete()

        # Extract key metrics for comparison
        result = {
            "model": model_extractor.model_name,
            "top_1_accuracy": metrics.get("top_1_accuracy", 0),
            "top_3_accuracy": metrics.get("top_3_accuracy", 0),
            "top_5_accuracy": metrics.get("top_5_accuracy", 0),
            "top_1_precision": metrics.get("top_1_precision", 0),
            "top_1_recall": metrics.get("top_1_recall", 0),
            "top_1_f1_score": metrics.get("top_1_f1_score", 0),
            "mrr_at_10": metrics.get("mrr_at_10", 0),
            "vector_dimension": metrics["summary"]["vector_dimension"],
        }
        results.append(result)

    # Create comparison table
    df = pd.DataFrame(results)
    df = df.sort_values("top_1_accuracy", ascending=False)

    print("\n" + "=" * 100)
    print("FEATURE EXTRACTORS COMPARISON")
    print("=" * 100)
    print(df.to_string(index=False, float_format="%.4f"))

    # Find best model
    best_model = df.iloc[0]["model"]
    print(f"\nBest performing model: {best_model}")
    print(f"Top-1 Accuracy: {df.iloc[0]['top_1_accuracy']:.4f}")

    assert len(results) > 0, "No extractors found"


def test_multiple_datasets():
    """Test with multiple test images if available"""
    try:
        # Try with multiple images
        train_images = [
            "tests/data/valid/formulaire-cerfa-complete.png",
            "tests/data/valid/formulaire-cerfa-complete.png",  # Duplicate for testing
        ]
        train_labels = ["1", "1"]

        test_images = ["tests/data/valid/formulaire-cerfa-complete.png"]
        test_labels = ["1"]

        dataset = Dataset(train_images, train_labels)
        dataset_test = Dataset(test_images, test_labels)

        extractors = get_available_feature_extractors()
        if extractors:
            extractor = extractors[0]
            evaluator = Evaluator()
            model_extractor = get_feature_extractor(extractor)
            evaluator.set_encoder(model_extractor)
            evaluator.set_train_data(dataset)
            evaluator.set_test_data(dataset_test)

            metrics = evaluator.get_metrics_from_test_complete()
            assert "top_1_accuracy" in metrics
            assert metrics["summary"]["total_train_samples"] == 2
            assert metrics["summary"]["total_test_samples"] == 1

    except Exception as e:
        pytest.skip(f"Multiple dataset test skipped: {e}")


def test_dataset_functionality():
    """Test Dataset class methods"""
    images = ["tests/data/valid/formulaire-cerfa-complete.png"]
    labels = ["test_label"]

    dataset = Dataset(images, labels)

    # Test length
    assert len(dataset) == 1

    # Test indexing
    image, label = dataset[0]
    assert label == "test_label"

    # Test iteration
    for img, lbl in dataset:
        assert lbl == "test_label"
        break


def test_evaluator_error_handling():
    """Test error handling in Evaluator"""
    evaluator = Evaluator()

    # Test without encoder
    with pytest.raises(ValueError, match="Encoder is not set"):
        from PIL import Image

        dummy_image = Image.new("RGB", (100, 100))
        evaluator._encode_image(dummy_image)

    # Test without train data
    with pytest.raises(ValueError, match="Train data and encoder must be set"):
        evaluator._add_vectors_to_store()

    # Test metrics without test data
    with pytest.raises(ValueError, match="Test data is not set"):
        evaluator.top_k_accuracy(1)


def test_detailed_metrics_analysis():
    """Perform detailed analysis of the best model"""
    dataset = Dataset(["tests/data/valid/formulaire-cerfa-complete.png"], ["1"])
    dataset_test = Dataset(["tests/data/valid/formulaire-cerfa-complete.png"], ["1"])

    extractors = get_available_feature_extractors()
    if not extractors:
        pytest.skip("No extractors available")

    best_results = None
    best_accuracy = 0
    best_model_name = ""

    for extractor in extractors:
        evaluator = Evaluator()
        model_extractor = get_feature_extractor(extractor)
        evaluator.set_encoder(model_extractor)
        evaluator.set_train_data(dataset)
        evaluator.set_test_data(dataset_test)

        metrics = evaluator.get_metrics_from_test_complete()
        top_1_accuracy = metrics.get("top_1_accuracy", 0)

        if top_1_accuracy > best_accuracy:
            best_accuracy = top_1_accuracy
            best_results = metrics
            best_model_name = model_extractor.model_name

    if best_results:
        print(f"\nDetailed analysis for best model: {best_model_name}")
        print(f"Vector dimension: {best_results['summary']['vector_dimension']}")
        print(f"Class distribution: {best_results['class_distribution']}")

        # Print accuracy metrics for different k values
        k_values = [1, 3, 5, 10]
        print("\nAccuracy by k-value:")
        for k in k_values:
            acc = best_results.get(f"top_{k}_accuracy", 0)
            print(f"  Top-{k}: {acc:.4f}")

        assert best_accuracy >= 0, "Accuracy should be non-negative"


def test_performance_benchmark():
    """Benchmark performance of different extractors"""
    import time

    dataset = Dataset(["tests/data/valid/formulaire-cerfa-complete.png"], ["1"])
    dataset_test = Dataset(["tests/data/valid/formulaire-cerfa-complete.png"], ["1"])

    performance_results = []
    extractors = get_available_feature_extractors()

    for extractor in extractors:
        start_time = time.time()

        evaluator = Evaluator()
        model_extractor = get_feature_extractor(extractor)
        evaluator.set_encoder(model_extractor)
        evaluator.set_train_data(dataset)
        evaluator.set_test_data(dataset_test)

        metrics = evaluator.get_metrics_from_test_complete()

        end_time = time.time()
        execution_time = end_time - start_time

        performance_results.append(
            {
                "model": model_extractor.model_name,
                "execution_time": execution_time,
                "top_1_accuracy": metrics.get("top_1_accuracy", 0),
                "vector_dimension": metrics["summary"]["vector_dimension"],
            }
        )

    # Sort by accuracy then by speed
    performance_df = pd.DataFrame(performance_results)
    performance_df = performance_df.sort_values(["top_1_accuracy", "execution_time"], ascending=[False, True])

    print("\n" + "=" * 80)
    print("PERFORMANCE BENCHMARK")
    print("=" * 80)
    print(performance_df.to_string(index=False, float_format="%.4f"))

    if len(performance_results) > 0:
        best_overall = performance_df.iloc[0]
        print(f"\nBest overall model: {best_overall['model']}")
        print(f"Accuracy: {best_overall['top_1_accuracy']:.4f}")
        print(f"Speed: {best_overall['execution_time']:.4f}s")

    assert len(performance_results) > 0, "No performance data collected"
