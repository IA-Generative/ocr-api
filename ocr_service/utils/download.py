import os
from surya.common.s3 import download_directory
from ocr_service.configs.surya import SuryaSetting

settings = SuryaSetting()


download_directory(remote_path=settings.SURYA_S3_DETECTION_PATH,
                   local_dir=settings.SURYA_DETECTION_FOLDER)
download_directory(remote_path=settings.SURYA_S3_RECOGNITION_PATH,
                   local_dir=settings.SURYA_RECOGNITION_FOLDER)
