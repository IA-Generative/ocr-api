from business.paddleocr2.configs.paddle import PaddleSetting


paddle_settings = PaddleSetting()


def download_paddle_models():
    from paddleocr import PaddleOCR

    PaddleOCR(
        text_detection_model_name="PP-OCRv5_mobile_det",
        text_recognition_model_name="PP-OCRv5_mobile_rec",
        use_doc_orientation_classify=True,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        device="cpu",
    )


if __name__ == "__main__":
    download_paddle_models()
