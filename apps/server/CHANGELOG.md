# Changelog

## 0.1.0 (2025-10-27)


### Features

* :sparkles: add husky, pre-commit and commitlint ([5b77743](https://github.com/IA-Generative/ocr-api/commit/5b77743f85c7d229d33360347556121c213aef6b))
* add all text from pdf ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* add configs directory copy to Dockerfile ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* add docling process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add document extraction support for multiple file formats ([026088c](https://github.com/IA-Generative/ocr-api/commit/026088cab3efb9cd2719fbb4039d70812e551612))
* add example curl commands for OCR API usage ([c3cc714](https://github.com/IA-Generative/ocr-api/commit/c3cc714a6e94f5b0deb42aeb0d1e88ec7633da1a))
* add ocr-docling group to Dockerfile build process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add parameters column to tasks and update migration script ([a1f092a](https://github.com/IA-Generative/ocr-api/commit/a1f092ae75ae27dd3fe92e1f65e680f22f8feec9))
* add PDF forms extraction worker and related tests ([d1392d9](https://github.com/IA-Generative/ocr-api/commit/d1392d9f2bdd605f01d6e966a390575d4a0b46d4))
* add process router for document processing and related tests ([9f2473e](https://github.com/IA-Generative/ocr-api/commit/9f2473e8156fbafcc8d606f056b1acf199ae22bf))
* add purge script for task deletion with Keycloak authentication ([b9197ca](https://github.com/IA-Generative/ocr-api/commit/b9197ca4192ecfe671f73d1bcd18d03682bce948))
* add set_page_text method to OCRResult for page text extraction ([3522ca4](https://github.com/IA-Generative/ocr-api/commit/3522ca4f3b849f5d0904d353c9bc320870146b2c))
* add test.csv file for validation in tests/data/valid ([69cfc75](https://github.com/IA-Generative/ocr-api/commit/69cfc755e6a7a84ffd45988f589503b466b7ee4a))
* add workflow for testing services related to forms ([d5647b9](https://github.com/IA-Generative/ocr-api/commit/d5647b98afe4cec88e80c95275c071fc1cae12b9))
* enhance Keycloak token verification and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* extract text and bounding boxes from PDF pages for improved data processing ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* implement centralized logging configuration system ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* integrate Keycloak authentication and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* merge staging to preprod ([#144](https://github.com/IA-Generative/ocr-api/issues/144)) ([59cb5a8](https://github.com/IA-Generative/ocr-api/commit/59cb5a89691b75fa200af457c59b1b7e2896b5fc))
* refactor PDF form extraction, add vector and template management, and improve feature extraction ([cda4e3d](https://github.com/IA-Generative/ocr-api/commit/cda4e3d73c515ce5a0f20827c4d61fd59ecc3808))
* **security:** improve Keycloak token verification, logging, and documentation ([15c3b87](https://github.com/IA-Generative/ocr-api/commit/15c3b871a5d4ef77d339e1f3f0bf6555a8de1de8))
* update environment variables and refactor job and task routers for improved functionality ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))


### Bug Fixes

* :rocket: don't open twice file ([1ae8f31](https://github.com/IA-Generative/ocr-api/commit/1ae8f31ff1d34e822d07795411af3564bf688c3d))
* add docling_inference directory to Dockerfile ([3707056](https://github.com/IA-Generative/ocr-api/commit/37070567d0ad9f5aa77fe3d1b955b3c9df102a1d))
* ensure task output pages are cleared for non-completed tasks and format delete function parameters ([edb41af](https://github.com/IA-Generative/ocr-api/commit/edb41afa9e0f4dd8b2117909cc168fa5b6a586a6))
* improve logging format and enhance trace context in launch_task ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* remove docling from dependencies and add ocr-docling group ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* remove unused 'tags' parameter from LangFuseTracingService ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* simplify metadata handling in LangFuseTracingService ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* update default task operation to use DEFAULT value in upload_file function ([e5b8162](https://github.com/IA-Generative/ocr-api/commit/e5b8162ea60664dad5e3b774d3d145bff6bec1f3))
* use resource_access and client_id to get roles ([d22ac16](https://github.com/IA-Generative/ocr-api/commit/d22ac162de5acddd0700e8c45482c56bb9b0cb3c))
