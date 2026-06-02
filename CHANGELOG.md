## 0.3.1 (2025-05-01)

### Feat

- :sparkles: add submodule infra
- :zap: add tests in containers
- add first client for ocr (#20)
- add input form
- add output format
- output integration
- add output around all
- :tada: add new arch for queueing ocr

### Fix

- **health**: :bug: add all deps for healthcheck
- use right env var
- input for task
- same id for task
- version
- write integration
- :bug: change runner type

### Refactor

- :lipstick: refactor s3
- base and s3
- clean code
- code clean
- :art: change minio vars

## [1.13.0](https://github.com/IA-Generative/ocr-api/compare/v1.12.0...v1.13.0) (2026-06-02)


### Features

* **email:** implement email extraction model and worker for processing email content ([cb04313](https://github.com/IA-Generative/ocr-api/commit/cb043137b9327dd288a0e883cb861d90061889dd))
* **lazy_pdf:** enhance __getitem__ method with overloads for better type hinting ([0dc7f2d](https://github.com/IA-Generative/ocr-api/commit/0dc7f2d18a7e13707240e5913cb932b2e70db990))
* **liteparser:** Refactor file extraction models to use a unified FileHandlerExtractionModel ([5ea920c](https://github.com/IA-Generative/ocr-api/commit/5ea920cbae6b1e4d0408306e325ed9e766c061fd))
* **readme:** update introduction and add supported file formats section ([f6ead06](https://github.com/IA-Generative/ocr-api/commit/f6ead0663ba51694bb6e39ea969d84eb202bc098))
* **upload:** centralize upload formats and MIME type validation for improved consistency ([e15f22c](https://github.com/IA-Generative/ocr-api/commit/e15f22cce612c41008d623b0183a134dbd36f60e))
* **upload:** update upload formats to include EML and adjust labels accordingly ([cb04313](https://github.com/IA-Generative/ocr-api/commit/cb043137b9327dd288a0e883cb861d90061889dd))


### Bug Fixes

* **docker-compose:** format healthcheck test commands for consistency ([ca30275](https://github.com/IA-Generative/ocr-api/commit/ca302755fbcd14b1f9d43571806a27b7b41d445b))

## [1.12.0](https://github.com/IA-Generative/ocr-api/compare/v1.11.1...v1.12.0) (2026-06-02)


### Features

* add mcp server ([32c2d20](https://github.com/IA-Generative/ocr-api/commit/32c2d20ab3d398506c1ab9bed6bc5bcbdf157eec))
* **mcp:** add compatibility patch for fastapi-mcp to handle self-referential models ([b4c8cf1](https://github.com/IA-Generative/ocr-api/commit/b4c8cf108fdc8259b53d535b6e1bbb4f004ca05a))

## [1.11.1](https://github.com/IA-Generative/ocr-api/compare/v1.11.0...v1.11.1) (2026-05-26)


### Bug Fixes

* **jobs:** streamline task handling for OCR processing without chunking ([de1d318](https://github.com/IA-Generative/ocr-api/commit/de1d31809f9f225b39bcd76bb1cb4e8d8cc07969))
* **release:** add versioning strategy for dev branch in release workflow ([a318f90](https://github.com/IA-Generative/ocr-api/commit/a318f903d525f7c30322f58ff8bfa18e7a56ad33))

## [1.11.0](https://github.com/IA-Generative/ocr-api/compare/v1.10.6...v1.11.0) (2026-05-17)


### Features

* **docs:** enhance documentation with new sections for classification, entity extraction, and templates ([6958a4c](https://github.com/IA-Generative/ocr-api/commit/6958a4cba009a9f6ec4ec1e2afa64168347bf2cc))


### Bug Fixes

* **docs:** update table of contents formatting for better readability ([8bfb680](https://github.com/IA-Generative/ocr-api/commit/8bfb680311d7239f7d1983616c097938b480f213))

## [1.10.6](https://github.com/IA-Generative/ocr-api/compare/v1.10.5...v1.10.6) (2026-04-30)


### Bug Fixes

* **chunker:** add SSL verification support using httpx client ([ffb7b8c](https://github.com/IA-Generative/ocr-api/commit/ffb7b8c12f5f4aa908e8761f4c166163a33baef6))

## [1.10.5](https://github.com/IA-Generative/ocr-api/compare/v1.10.4...v1.10.5) (2026-04-30)


### Bug Fixes

* **tasks:** add support for OCR_TASK_ONLY in upload_file function ([5074ad4](https://github.com/IA-Generative/ocr-api/commit/5074ad4daf4d84b65a24efe0eba0a171a6ccbcf6))

## [1.10.4](https://github.com/IA-Generative/ocr-api/compare/v1.10.3...v1.10.4) (2026-04-30)


### Bug Fixes

* **import:** move OpenAIClipModel import to conditional block ([09a40d4](https://github.com/IA-Generative/ocr-api/commit/09a40d4178c3e6f8c9c301a6ec7fb86656aa524c))

## [1.10.3](https://github.com/IA-Generative/ocr-api/compare/v1.10.2...v1.10.3) (2026-04-29)


### Bug Fixes

* **docker:** add healthchecks for minio, redis, and ocr_backend services ([f5dbba1](https://github.com/IA-Generative/ocr-api/commit/f5dbba1249f770a3a25ba4eb961feaec7ebf37bc))
* **tasks:** add fetchTaskPageImage method and update OcrViewer to load page images ([f5dbba1](https://github.com/IA-Generative/ocr-api/commit/f5dbba1249f770a3a25ba4eb961feaec7ebf37bc))

## [1.10.2](https://github.com/IA-Generative/ocr-api/compare/v1.10.1...v1.10.2) (2026-04-22)


### Bug Fixes

* **openai:** add timeout and max retries to OpenAI client configurations ([2cce948](https://github.com/IA-Generative/ocr-api/commit/2cce9489a7a1aa6c73af7ffa8cf2a09a566ca10e))

## [1.10.1](https://github.com/IA-Generative/ocr-api/compare/v1.10.0...v1.10.1) (2026-04-21)


### Bug Fixes

* **queue:** display queue position for tasks in progress ([ed74211](https://github.com/IA-Generative/ocr-api/commit/ed74211661b4389fe36588f4cf70700f153ed0f8))

## [1.10.0](https://github.com/IA-Generative/ocr-api/compare/v1.9.3...v1.10.0) (2026-04-21)


### Features

* **leaderboard:** add leaderboard modal and API integration ([d65984f](https://github.com/IA-Generative/ocr-api/commit/d65984f2e28c85c99bb50c7c2fdfbfe2763a071e))

## [1.9.3](https://github.com/IA-Generative/ocr-api/compare/v1.9.2...v1.9.3) (2026-04-21)


### Bug Fixes

* **statistics:** set default selected period to 'today' ([071aadf](https://github.com/IA-Generative/ocr-api/commit/071aadfa2a64d8ee3debf65e753438895169a8a7))
* **tasks:** add revoke task functionality and update task status mapping ([e3f17ce](https://github.com/IA-Generative/ocr-api/commit/e3f17ce132c5145733444f46bcbd73e0435e2dba))

## [1.9.2](https://github.com/IA-Generative/ocr-api/compare/v1.9.1...v1.9.2) (2026-04-21)


### Bug Fixes

* **tasks:** add task position display for queued tasks in the UI ([3eedd53](https://github.com/IA-Generative/ocr-api/commit/3eedd5390ac3f4d084bdafcc486b01583074ed68))

## [1.9.1](https://github.com/IA-Generative/ocr-api/compare/v1.9.0...v1.9.1) (2026-04-21)


### Bug Fixes

* **boto3:** implement async S3 operations using aioboto3 for improved performance ([b9b9fb7](https://github.com/IA-Generative/ocr-api/commit/b9b9fb79a256b7462ba324d69b3e6e0430259248))

## [1.9.0](https://github.com/IA-Generative/ocr-api/compare/v1.8.0...v1.9.0) (2026-04-21)


### Features

* **migration:** add task indexes for status, created_at, and user_id ([8a2992b](https://github.com/IA-Generative/ocr-api/commit/8a2992b15512d32870b1ea0ef9d27b8f7915b245))


### Bug Fixes

* **stats:** add period filtering for task statistics and health checks ([4090249](https://github.com/IA-Generative/ocr-api/commit/4090249d36f3a678c66da6dabbf11d6eb84bbc00))

## [1.8.0](https://github.com/IA-Generative/ocr-api/compare/v1.7.0...v1.8.0) (2026-04-21)


### Features

* add task statistics by type for global and user tasks ([83d4e41](https://github.com/IA-Generative/ocr-api/commit/83d4e41e52fc6d23595a0de504d64c3479ea3a4f))

## [1.7.0](https://github.com/IA-Generative/ocr-api/compare/v1.6.0...v1.7.0) (2026-04-20)


### Features

* add result file download functionality and template filling feature ([20278a9](https://github.com/IA-Generative/ocr-api/commit/20278a975c91baad5e2b884e914b5afb2299c84a))
* Add templating functionality with CRUD operations ([2ad672b](https://github.com/IA-Generative/ocr-api/commit/2ad672bb0bf6b53536787e573480644e626d440b))
* add usage guides for document classification, entity extraction, and template management ([323cab3](https://github.com/IA-Generative/ocr-api/commit/323cab303f804438637f4c866151b925054acadf))
* **templating:** add TemplateHistoryModal component and integrate into TemplatesView ([9744eda](https://github.com/IA-Generative/ocr-api/commit/9744eda29b1e76c4f4a58cb8da030cd4cc42f87d))
* **templating:** implement templating field extraction and add tests ([72013fe](https://github.com/IA-Generative/ocr-api/commit/72013fecc2bcd5f33512db671fd3c2dcb62b8c67))

## [1.6.0](https://github.com/IA-Generative/ocr-api/compare/v1.5.1...v1.6.0) (2026-04-20)


### Features

* **training:** add training process ([65fa2ca](https://github.com/IA-Generative/ocr-api/commit/65fa2ca7b0b306407736f3376734ba0f372ce13f))

## [1.5.1](https://github.com/IA-Generative/ocr-api/compare/v1.5.0...v1.5.1) (2026-04-19)


### Bug Fixes

* **paddle:** adjust recognition batch size and add CPU threading options ([9f22d2a](https://github.com/IA-Generative/ocr-api/commit/9f22d2a009fe02f7518da2dff653fe289f34a8db))

## [1.5.0](https://github.com/IA-Generative/ocr-api/compare/v1.4.3...v1.5.0) (2026-04-19)


### Features

* add imageUrl prop and thumbnail display to detail modals ([2483b28](https://github.com/IA-Generative/ocr-api/commit/2483b28142674f456dd45ba8be5a8804fa10d99e))
* add layout components for formula, image, and table blocks ([a84d05a](https://github.com/IA-Generative/ocr-api/commit/a84d05a5e8973878717e205edb3348b13384f17f))


### Bug Fixes

* **modal:** update background color and margin styles for better visibility ([613549f](https://github.com/IA-Generative/ocr-api/commit/613549fd9777038dd3b2212b3156e1ca4f95ff4e))

## [1.4.3](https://github.com/IA-Generative/ocr-api/compare/v1.4.2...v1.4.3) (2026-04-19)


### Bug Fixes

* **progress:** enhance progress tracking for OCR and entity extraction ([826db21](https://github.com/IA-Generative/ocr-api/commit/826db2107b499deea3c0f7aabc2f5b7a29b5498d))

## [1.4.2](https://github.com/IA-Generative/ocr-api/compare/v1.4.1...v1.4.2) (2026-04-18)


### Bug Fixes

* **modal:** add modal ([a8ef2b7](https://github.com/IA-Generative/ocr-api/commit/a8ef2b7902431f983643b2c576b6fb842872000c))

## [1.4.1](https://github.com/IA-Generative/ocr-api/compare/v1.4.0...v1.4.1) (2026-04-18)


### Bug Fixes

* **task:** add user_id to task forms and processing functions ([4f8457c](https://github.com/IA-Generative/ocr-api/commit/4f8457cd9466f6a687f9671536597250c69f3db8))

## [1.4.0](https://github.com/IA-Generative/ocr-api/compare/v1.3.0...v1.4.0) (2026-04-18)


### Features

* **entity:** entity extraction ([3ded0f6](https://github.com/IA-Generative/ocr-api/commit/3ded0f64cf284f83502b6f94bac09fc55df0cce2))

## [1.3.0](https://github.com/IA-Generative/ocr-api/compare/v1.2.5...v1.3.0) (2026-04-18)


### Features

* **classification:** add classification and layout ([882a9a6](https://github.com/IA-Generative/ocr-api/commit/882a9a64a35905c2f0960f630261276eaf4f1a6b))
* **classification:** add classification part ([788cf14](https://github.com/IA-Generative/ocr-api/commit/788cf1448a5f49abb4535cb32d28ba6b3467795d))
* **classification:** implement text classification model and related tasks ([3ef3e51](https://github.com/IA-Generative/ocr-api/commit/3ef3e516e3a9aad56c1f90979da3fce36274c731))

## [1.2.5](https://github.com/IA-Generative/ocr-api/compare/v1.2.4...v1.2.5) (2026-04-16)


### Bug Fixes

* **api-token:** update token validation to set user roles and admin status ([99da27c](https://github.com/IA-Generative/ocr-api/commit/99da27c2db2046898dfb8714ca65d057e6b64292))

## [1.2.4](https://github.com/IA-Generative/ocr-api/compare/v1.2.3...v1.2.4) (2026-04-16)


### Bug Fixes

* **docker:** remove conditional for uv image stage in Dockerfiles ([53019e7](https://github.com/IA-Generative/ocr-api/commit/53019e787534a8aae1285105175b493e2dbe7815))
* **release:** add bootstrap-sha to prevent old breaking change from bumping major version ([fd8c346](https://github.com/IA-Generative/ocr-api/commit/fd8c346c70e1ca17ec145fbaacd5336e324baa03))
* **release:** add last-release-sha to force release-please start point [skip gha] ([564e0c6](https://github.com/IA-Generative/ocr-api/commit/564e0c6cbfe54ca0fe2fce97cbc34fd1b4b664e9))
* **release:** remove bootstrap/last-release-sha, fix v1.2.3 tag placement ([15a9544](https://github.com/IA-Generative/ocr-api/commit/15a954493a17d52f86ba12b8c9906666b5a10ff3))
* **release:** update manifest file handling for dev branch and add prerelease manifest ([8c06cff](https://github.com/IA-Generative/ocr-api/commit/8c06cff3fbdec73def54688e4866bf891330304f))

## [1.2.3](https://github.com/IA-Generative/ocr-api/compare/v1.2.2...v1.2.3) (2026-04-16)


### Bug Fixes

* **security:** update token verification logic to use get_token_by_value ([f6fd504](https://github.com/IA-Generative/ocr-api/commit/f6fd5041cc71584b4d3c3a8400cd82b6e0eb2b79))

## [1.2.2](https://github.com/IA-Generative/ocr-api/compare/v1.2.1...v1.2.2) (2026-04-16)


### Bug Fixes

* **server:** update default headers to use environment variable for API key ([5374506](https://github.com/IA-Generative/ocr-api/commit/5374506295844c881050ab245dac556ab70d11ce))

## [1.2.1](https://github.com/IA-Generative/ocr-api/compare/v1.2.0...v1.2.1) (2026-04-16)


### Bug Fixes

* **docs:** update demo OCR GIF to reflect recent changes ([7a28063](https://github.com/IA-Generative/ocr-api/commit/7a28063a2fcc2f4565ca9e540ab01e058719bd2a))

## [1.2.0](https://github.com/IA-Generative/ocr-api/compare/v1.1.3...v1.2.0) (2026-04-16)


### Features

* **security:** enhance token verification and logging; update API keys in docker-compose for testing ([6d9f426](https://github.com/IA-Generative/ocr-api/commit/6d9f426aa887bd8ba5b9126e855209f020d318a5))

## [1.1.3](https://github.com/IA-Generative/ocr-api/compare/v1.1.2...v1.1.3) (2026-04-16)


### Bug Fixes

* **docs:** update documentation for token management and job submission parameters ([b811ece](https://github.com/IA-Generative/ocr-api/commit/b811eceaed87fd96c228a2dfdfe67b9077fc69aa))

## [1.1.2](https://github.com/IA-Generative/ocr-api/compare/v1.1.1...v1.1.2) (2026-04-16)


### Bug Fixes

* **ui:** add experimental feature warning banner to Classification components ([f99d762](https://github.com/IA-Generative/ocr-api/commit/f99d76257e3325332e4cab066745d86d478f71e6))

## [1.1.1](https://github.com/IA-Generative/ocr-api/compare/v1.1.0...v1.1.1) (2026-04-16)


### Bug Fixes

* **config:** update path for uv.lock in release configuration ([30059f8](https://github.com/IA-Generative/ocr-api/commit/30059f82e04ed0a85acf18a7ec4943598b41f00d))
* **Dockerfile, download_paddle_models_v3.py:** comment out ocr-service-features group and clip model loading ([e040774](https://github.com/IA-Generative/ocr-api/commit/e0407740f117aee88415ef88e491d0567b6742fc))
* **release:** fix release ([41f5c4c](https://github.com/IA-Generative/ocr-api/commit/41f5c4c319f25433c65b83976d1c92181ec35d38))

## [2.0.0](https://github.com/IA-Generative/ocr-api/compare/v1.0.0...v2.0.0) (2026-04-15)


### ⚠ BREAKING CHANGES

* **services:** refacto add token, classification

### Features

* :art: add auth with backend ([8d5b74c](https://github.com/IA-Generative/ocr-api/commit/8d5b74cf18eedf7b0c4f9a1c73eee71404f8d120))
* :art: add headers to api ([ca4e425](https://github.com/IA-Generative/ocr-api/commit/ca4e425fd2d9f1a134d7ce5ee5491b22643f09ba))
* :chart_with_upwards_trend: add matomo tracking ([e0cbb46](https://github.com/IA-Generative/ocr-api/commit/e0cbb46d1487386dbca7ff3b35b7aa094a389fa6))
* :sparkles: add husky, pre-commit and commitlint ([5b77743](https://github.com/IA-Generative/ocr-api/commit/5b77743f85c7d229d33360347556121c213aef6b))
* :sparkles: update environment variables and improve sidebar links ([4a3f1e6](https://github.com/IA-Generative/ocr-api/commit/4a3f1e67158313ef84c757e05cb85ab68d95666f))
* add all text from pdf ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* add configs directory copy to Dockerfile ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* add delete routers ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* add docling process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add document extraction support for multiple file formats ([026088c](https://github.com/IA-Generative/ocr-api/commit/026088cab3efb9cd2719fbb4039d70812e551612))
* add example curl commands for OCR API usage ([c3cc714](https://github.com/IA-Generative/ocr-api/commit/c3cc714a6e94f5b0deb42aeb0d1e88ec7633da1a))
* add Keycloak configuration details and OpenAI API variables to documentation ([ff217ac](https://github.com/IA-Generative/ocr-api/commit/ff217ac84f988c7da8e3193f5675f1eb5180150e))
* add ocr-docling group to Dockerfile build process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add OPENAI_API_KEY to environment configuration ([95de513](https://github.com/IA-Generative/ocr-api/commit/95de5131a084d84f35d1287df07fd518b2a659bc))
* add parameters column to tasks and update migration script ([a1f092a](https://github.com/IA-Generative/ocr-api/commit/a1f092ae75ae27dd3fe92e1f65e680f22f8feec9))
* add PDF forms extraction worker and related tests ([d1392d9](https://github.com/IA-Generative/ocr-api/commit/d1392d9f2bdd605f01d6e966a390575d4a0b46d4))
* add process router for document processing and related tests ([9f2473e](https://github.com/IA-Generative/ocr-api/commit/9f2473e8156fbafcc8d606f056b1acf199ae22bf))
* add purge script for task deletion with Keycloak authentication ([b9197ca](https://github.com/IA-Generative/ocr-api/commit/b9197ca4192ecfe671f73d1bcd18d03682bce948))
* add set_page_text method to OCRResult for page text extraction ([3522ca4](https://github.com/IA-Generative/ocr-api/commit/3522ca4f3b849f5d0904d353c9bc320870146b2c))
* add test.csv file for validation in tests/data/valid ([69cfc75](https://github.com/IA-Generative/ocr-api/commit/69cfc755e6a7a84ffd45988f589503b466b7ee4a))
* add workflow for testing services related to forms ([d5647b9](https://github.com/IA-Generative/ocr-api/commit/d5647b98afe4cec88e80c95275c071fc1cae12b9))
* **annotation:** feat(annotation):  ([14d2446](https://github.com/IA-Generative/ocr-api/commit/14d244614e23ede5c91213addc9a88e4d0c300fa))
* **api:** enhance API key handling and validation in ApiToken class ([#265](https://github.com/IA-Generative/ocr-api/issues/265)) ([59531d8](https://github.com/IA-Generative/ocr-api/commit/59531d87b54a2b9ed2883c7610276a147a915579))
* **api:** enhance task and token management endpoints with detailed descriptions and new operations ([6fdd7ce](https://github.com/IA-Generative/ocr-api/commit/6fdd7cea6460e873e78dafa1195a66f093213ff7))
* **AppFooter:** add footer component to display application version ([e5cabb0](https://github.com/IA-Generative/ocr-api/commit/e5cabb095dc755fc848cff5524e71e6b627555d8))
* **Classification:** implement classification result component and integrate into classification view ([9b26995](https://github.com/IA-Generative/ocr-api/commit/9b26995197b73b3db1e7f2424848c2654da067e5))
* **docker:** add PaddleOCR model download script and update Dockerfile ([#264](https://github.com/IA-Generative/ocr-api/issues/264)) ([1e179f2](https://github.com/IA-Generative/ocr-api/commit/1e179f28843c73a32475be635b99abc44a748cf3))
* **docs:** add Langfuse tracing configuration variables ([88ee3b5](https://github.com/IA-Generative/ocr-api/commit/88ee3b5172da4e43a3f8459c8d12542af8bf4d85))
* enhance Keycloak token verification and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* enhance task management with admin checks and update request context ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* extract text and bounding boxes from PDF pages for improved data processing ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* implement centralized logging configuration system ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* integrate Keycloak authentication and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* integrate Keycloak for authentication and user management ([521a930](https://github.com/IA-Generative/ocr-api/commit/521a930719010e44b6ae39b4c4e5fb6d48a0354a))
* merge staging to preprod ([#144](https://github.com/IA-Generative/ocr-api/issues/144)) ([59cb5a8](https://github.com/IA-Generative/ocr-api/commit/59cb5a89691b75fa200af457c59b1b7e2896b5fc))
* **new:** add annotation view ([#251](https://github.com/IA-Generative/ocr-api/issues/251)) ([f8d5b9e](https://github.com/IA-Generative/ocr-api/commit/f8d5b9e7aa637c85b73a4a1924e8bfc89b16a8d0))
* **OpenAIClip:** update model loading to use configurable CLIP_MODEL_DIR ([3d97a51](https://github.com/IA-Generative/ocr-api/commit/3d97a51b5540e53e1bfc2c8812cab61ab4fa65e3))
* **PaddleSetting:** add CLIP_MODEL_DIR configuration for model downloads ([3d97a51](https://github.com/IA-Generative/ocr-api/commit/3d97a51b5540e53e1bfc2c8812cab61ab4fa65e3))
* refactor PDF form extraction, add vector and template management, and improve feature extraction ([cda4e3d](https://github.com/IA-Generative/ocr-api/commit/cda4e3d73c515ce5a0f20827c4d61fd59ecc3808))
* **security:** improve Keycloak token verification, logging, and documentation ([15c3b87](https://github.com/IA-Generative/ocr-api/commit/15c3b871a5d4ef77d339e1f3f0bf6555a8de1de8))
* **services:** refacto add token, classification ([bb08512](https://github.com/IA-Generative/ocr-api/commit/bb085128ef85b068dabb159ed44f30c93ccd9186))
* **TasksTab:** enhance task display with file information and improved task type labels ([9b26995](https://github.com/IA-Generative/ocr-api/commit/9b26995197b73b3db1e7f2424848c2654da067e5))
* update environment variables and refactor job and task routers for improved functionality ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))


### Bug Fixes

* :label: fix error types ts ([c3d1a13](https://github.com/IA-Generative/ocr-api/commit/c3d1a1377f0899cccb8696499abd3c4addcbebce))
* :passport_control: fixing keycloak infinity loop on sign in ([0bc8db0](https://github.com/IA-Generative/ocr-api/commit/0bc8db07a79b770b2e765fa607f4d5f240493217))
* :rocket: don't open twice file ([1ae8f31](https://github.com/IA-Generative/ocr-api/commit/1ae8f31ff1d34e822d07795411af3564bf688c3d))
* :white_check_mark: fix ocr e2e test ([f225d2f](https://github.com/IA-Generative/ocr-api/commit/f225d2f2e7fdbe5ac28b99fe34542c5d13d546e7))
* add clearToken when keycloak logout ([1fabd51](https://github.com/IA-Generative/ocr-api/commit/1fabd51be72115d858eb204512adacbf92e4340b))
* add docling_inference directory to Dockerfile ([3707056](https://github.com/IA-Generative/ocr-api/commit/37070567d0ad9f5aa77fe3d1b955b3c9df102a1d))
* add missing extraction files to Dockerfile ([0f3be43](https://github.com/IA-Generative/ocr-api/commit/0f3be43371cc68e2759d7b8ba70ab5661d365164))
* add missing version and tag_name outputs to release workflow ([9f69eeb](https://github.com/IA-Generative/ocr-api/commit/9f69eeb00da51d0beda9e90bfac4173983f7a5fe))
* add more log using user_id ([9b310c9](https://github.com/IA-Generative/ocr-api/commit/9b310c9a25ad8fdc73e15ffff17e3a3c82e5adb5))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* **ci:** add HARBOR_PROXY_URL build argument to Docker build configurations ([6ed5d12](https://github.com/IA-Generative/ocr-api/commit/6ed5d12f695401d6dfec832d7ca491b82be97ac3))
* **ci:** guard release-please against force-pushes and invalid branch dispatches ([#281](https://github.com/IA-Generative/ocr-api/issues/281)) ([2bf0317](https://github.com/IA-Generative/ocr-api/commit/2bf031762778929f8a9d56f1fca69a051d8126ed))
* **ci:** set lowercase registry prefix for Docker image tags ([#283](https://github.com/IA-Generative/ocr-api/issues/283)) ([7aa2b85](https://github.com/IA-Generative/ocr-api/commit/7aa2b850a46462846ec253c378e7e4e26fb81ca1))
* **ci:** update Docker build rules for ocr-api, ocr-worker, and ocr-f… ([#287](https://github.com/IA-Generative/ocr-api/issues/287)) ([a2d567e](https://github.com/IA-Generative/ocr-api/commit/a2d567eddd05336d38f33398685595078050c4ee))
* **ci:** update image names to include tags for Docker builds ([#278](https://github.com/IA-Generative/ocr-api/issues/278)) ([#280](https://github.com/IA-Generative/ocr-api/issues/280)) ([5219460](https://github.com/IA-Generative/ocr-api/commit/52194609812107d52e51ebeebd2c3ed3574aabf2))
* **ci:** update image tagging logic in GitLab CI configuration ([#293](https://github.com/IA-Generative/ocr-api/issues/293)) ([b6de937](https://github.com/IA-Generative/ocr-api/commit/b6de937477d8cb2fad88d6001fa42f6395f304ba))
* **ci:** update image tagging logic to always include branch tags ([#295](https://github.com/IA-Generative/ocr-api/issues/295)) ([5a9204c](https://github.com/IA-Generative/ocr-api/commit/5a9204c5fcc12598500578f41ec09562d11b312e))
* correct attribut href to in DsfrTile component ([43f670a](https://github.com/IA-Generative/ocr-api/commit/43f670a4171cbc6fe67a37bd00b87bda0ed97a6c))
* delete role in headers (not necessary) ([098d6a6](https://github.com/IA-Generative/ocr-api/commit/098d6a68f8ff74f0a3ff607f1e7c26b371395265))
* **docker:** add TORCHINDUCTOR_CACHE_DIR environment variable ([#297](https://github.com/IA-Generative/ocr-api/issues/297)) ([b1b2797](https://github.com/IA-Generative/ocr-api/commit/b1b27973aaf2304cc3f715483a16ac3434f8c399))
* **Dockerfile:** add ocr-service-features group to uv sync command ([9bdff82](https://github.com/IA-Generative/ocr-api/commit/9bdff8292316f9e40a52670cf2e9d477972409bb))
* **docker:** include chunks directory in Dockerfile ([#276](https://github.com/IA-Generative/ocr-api/issues/276)) ([dfd54b8](https://github.com/IA-Generative/ocr-api/commit/dfd54b865708c3636e707033b38890ba40e56468))
* enable SSL verification for S3 client and improve code formatting ([#254](https://github.com/IA-Generative/ocr-api/issues/254)) ([33d197f](https://github.com/IA-Generative/ocr-api/commit/33d197f8fa8590a8de6c53fb1a8b68809e8bb7d0))
* ensure task output pages are cleared for non-completed tasks and format delete function parameters ([edb41af](https://github.com/IA-Generative/ocr-api/commit/edb41afa9e0f4dd8b2117909cc168fa5b6a586a6))
* fix keycloak client id ([c5e932e](https://github.com/IA-Generative/ocr-api/commit/c5e932ea1e662d624c6816a6113e090f9660b209))
* hot fix lock ([2e93413](https://github.com/IA-Generative/ocr-api/commit/2e93413ed1802fa711a78a549b36d522fe013273))
* improve code formatting and structure in token verification classes ([#259](https://github.com/IA-Generative/ocr-api/issues/259)) ([d85cc55](https://github.com/IA-Generative/ocr-api/commit/d85cc55a591ffc6d36d4d172b5c7272de18dbd03))
* improve logging format and enhance trace context in launch_task ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* mettre à jour les chemins des liens dans la barre latérale ([78c54ea](https://github.com/IA-Generative/ocr-api/commit/78c54eaa3c94d030cb73deef41588911173b45a6))
* mettre à jour les liens des conditions d'utilisation et de la FAQ dans la barre latérale ([88e73de](https://github.com/IA-Generative/ocr-api/commit/88e73decd3986bb9dedbfe8c49cccc1368876300))
* Refactor batch_predict method to improve handling of predictions and ensure non-null checks for better stability ([#55](https://github.com/IA-Generative/ocr-api/issues/55)) ([2ffdcfc](https://github.com/IA-Generative/ocr-api/commit/2ffdcfc07f2ff12b2cb399066e28a05bbd385de8))
* **release:** remove unnecessary blank line in release workflow ([#291](https://github.com/IA-Generative/ocr-api/issues/291)) ([a71fd77](https://github.com/IA-Generative/ocr-api/commit/a71fd777e61f7c71dace05b0e661b24764d4e204))
* **release:** unify release ([#246](https://github.com/IA-Generative/ocr-api/issues/246)) ([80c044c](https://github.com/IA-Generative/ocr-api/commit/80c044c545ffc92ef25df156aed7ff5645a19adb))
* **release:** update image version deletion logic in GitHub Actions w… ([#289](https://github.com/IA-Generative/ocr-api/issues/289)) ([29bf3e1](https://github.com/IA-Generative/ocr-api/commit/29bf3e1e22278d11f3b08c200b96b8ca259c755d))
* remove docling from dependencies and add ocr-docling group ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* remove unused 'tags' parameter from LangFuseTracingService ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* **router:** extend token expiration time for presigned URLs ([9b26995](https://github.com/IA-Generative/ocr-api/commit/9b26995197b73b3db1e7f2424848c2654da067e5))
* **security:** hash API tokens for secure storage and verification ([9b26995](https://github.com/IA-Generative/ocr-api/commit/9b26995197b73b3db1e7f2424848c2654da067e5))
* **server:** url presigned and prossion text ([#274](https://github.com/IA-Generative/ocr-api/issues/274)) ([f27d75e](https://github.com/IA-Generative/ocr-api/commit/f27d75e344230b2068549c38876f6ffbdaed05c5))
* simplify metadata handling in LangFuseTracingService ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* **tests:** unitttest and model folder ([#270](https://github.com/IA-Generative/ocr-api/issues/270)) ([8defbfa](https://github.com/IA-Generative/ocr-api/commit/8defbfa1faa2c203cd0f3137d7dcb0acce1fbfd3))
* **token:** add token approach ([80e0aeb](https://github.com/IA-Generative/ocr-api/commit/80e0aeb7c325bd59dc8aea99501c7e1d563995ca))
* **TokenModal:** refactor token management to use HTTP client for API requests ([12f89df](https://github.com/IA-Generative/ocr-api/commit/12f89dfc0a653fb0d4cff3a10c1a1f0daf21eb16))
* **TokenModal:** update API endpoint to include trailing slash for token requests ([d6e6fd2](https://github.com/IA-Generative/ocr-api/commit/d6e6fd202b07bb63634b9c49a68f694307e0ec8b))
* update apps/client/src/api/http-client.ts ([7012539](https://github.com/IA-Generative/ocr-api/commit/70125395a3408a92004ab257e178714f9d53f020))
* update apps/client/src/api/http-client.ts ([2d0704f](https://github.com/IA-Generative/ocr-api/commit/2d0704f6d0f7815c4e0a501990aa9ba80701b5eb))
* update apps/client/src/api/http-client.ts ([453edc0](https://github.com/IA-Generative/ocr-api/commit/453edc0c6203c9bfee29402161a96409e9b2f377))
* update apps/client/src/utils/keycloak.ts ([9bca0e0](https://github.com/IA-Generative/ocr-api/commit/9bca0e03a7c67386a9a1e87c17716943310ab5dc))
* update apps/client/src/utils/keycloak.ts ([cdfb2f9](https://github.com/IA-Generative/ocr-api/commit/cdfb2f9c1b9443ae4aff82e9c45e4397453d1574))
* update apps/client/src/utils/keycloak.ts ([12b3614](https://github.com/IA-Generative/ocr-api/commit/12b3614a3bb2aef2669ca0bebde8d43d8b20092d))
* update apps/client/src/utils/keycloak.ts ([655e2ee](https://github.com/IA-Generative/ocr-api/commit/655e2eeda630b3d6fce788d6c8f06a217c154915))
* update apps/client/src/utils/keycloak.ts ([cb674a4](https://github.com/IA-Generative/ocr-api/commit/cb674a44d5cc705345242179cc5d66b40620004b))
* update apps/client/src/utils/keycloak.ts ([cb0a6c0](https://github.com/IA-Generative/ocr-api/commit/cb0a6c096f9b1736ebf4f9aa10b978e3c1c11a04))
* update apps/client/src/utils/keycloak.ts ([0a5e16b](https://github.com/IA-Generative/ocr-api/commit/0a5e16bd52602d0618e1882cdd2e0619b45dcedd))
* update default task operation to use DEFAULT value in upload_file function ([e5b8162](https://github.com/IA-Generative/ocr-api/commit/e5b8162ea60664dad5e3b774d3d145bff6bec1f3))
* update environment variables and adjust frontend port in docker-compose ([#272](https://github.com/IA-Generative/ocr-api/issues/272)) ([3e88d8d](https://github.com/IA-Generative/ocr-api/commit/3e88d8d430daea725954eb6dc44d170122fe00a5))
* update maxfail option in test commands to allow all tests to run ([00616f0](https://github.com/IA-Generative/ocr-api/commit/00616f004ae19bee5a587ed5fd71c963091f79b4))
* update package name in release-please manifest ([2786f37](https://github.com/IA-Generative/ocr-api/commit/2786f37b1ecd64607f0f34b579a56d28aecdaf4e))
* update package names and include-component-in-tag settings in re… ([#238](https://github.com/IA-Generative/ocr-api/issues/238)) ([e41e106](https://github.com/IA-Generative/ocr-api/commit/e41e10695e4839e525cd5afccc1f675032a1c21e))
* update PaddleOCR base directory path in Dockerfile ([#261](https://github.com/IA-Generative/ocr-api/issues/261)) ([b9e6d8c](https://github.com/IA-Generative/ocr-api/commit/b9e6d8cde4aab7b0c600ad28e65ce4346eaf622b))
* update PaddleOCR model version to PP-OCRv3 in Dockerfile ([#257](https://github.com/IA-Generative/ocr-api/issues/257)) ([b219897](https://github.com/IA-Generative/ocr-api/commit/b219897978a7a67c0147740ac9357fd032741a21))
* update release workflow to correct manifest and config file paths ([93de8cc](https://github.com/IA-Generative/ocr-api/commit/93de8cc4636c41e568bec0a069972c37dc020388))
* update SDK test cases and improve Makefile for testing ([#242](https://github.com/IA-Generative/ocr-api/issues/242)) ([e00afd8](https://github.com/IA-Generative/ocr-api/commit/e00afd832068a76b072ddc3cb9a363a9a92a31b9))
* use resource_access and client_id to get roles ([d22ac16](https://github.com/IA-Generative/ocr-api/commit/d22ac162de5acddd0700e8c45482c56bb9b0cb3c))

## [1.0.0](https://github.com/IA-Generative/ocr-api/compare/v0.15.0...v1.0.0) (2026-04-15)


### ⚠ BREAKING CHANGES

* **services:** refacto add token, classification

### Features

* **api:** enhance task and token management endpoints with detailed descriptions and new operations ([24aae9a](https://github.com/IA-Generative/ocr-api/commit/24aae9a8f2edb755b2ac486fa4cb7c00f8468825))
* **Classification:** implement classification result component and integrate into classification view ([4b9c17a](https://github.com/IA-Generative/ocr-api/commit/4b9c17a19e9a4db32e2736ddffdb858f4a810020))
* **services:** refacto add token, classification ([3966214](https://github.com/IA-Generative/ocr-api/commit/396621402161b2a8c36613143903eaf5184d39b5))
* **TasksTab:** enhance task display with file information and improved task type labels ([4b9c17a](https://github.com/IA-Generative/ocr-api/commit/4b9c17a19e9a4db32e2736ddffdb858f4a810020))


### Bug Fixes

* **router:** extend token expiration time for presigned URLs ([4b9c17a](https://github.com/IA-Generative/ocr-api/commit/4b9c17a19e9a4db32e2736ddffdb858f4a810020))
* **security:** hash API tokens for secure storage and verification ([4b9c17a](https://github.com/IA-Generative/ocr-api/commit/4b9c17a19e9a4db32e2736ddffdb858f4a810020))

## [0.15.0](https://github.com/IA-Generative/ocr-api/compare/v0.14.4...v0.15.0) (2026-04-13)


### Features

* **AppFooter:** add footer component to display application version ([e5cabb0](https://github.com/IA-Generative/ocr-api/commit/e5cabb095dc755fc848cff5524e71e6b627555d8))

## [0.14.4](https://github.com/IA-Generative/ocr-api/compare/v0.14.3...v0.14.4) (2026-04-13)


### Bug Fixes

* **ci:** add HARBOR_PROXY_URL build argument to Docker build configurations ([6ed5d12](https://github.com/IA-Generative/ocr-api/commit/6ed5d12f695401d6dfec832d7ca491b82be97ac3))
* **TokenModal:** refactor token management to use HTTP client for API requests ([12f89df](https://github.com/IA-Generative/ocr-api/commit/12f89dfc0a653fb0d4cff3a10c1a1f0daf21eb16))
* **TokenModal:** update API endpoint to include trailing slash for token requests ([d6e6fd2](https://github.com/IA-Generative/ocr-api/commit/d6e6fd202b07bb63634b9c49a68f694307e0ec8b))

## [0.14.3](https://github.com/IA-Generative/ocr-api/compare/v0.14.2...v0.14.3) (2026-04-13)


### Bug Fixes

* **docker:** add TORCHINDUCTOR_CACHE_DIR environment variable ([#297](https://github.com/IA-Generative/ocr-api/issues/297)) ([b1b2797](https://github.com/IA-Generative/ocr-api/commit/b1b27973aaf2304cc3f715483a16ac3434f8c399))

## [0.14.2](https://github.com/IA-Generative/ocr-api/compare/v0.14.1...v0.14.2) (2026-04-13)


### Bug Fixes

* **ci:** update image tagging logic to always include branch tags ([#295](https://github.com/IA-Generative/ocr-api/issues/295)) ([5a9204c](https://github.com/IA-Generative/ocr-api/commit/5a9204c5fcc12598500578f41ec09562d11b312e))

## [0.14.1](https://github.com/IA-Generative/ocr-api/compare/v0.14.0...v0.14.1) (2026-04-13)


### Bug Fixes

* **ci:** update image tagging logic in GitLab CI configuration ([#293](https://github.com/IA-Generative/ocr-api/issues/293)) ([b6de937](https://github.com/IA-Generative/ocr-api/commit/b6de937477d8cb2fad88d6001fa42f6395f304ba))

## [0.14.0](https://github.com/IA-Generative/ocr-api/compare/v0.13.9...v0.14.0) (2026-04-13)


### Features

* :art: add auth with backend ([8d5b74c](https://github.com/IA-Generative/ocr-api/commit/8d5b74cf18eedf7b0c4f9a1c73eee71404f8d120))
* :art: add headers to api ([ca4e425](https://github.com/IA-Generative/ocr-api/commit/ca4e425fd2d9f1a134d7ce5ee5491b22643f09ba))
* :chart_with_upwards_trend: add matomo tracking ([e0cbb46](https://github.com/IA-Generative/ocr-api/commit/e0cbb46d1487386dbca7ff3b35b7aa094a389fa6))
* :sparkles: add husky, pre-commit and commitlint ([5b77743](https://github.com/IA-Generative/ocr-api/commit/5b77743f85c7d229d33360347556121c213aef6b))
* :sparkles: update environment variables and improve sidebar links ([4a3f1e6](https://github.com/IA-Generative/ocr-api/commit/4a3f1e67158313ef84c757e05cb85ab68d95666f))
* add all text from pdf ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* add configs directory copy to Dockerfile ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* add delete routers ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* add docling process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add document extraction support for multiple file formats ([026088c](https://github.com/IA-Generative/ocr-api/commit/026088cab3efb9cd2719fbb4039d70812e551612))
* add example curl commands for OCR API usage ([c3cc714](https://github.com/IA-Generative/ocr-api/commit/c3cc714a6e94f5b0deb42aeb0d1e88ec7633da1a))
* add Keycloak configuration details and OpenAI API variables to documentation ([ff217ac](https://github.com/IA-Generative/ocr-api/commit/ff217ac84f988c7da8e3193f5675f1eb5180150e))
* add ocr-docling group to Dockerfile build process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add OPENAI_API_KEY to environment configuration ([95de513](https://github.com/IA-Generative/ocr-api/commit/95de5131a084d84f35d1287df07fd518b2a659bc))
* add parameters column to tasks and update migration script ([a1f092a](https://github.com/IA-Generative/ocr-api/commit/a1f092ae75ae27dd3fe92e1f65e680f22f8feec9))
* add PDF forms extraction worker and related tests ([d1392d9](https://github.com/IA-Generative/ocr-api/commit/d1392d9f2bdd605f01d6e966a390575d4a0b46d4))
* add process router for document processing and related tests ([9f2473e](https://github.com/IA-Generative/ocr-api/commit/9f2473e8156fbafcc8d606f056b1acf199ae22bf))
* add purge script for task deletion with Keycloak authentication ([b9197ca](https://github.com/IA-Generative/ocr-api/commit/b9197ca4192ecfe671f73d1bcd18d03682bce948))
* add set_page_text method to OCRResult for page text extraction ([3522ca4](https://github.com/IA-Generative/ocr-api/commit/3522ca4f3b849f5d0904d353c9bc320870146b2c))
* add test.csv file for validation in tests/data/valid ([69cfc75](https://github.com/IA-Generative/ocr-api/commit/69cfc755e6a7a84ffd45988f589503b466b7ee4a))
* add workflow for testing services related to forms ([d5647b9](https://github.com/IA-Generative/ocr-api/commit/d5647b98afe4cec88e80c95275c071fc1cae12b9))
* **annotation:** feat(annotation):  ([14d2446](https://github.com/IA-Generative/ocr-api/commit/14d244614e23ede5c91213addc9a88e4d0c300fa))
* **api:** enhance API key handling and validation in ApiToken class ([#265](https://github.com/IA-Generative/ocr-api/issues/265)) ([59531d8](https://github.com/IA-Generative/ocr-api/commit/59531d87b54a2b9ed2883c7610276a147a915579))
* **docker:** add PaddleOCR model download script and update Dockerfile ([#264](https://github.com/IA-Generative/ocr-api/issues/264)) ([1e179f2](https://github.com/IA-Generative/ocr-api/commit/1e179f28843c73a32475be635b99abc44a748cf3))
* **docs:** add Langfuse tracing configuration variables ([88ee3b5](https://github.com/IA-Generative/ocr-api/commit/88ee3b5172da4e43a3f8459c8d12542af8bf4d85))
* enhance Keycloak token verification and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* enhance task management with admin checks and update request context ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* extract text and bounding boxes from PDF pages for improved data processing ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* implement centralized logging configuration system ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* integrate Keycloak authentication and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* integrate Keycloak for authentication and user management ([521a930](https://github.com/IA-Generative/ocr-api/commit/521a930719010e44b6ae39b4c4e5fb6d48a0354a))
* merge staging to preprod ([#144](https://github.com/IA-Generative/ocr-api/issues/144)) ([59cb5a8](https://github.com/IA-Generative/ocr-api/commit/59cb5a89691b75fa200af457c59b1b7e2896b5fc))
* **new:** add annotation view ([#251](https://github.com/IA-Generative/ocr-api/issues/251)) ([f8d5b9e](https://github.com/IA-Generative/ocr-api/commit/f8d5b9e7aa637c85b73a4a1924e8bfc89b16a8d0))
* refactor PDF form extraction, add vector and template management, and improve feature extraction ([cda4e3d](https://github.com/IA-Generative/ocr-api/commit/cda4e3d73c515ce5a0f20827c4d61fd59ecc3808))
* **security:** improve Keycloak token verification, logging, and documentation ([15c3b87](https://github.com/IA-Generative/ocr-api/commit/15c3b871a5d4ef77d339e1f3f0bf6555a8de1de8))
* update environment variables and refactor job and task routers for improved functionality ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))


### Bug Fixes

* :label: fix error types ts ([c3d1a13](https://github.com/IA-Generative/ocr-api/commit/c3d1a1377f0899cccb8696499abd3c4addcbebce))
* :passport_control: fixing keycloak infinity loop on sign in ([0bc8db0](https://github.com/IA-Generative/ocr-api/commit/0bc8db07a79b770b2e765fa607f4d5f240493217))
* :rocket: don't open twice file ([1ae8f31](https://github.com/IA-Generative/ocr-api/commit/1ae8f31ff1d34e822d07795411af3564bf688c3d))
* :white_check_mark: fix ocr e2e test ([f225d2f](https://github.com/IA-Generative/ocr-api/commit/f225d2f2e7fdbe5ac28b99fe34542c5d13d546e7))
* add clearToken when keycloak logout ([1fabd51](https://github.com/IA-Generative/ocr-api/commit/1fabd51be72115d858eb204512adacbf92e4340b))
* add docling_inference directory to Dockerfile ([3707056](https://github.com/IA-Generative/ocr-api/commit/37070567d0ad9f5aa77fe3d1b955b3c9df102a1d))
* add missing extraction files to Dockerfile ([0f3be43](https://github.com/IA-Generative/ocr-api/commit/0f3be43371cc68e2759d7b8ba70ab5661d365164))
* add missing version and tag_name outputs to release workflow ([9f69eeb](https://github.com/IA-Generative/ocr-api/commit/9f69eeb00da51d0beda9e90bfac4173983f7a5fe))
* add more log using user_id ([9b310c9](https://github.com/IA-Generative/ocr-api/commit/9b310c9a25ad8fdc73e15ffff17e3a3c82e5adb5))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* **ci:** guard release-please against force-pushes and invalid branch dispatches ([#281](https://github.com/IA-Generative/ocr-api/issues/281)) ([2bf0317](https://github.com/IA-Generative/ocr-api/commit/2bf031762778929f8a9d56f1fca69a051d8126ed))
* **ci:** set lowercase registry prefix for Docker image tags ([#283](https://github.com/IA-Generative/ocr-api/issues/283)) ([7aa2b85](https://github.com/IA-Generative/ocr-api/commit/7aa2b850a46462846ec253c378e7e4e26fb81ca1))
* **ci:** update Docker build rules for ocr-api, ocr-worker, and ocr-f… ([#287](https://github.com/IA-Generative/ocr-api/issues/287)) ([a2d567e](https://github.com/IA-Generative/ocr-api/commit/a2d567eddd05336d38f33398685595078050c4ee))
* **ci:** update image names to include tags for Docker builds ([#278](https://github.com/IA-Generative/ocr-api/issues/278)) ([#280](https://github.com/IA-Generative/ocr-api/issues/280)) ([5219460](https://github.com/IA-Generative/ocr-api/commit/52194609812107d52e51ebeebd2c3ed3574aabf2))
* correct attribut href to in DsfrTile component ([43f670a](https://github.com/IA-Generative/ocr-api/commit/43f670a4171cbc6fe67a37bd00b87bda0ed97a6c))
* delete role in headers (not necessary) ([098d6a6](https://github.com/IA-Generative/ocr-api/commit/098d6a68f8ff74f0a3ff607f1e7c26b371395265))
* **docker:** include chunks directory in Dockerfile ([#276](https://github.com/IA-Generative/ocr-api/issues/276)) ([dfd54b8](https://github.com/IA-Generative/ocr-api/commit/dfd54b865708c3636e707033b38890ba40e56468))
* enable SSL verification for S3 client and improve code formatting ([#254](https://github.com/IA-Generative/ocr-api/issues/254)) ([33d197f](https://github.com/IA-Generative/ocr-api/commit/33d197f8fa8590a8de6c53fb1a8b68809e8bb7d0))
* ensure task output pages are cleared for non-completed tasks and format delete function parameters ([edb41af](https://github.com/IA-Generative/ocr-api/commit/edb41afa9e0f4dd8b2117909cc168fa5b6a586a6))
* fix keycloak client id ([c5e932e](https://github.com/IA-Generative/ocr-api/commit/c5e932ea1e662d624c6816a6113e090f9660b209))
* hot fix lock ([2e93413](https://github.com/IA-Generative/ocr-api/commit/2e93413ed1802fa711a78a549b36d522fe013273))
* improve code formatting and structure in token verification classes ([#259](https://github.com/IA-Generative/ocr-api/issues/259)) ([d85cc55](https://github.com/IA-Generative/ocr-api/commit/d85cc55a591ffc6d36d4d172b5c7272de18dbd03))
* improve logging format and enhance trace context in launch_task ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* mettre à jour les chemins des liens dans la barre latérale ([78c54ea](https://github.com/IA-Generative/ocr-api/commit/78c54eaa3c94d030cb73deef41588911173b45a6))
* mettre à jour les liens des conditions d'utilisation et de la FAQ dans la barre latérale ([88e73de](https://github.com/IA-Generative/ocr-api/commit/88e73decd3986bb9dedbfe8c49cccc1368876300))
* Refactor batch_predict method to improve handling of predictions and ensure non-null checks for better stability ([#55](https://github.com/IA-Generative/ocr-api/issues/55)) ([2ffdcfc](https://github.com/IA-Generative/ocr-api/commit/2ffdcfc07f2ff12b2cb399066e28a05bbd385de8))
* **release:** remove unnecessary blank line in release workflow ([#291](https://github.com/IA-Generative/ocr-api/issues/291)) ([a71fd77](https://github.com/IA-Generative/ocr-api/commit/a71fd777e61f7c71dace05b0e661b24764d4e204))
* **release:** unify release ([#246](https://github.com/IA-Generative/ocr-api/issues/246)) ([80c044c](https://github.com/IA-Generative/ocr-api/commit/80c044c545ffc92ef25df156aed7ff5645a19adb))
* **release:** update image version deletion logic in GitHub Actions w… ([#289](https://github.com/IA-Generative/ocr-api/issues/289)) ([29bf3e1](https://github.com/IA-Generative/ocr-api/commit/29bf3e1e22278d11f3b08c200b96b8ca259c755d))
* remove docling from dependencies and add ocr-docling group ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* remove unused 'tags' parameter from LangFuseTracingService ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* **server:** url presigned and prossion text ([#274](https://github.com/IA-Generative/ocr-api/issues/274)) ([f27d75e](https://github.com/IA-Generative/ocr-api/commit/f27d75e344230b2068549c38876f6ffbdaed05c5))
* simplify metadata handling in LangFuseTracingService ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* **tests:** unitttest and model folder ([#270](https://github.com/IA-Generative/ocr-api/issues/270)) ([8defbfa](https://github.com/IA-Generative/ocr-api/commit/8defbfa1faa2c203cd0f3137d7dcb0acce1fbfd3))
* **token:** add token approach ([80e0aeb](https://github.com/IA-Generative/ocr-api/commit/80e0aeb7c325bd59dc8aea99501c7e1d563995ca))
* update apps/client/src/api/http-client.ts ([7012539](https://github.com/IA-Generative/ocr-api/commit/70125395a3408a92004ab257e178714f9d53f020))
* update apps/client/src/api/http-client.ts ([2d0704f](https://github.com/IA-Generative/ocr-api/commit/2d0704f6d0f7815c4e0a501990aa9ba80701b5eb))
* update apps/client/src/api/http-client.ts ([453edc0](https://github.com/IA-Generative/ocr-api/commit/453edc0c6203c9bfee29402161a96409e9b2f377))
* update apps/client/src/utils/keycloak.ts ([9bca0e0](https://github.com/IA-Generative/ocr-api/commit/9bca0e03a7c67386a9a1e87c17716943310ab5dc))
* update apps/client/src/utils/keycloak.ts ([cdfb2f9](https://github.com/IA-Generative/ocr-api/commit/cdfb2f9c1b9443ae4aff82e9c45e4397453d1574))
* update apps/client/src/utils/keycloak.ts ([12b3614](https://github.com/IA-Generative/ocr-api/commit/12b3614a3bb2aef2669ca0bebde8d43d8b20092d))
* update apps/client/src/utils/keycloak.ts ([655e2ee](https://github.com/IA-Generative/ocr-api/commit/655e2eeda630b3d6fce788d6c8f06a217c154915))
* update apps/client/src/utils/keycloak.ts ([cb674a4](https://github.com/IA-Generative/ocr-api/commit/cb674a44d5cc705345242179cc5d66b40620004b))
* update apps/client/src/utils/keycloak.ts ([cb0a6c0](https://github.com/IA-Generative/ocr-api/commit/cb0a6c096f9b1736ebf4f9aa10b978e3c1c11a04))
* update apps/client/src/utils/keycloak.ts ([0a5e16b](https://github.com/IA-Generative/ocr-api/commit/0a5e16bd52602d0618e1882cdd2e0619b45dcedd))
* update default task operation to use DEFAULT value in upload_file function ([e5b8162](https://github.com/IA-Generative/ocr-api/commit/e5b8162ea60664dad5e3b774d3d145bff6bec1f3))
* update environment variables and adjust frontend port in docker-compose ([#272](https://github.com/IA-Generative/ocr-api/issues/272)) ([3e88d8d](https://github.com/IA-Generative/ocr-api/commit/3e88d8d430daea725954eb6dc44d170122fe00a5))
* update maxfail option in test commands to allow all tests to run ([00616f0](https://github.com/IA-Generative/ocr-api/commit/00616f004ae19bee5a587ed5fd71c963091f79b4))
* update package name in release-please manifest ([2786f37](https://github.com/IA-Generative/ocr-api/commit/2786f37b1ecd64607f0f34b579a56d28aecdaf4e))
* update package names and include-component-in-tag settings in re… ([#238](https://github.com/IA-Generative/ocr-api/issues/238)) ([e41e106](https://github.com/IA-Generative/ocr-api/commit/e41e10695e4839e525cd5afccc1f675032a1c21e))
* update PaddleOCR base directory path in Dockerfile ([#261](https://github.com/IA-Generative/ocr-api/issues/261)) ([b9e6d8c](https://github.com/IA-Generative/ocr-api/commit/b9e6d8cde4aab7b0c600ad28e65ce4346eaf622b))
* update PaddleOCR model version to PP-OCRv3 in Dockerfile ([#257](https://github.com/IA-Generative/ocr-api/issues/257)) ([b219897](https://github.com/IA-Generative/ocr-api/commit/b219897978a7a67c0147740ac9357fd032741a21))
* update release workflow to correct manifest and config file paths ([93de8cc](https://github.com/IA-Generative/ocr-api/commit/93de8cc4636c41e568bec0a069972c37dc020388))
* update SDK test cases and improve Makefile for testing ([#242](https://github.com/IA-Generative/ocr-api/issues/242)) ([e00afd8](https://github.com/IA-Generative/ocr-api/commit/e00afd832068a76b072ddc3cb9a363a9a92a31b9))
* use resource_access and client_id to get roles ([d22ac16](https://github.com/IA-Generative/ocr-api/commit/d22ac162de5acddd0700e8c45482c56bb9b0cb3c))

## [0.13.9](https://github.com/IA-Generative/ocr-api/compare/v0.13.8...v0.13.9) (2026-04-13)


### Bug Fixes

* **release:** update image version deletion logic in GitHub Actions w… ([#289](https://github.com/IA-Generative/ocr-api/issues/289)) ([29bf3e1](https://github.com/IA-Generative/ocr-api/commit/29bf3e1e22278d11f3b08c200b96b8ca259c755d))

## [0.13.8](https://github.com/IA-Generative/ocr-api/compare/v0.13.7...v0.13.8) (2026-04-13)


### Bug Fixes

* **ci:** update Docker build rules for ocr-api, ocr-worker, and ocr-f… ([#287](https://github.com/IA-Generative/ocr-api/issues/287)) ([a2d567e](https://github.com/IA-Generative/ocr-api/commit/a2d567eddd05336d38f33398685595078050c4ee))

## [0.13.7](https://github.com/IA-Generative/ocr-api/compare/v0.13.6...v0.13.7) (2026-04-11)


### Bug Fixes

* **token:** add token approach ([80e0aeb](https://github.com/IA-Generative/ocr-api/commit/80e0aeb7c325bd59dc8aea99501c7e1d563995ca))

## [0.13.6](https://github.com/IA-Generative/ocr-api/compare/v0.13.5...v0.13.6) (2026-04-10)


### Bug Fixes

* **ci:** set lowercase registry prefix for Docker image tags ([#283](https://github.com/IA-Generative/ocr-api/issues/283)) ([7aa2b85](https://github.com/IA-Generative/ocr-api/commit/7aa2b850a46462846ec253c378e7e4e26fb81ca1))

## [0.13.5](https://github.com/IA-Generative/ocr-api/compare/v0.13.4...v0.13.5) (2026-04-10)


### Bug Fixes

* **ci:** guard release-please against force-pushes and invalid branch dispatches ([#281](https://github.com/IA-Generative/ocr-api/issues/281)) ([2bf0317](https://github.com/IA-Generative/ocr-api/commit/2bf031762778929f8a9d56f1fca69a051d8126ed))
* **ci:** update image names to include tags for Docker builds ([#278](https://github.com/IA-Generative/ocr-api/issues/278)) ([#280](https://github.com/IA-Generative/ocr-api/issues/280)) ([5219460](https://github.com/IA-Generative/ocr-api/commit/52194609812107d52e51ebeebd2c3ed3574aabf2))

## [0.13.4](https://github.com/IA-Generative/ocr-api/compare/v0.13.3...v0.13.4) (2026-04-09)


### Bug Fixes

* **docker:** include chunks directory in Dockerfile ([#276](https://github.com/IA-Generative/ocr-api/issues/276)) ([dfd54b8](https://github.com/IA-Generative/ocr-api/commit/dfd54b865708c3636e707033b38890ba40e56468))

## [0.13.3](https://github.com/IA-Generative/ocr-api/compare/v0.13.2...v0.13.3) (2026-04-09)


### Bug Fixes

* **server:** url presigned and prossion text ([#274](https://github.com/IA-Generative/ocr-api/issues/274)) ([f27d75e](https://github.com/IA-Generative/ocr-api/commit/f27d75e344230b2068549c38876f6ffbdaed05c5))

## [0.13.2](https://github.com/IA-Generative/ocr-api/compare/v0.13.1...v0.13.2) (2026-04-08)


### Bug Fixes

* update environment variables and adjust frontend port in docker-compose ([#272](https://github.com/IA-Generative/ocr-api/issues/272)) ([3e88d8d](https://github.com/IA-Generative/ocr-api/commit/3e88d8d430daea725954eb6dc44d170122fe00a5))

## [0.13.1](https://github.com/IA-Generative/ocr-api/compare/v0.13.0...v0.13.1) (2026-04-08)


### Bug Fixes

* **tests:** unitttest and model folder ([#270](https://github.com/IA-Generative/ocr-api/issues/270)) ([8defbfa](https://github.com/IA-Generative/ocr-api/commit/8defbfa1faa2c203cd0f3137d7dcb0acce1fbfd3))

## [0.13.0](https://github.com/IA-Generative/ocr-api/compare/v0.12.0...v0.13.0) (2026-04-08)


### Features

* **api:** enhance API key handling and validation in ApiToken class ([#265](https://github.com/IA-Generative/ocr-api/issues/265)) ([59531d8](https://github.com/IA-Generative/ocr-api/commit/59531d87b54a2b9ed2883c7610276a147a915579))

## [0.12.0](https://github.com/IA-Generative/ocr-api/compare/v0.11.0...v0.12.0) (2026-04-08)


### Features

* **docker:** add PaddleOCR model download script and update Dockerfile ([#264](https://github.com/IA-Generative/ocr-api/issues/264)) ([1e179f2](https://github.com/IA-Generative/ocr-api/commit/1e179f28843c73a32475be635b99abc44a748cf3))

## [0.11.0](https://github.com/IA-Generative/ocr-api/compare/v0.10.4...v0.11.0) (2026-04-08)


### Features

* **annotation:** feat(annotation):  ([14d2446](https://github.com/IA-Generative/ocr-api/commit/14d244614e23ede5c91213addc9a88e4d0c300fa))
* **new:** add annotation view ([#251](https://github.com/IA-Generative/ocr-api/issues/251)) ([f8d5b9e](https://github.com/IA-Generative/ocr-api/commit/f8d5b9e7aa637c85b73a4a1924e8bfc89b16a8d0))

## [0.10.4](https://github.com/IA-Generative/ocr-api/compare/v0.10.3...v0.10.4) (2026-04-07)


### Bug Fixes

* update PaddleOCR base directory path in Dockerfile ([#261](https://github.com/IA-Generative/ocr-api/issues/261)) ([b9e6d8c](https://github.com/IA-Generative/ocr-api/commit/b9e6d8cde4aab7b0c600ad28e65ce4346eaf622b))

## [0.10.3](https://github.com/IA-Generative/ocr-api/compare/v0.10.2...v0.10.3) (2026-04-07)


### Bug Fixes

* improve code formatting and structure in token verification classes ([#259](https://github.com/IA-Generative/ocr-api/issues/259)) ([d85cc55](https://github.com/IA-Generative/ocr-api/commit/d85cc55a591ffc6d36d4d172b5c7272de18dbd03))

## [0.10.2](https://github.com/IA-Generative/ocr-api/compare/v0.10.1...v0.10.2) (2026-04-07)


### Bug Fixes

* update PaddleOCR model version to PP-OCRv3 in Dockerfile ([#257](https://github.com/IA-Generative/ocr-api/issues/257)) ([b219897](https://github.com/IA-Generative/ocr-api/commit/b219897978a7a67c0147740ac9357fd032741a21))

## [0.10.1](https://github.com/IA-Generative/ocr-api/compare/v0.10.0...v0.10.1) (2026-04-07)


### Bug Fixes

* enable SSL verification for S3 client and improve code formatting ([#254](https://github.com/IA-Generative/ocr-api/issues/254)) ([33d197f](https://github.com/IA-Generative/ocr-api/commit/33d197f8fa8590a8de6c53fb1a8b68809e8bb7d0))

## [0.10.0](https://github.com/IA-Generative/ocr-api/compare/v0.9.0...v0.10.0) (2026-03-05)


### Features

* add OPENAI_API_KEY to environment configuration ([95de513](https://github.com/IA-Generative/ocr-api/commit/95de5131a084d84f35d1287df07fd518b2a659bc))


### Bug Fixes

* add missing version and tag_name outputs to release workflow ([9f69eeb](https://github.com/IA-Generative/ocr-api/commit/9f69eeb00da51d0beda9e90bfac4173983f7a5fe))
* **release:** unify release ([#246](https://github.com/IA-Generative/ocr-api/issues/246)) ([80c044c](https://github.com/IA-Generative/ocr-api/commit/80c044c545ffc92ef25df156aed7ff5645a19adb))
* update SDK test cases and improve Makefile for testing ([#242](https://github.com/IA-Generative/ocr-api/issues/242)) ([e00afd8](https://github.com/IA-Generative/ocr-api/commit/e00afd832068a76b072ddc3cb9a363a9a92a31b9))

## [0.9.0](https://github.com/IA-Generative/ocr-api/compare/v0.8.4...v0.9.0) (2026-02-17)


### Features

* add OPENAI_API_KEY to environment configuration ([95de513](https://github.com/IA-Generative/ocr-api/commit/95de5131a084d84f35d1287df07fd518b2a659bc))


### Bug Fixes

* add missing version and tag_name outputs to release workflow ([9f69eeb](https://github.com/IA-Generative/ocr-api/commit/9f69eeb00da51d0beda9e90bfac4173983f7a5fe))

## [0.8.4](https://github.com/IA-Generative/ocr-api/compare/v0.8.3...v0.8.4) (2026-02-16)


### Bug Fixes

* update SDK test cases and improve Makefile for testing ([#242](https://github.com/IA-Generative/ocr-api/issues/242)) ([e00afd8](https://github.com/IA-Generative/ocr-api/commit/e00afd832068a76b072ddc3cb9a363a9a92a31b9))

## [0.8.3](https://github.com/IA-Generative/ocr-api/compare/v0.8.2...v0.8.3) (2026-02-16)


### Bug Fixes

* update package names and include-component-in-tag settings in re… ([#238](https://github.com/IA-Generative/ocr-api/issues/238)) ([e41e106](https://github.com/IA-Generative/ocr-api/commit/e41e10695e4839e525cd5afccc1f675032a1c21e))

## [0.8.2](https://github.com/IA-Generative/ocr-api/compare/v0.8.1...v0.8.2) (2025-11-21)


### Bug Fixes

* add missing extraction files to Dockerfile ([0f3be43](https://github.com/IA-Generative/ocr-api/commit/0f3be43371cc68e2759d7b8ba70ab5661d365164))
* update package name in release-please manifest ([2786f37](https://github.com/IA-Generative/ocr-api/commit/2786f37b1ecd64607f0f34b579a56d28aecdaf4e))

## [0.8.1](https://github.com/IA-Generative/ocr-api/compare/v0.8.0...v0.8.1) (2025-10-27)


### Bug Fixes

* mettre à jour les chemins des liens dans la barre latérale ([78c54ea](https://github.com/IA-Generative/ocr-api/commit/78c54eaa3c94d030cb73deef41588911173b45a6))
* mettre à jour les liens des conditions d'utilisation et de la FAQ dans la barre latérale ([88e73de](https://github.com/IA-Generative/ocr-api/commit/88e73decd3986bb9dedbfe8c49cccc1368876300))

## [0.8.0](https://github.com/IA-Generative/ocr-api/compare/v0.7.0...v0.8.0) (2025-10-25)


### Features

* add document extraction support for multiple file formats ([026088c](https://github.com/IA-Generative/ocr-api/commit/026088cab3efb9cd2719fbb4039d70812e551612))
* add process router for document processing and related tests ([9f2473e](https://github.com/IA-Generative/ocr-api/commit/9f2473e8156fbafcc8d606f056b1acf199ae22bf))
* add set_page_text method to OCRResult for page text extraction ([3522ca4](https://github.com/IA-Generative/ocr-api/commit/3522ca4f3b849f5d0904d353c9bc320870146b2c))
* add test.csv file for validation in tests/data/valid ([69cfc75](https://github.com/IA-Generative/ocr-api/commit/69cfc755e6a7a84ffd45988f589503b466b7ee4a))

## [0.7.0](https://github.com/IA-Generative/ocr-api/compare/v0.6.0...v0.7.0) (2025-10-01)


### Features

* :art: add auth with backend ([8d5b74c](https://github.com/IA-Generative/ocr-api/commit/8d5b74cf18eedf7b0c4f9a1c73eee71404f8d120))
* :art: add headers to api ([ca4e425](https://github.com/IA-Generative/ocr-api/commit/ca4e425fd2d9f1a134d7ce5ee5491b22643f09ba))
* :chart_with_upwards_trend: add matomo tracking ([e0cbb46](https://github.com/IA-Generative/ocr-api/commit/e0cbb46d1487386dbca7ff3b35b7aa094a389fa6))
* :sparkles: add husky, pre-commit and commitlint ([5b77743](https://github.com/IA-Generative/ocr-api/commit/5b77743f85c7d229d33360347556121c213aef6b))
* :sparkles: update environment variables and improve sidebar links ([4a3f1e6](https://github.com/IA-Generative/ocr-api/commit/4a3f1e67158313ef84c757e05cb85ab68d95666f))
* add all text from pdf ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* add configs directory copy to Dockerfile ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* add delete routers ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* add docling process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add example curl commands for OCR API usage ([c3cc714](https://github.com/IA-Generative/ocr-api/commit/c3cc714a6e94f5b0deb42aeb0d1e88ec7633da1a))
* add Keycloak configuration details and OpenAI API variables to documentation ([ff217ac](https://github.com/IA-Generative/ocr-api/commit/ff217ac84f988c7da8e3193f5675f1eb5180150e))
* add ocr-docling group to Dockerfile build process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add parameters column to tasks and update migration script ([a1f092a](https://github.com/IA-Generative/ocr-api/commit/a1f092ae75ae27dd3fe92e1f65e680f22f8feec9))
* add PDF forms extraction worker and related tests ([d1392d9](https://github.com/IA-Generative/ocr-api/commit/d1392d9f2bdd605f01d6e966a390575d4a0b46d4))
* add purge script for task deletion with Keycloak authentication ([b9197ca](https://github.com/IA-Generative/ocr-api/commit/b9197ca4192ecfe671f73d1bcd18d03682bce948))
* add workflow for testing services related to forms ([d5647b9](https://github.com/IA-Generative/ocr-api/commit/d5647b98afe4cec88e80c95275c071fc1cae12b9))
* **docs:** add Langfuse tracing configuration variables ([88ee3b5](https://github.com/IA-Generative/ocr-api/commit/88ee3b5172da4e43a3f8459c8d12542af8bf4d85))
* enhance Keycloak token verification and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* enhance task management with admin checks and update request context ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* extract text and bounding boxes from PDF pages for improved data processing ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* implement centralized logging configuration system ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* integrate Keycloak authentication and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* integrate Keycloak for authentication and user management ([521a930](https://github.com/IA-Generative/ocr-api/commit/521a930719010e44b6ae39b4c4e5fb6d48a0354a))
* merge staging to preprod ([#144](https://github.com/IA-Generative/ocr-api/issues/144)) ([59cb5a8](https://github.com/IA-Generative/ocr-api/commit/59cb5a89691b75fa200af457c59b1b7e2896b5fc))
* refactor PDF form extraction, add vector and template management, and improve feature extraction ([cda4e3d](https://github.com/IA-Generative/ocr-api/commit/cda4e3d73c515ce5a0f20827c4d61fd59ecc3808))
* **security:** improve Keycloak token verification, logging, and documentation ([15c3b87](https://github.com/IA-Generative/ocr-api/commit/15c3b871a5d4ef77d339e1f3f0bf6555a8de1de8))
* update environment variables and refactor job and task routers for improved functionality ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))


### Bug Fixes

* :label: fix error types ts ([c3d1a13](https://github.com/IA-Generative/ocr-api/commit/c3d1a1377f0899cccb8696499abd3c4addcbebce))
* :passport_control: fixing keycloak infinity loop on sign in ([0bc8db0](https://github.com/IA-Generative/ocr-api/commit/0bc8db07a79b770b2e765fa607f4d5f240493217))
* :rocket: don't open twice file ([1ae8f31](https://github.com/IA-Generative/ocr-api/commit/1ae8f31ff1d34e822d07795411af3564bf688c3d))
* :white_check_mark: fix ocr e2e test ([f225d2f](https://github.com/IA-Generative/ocr-api/commit/f225d2f2e7fdbe5ac28b99fe34542c5d13d546e7))
* add clearToken when keycloak logout ([1fabd51](https://github.com/IA-Generative/ocr-api/commit/1fabd51be72115d858eb204512adacbf92e4340b))
* add docling_inference directory to Dockerfile ([3707056](https://github.com/IA-Generative/ocr-api/commit/37070567d0ad9f5aa77fe3d1b955b3c9df102a1d))
* add more log using user_id ([9b310c9](https://github.com/IA-Generative/ocr-api/commit/9b310c9a25ad8fdc73e15ffff17e3a3c82e5adb5))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* correct attribut href to in DsfrTile component ([43f670a](https://github.com/IA-Generative/ocr-api/commit/43f670a4171cbc6fe67a37bd00b87bda0ed97a6c))
* delete role in headers (not necessary) ([098d6a6](https://github.com/IA-Generative/ocr-api/commit/098d6a68f8ff74f0a3ff607f1e7c26b371395265))
* ensure task output pages are cleared for non-completed tasks and format delete function parameters ([edb41af](https://github.com/IA-Generative/ocr-api/commit/edb41afa9e0f4dd8b2117909cc168fa5b6a586a6))
* fix keycloak client id ([c5e932e](https://github.com/IA-Generative/ocr-api/commit/c5e932ea1e662d624c6816a6113e090f9660b209))
* hot fix lock ([2e93413](https://github.com/IA-Generative/ocr-api/commit/2e93413ed1802fa711a78a549b36d522fe013273))
* improve logging format and enhance trace context in launch_task ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* Refactor batch_predict method to improve handling of predictions and ensure non-null checks for better stability ([#55](https://github.com/IA-Generative/ocr-api/issues/55)) ([2ffdcfc](https://github.com/IA-Generative/ocr-api/commit/2ffdcfc07f2ff12b2cb399066e28a05bbd385de8))
* remove docling from dependencies and add ocr-docling group ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* remove unused 'tags' parameter from LangFuseTracingService ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* simplify metadata handling in LangFuseTracingService ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* update apps/client/src/api/http-client.ts ([7012539](https://github.com/IA-Generative/ocr-api/commit/70125395a3408a92004ab257e178714f9d53f020))
* update apps/client/src/api/http-client.ts ([2d0704f](https://github.com/IA-Generative/ocr-api/commit/2d0704f6d0f7815c4e0a501990aa9ba80701b5eb))
* update apps/client/src/api/http-client.ts ([453edc0](https://github.com/IA-Generative/ocr-api/commit/453edc0c6203c9bfee29402161a96409e9b2f377))
* update apps/client/src/utils/keycloak.ts ([9bca0e0](https://github.com/IA-Generative/ocr-api/commit/9bca0e03a7c67386a9a1e87c17716943310ab5dc))
* update apps/client/src/utils/keycloak.ts ([cdfb2f9](https://github.com/IA-Generative/ocr-api/commit/cdfb2f9c1b9443ae4aff82e9c45e4397453d1574))
* update apps/client/src/utils/keycloak.ts ([12b3614](https://github.com/IA-Generative/ocr-api/commit/12b3614a3bb2aef2669ca0bebde8d43d8b20092d))
* update apps/client/src/utils/keycloak.ts ([655e2ee](https://github.com/IA-Generative/ocr-api/commit/655e2eeda630b3d6fce788d6c8f06a217c154915))
* update apps/client/src/utils/keycloak.ts ([cb674a4](https://github.com/IA-Generative/ocr-api/commit/cb674a44d5cc705345242179cc5d66b40620004b))
* update apps/client/src/utils/keycloak.ts ([cb0a6c0](https://github.com/IA-Generative/ocr-api/commit/cb0a6c096f9b1736ebf4f9aa10b978e3c1c11a04))
* update apps/client/src/utils/keycloak.ts ([0a5e16b](https://github.com/IA-Generative/ocr-api/commit/0a5e16bd52602d0618e1882cdd2e0619b45dcedd))
* update default task operation to use DEFAULT value in upload_file function ([e5b8162](https://github.com/IA-Generative/ocr-api/commit/e5b8162ea60664dad5e3b774d3d145bff6bec1f3))
* update maxfail option in test commands to allow all tests to run ([00616f0](https://github.com/IA-Generative/ocr-api/commit/00616f004ae19bee5a587ed5fd71c963091f79b4))
* update release workflow to correct manifest and config file paths ([93de8cc](https://github.com/IA-Generative/ocr-api/commit/93de8cc4636c41e568bec0a069972c37dc020388))
* use resource_access and client_id to get roles ([d22ac16](https://github.com/IA-Generative/ocr-api/commit/d22ac162de5acddd0700e8c45482c56bb9b0cb3c))

## [0.6.0](https://github.com/IA-Generative/ocr-api/compare/v0.5.0...v0.6.0) (2025-10-01)


### Features

* add purge script for task deletion with Keycloak authentication ([68b5ebb](https://github.com/IA-Generative/ocr-api/commit/68b5ebbfd960cc4e933a11a5aa3d0a8a8707f0e5))


### Bug Fixes

* use resource_access and client_id to get roles ([c1a26d7](https://github.com/IA-Generative/ocr-api/commit/c1a26d70274b5c5fd85d916c184cfb232594cd73))

## [0.5.0](https://github.com/IA-Generative/ocr-api/compare/v0.4.0...v0.5.0) (2025-09-29)


### Features

* :art: add auth with backend ([8d5b74c](https://github.com/IA-Generative/ocr-api/commit/8d5b74cf18eedf7b0c4f9a1c73eee71404f8d120))
* :art: add headers to api ([ca4e425](https://github.com/IA-Generative/ocr-api/commit/ca4e425fd2d9f1a134d7ce5ee5491b22643f09ba))
* :chart_with_upwards_trend: add matomo tracking ([e0cbb46](https://github.com/IA-Generative/ocr-api/commit/e0cbb46d1487386dbca7ff3b35b7aa094a389fa6))
* :sparkles: add husky, pre-commit and commitlint ([5b77743](https://github.com/IA-Generative/ocr-api/commit/5b77743f85c7d229d33360347556121c213aef6b))
* :sparkles: update environment variables and improve sidebar links ([4a3f1e6](https://github.com/IA-Generative/ocr-api/commit/4a3f1e67158313ef84c757e05cb85ab68d95666f))
* add all text from pdf ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* add configs directory copy to Dockerfile ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* add delete routers ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* add docling process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add example curl commands for OCR API usage ([c3cc714](https://github.com/IA-Generative/ocr-api/commit/c3cc714a6e94f5b0deb42aeb0d1e88ec7633da1a))
* add Keycloak configuration details and OpenAI API variables to documentation ([ff217ac](https://github.com/IA-Generative/ocr-api/commit/ff217ac84f988c7da8e3193f5675f1eb5180150e))
* add ocr-docling group to Dockerfile build process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add parameters column to tasks and update migration script ([a1f092a](https://github.com/IA-Generative/ocr-api/commit/a1f092ae75ae27dd3fe92e1f65e680f22f8feec9))
* add PDF forms extraction worker and related tests ([d1392d9](https://github.com/IA-Generative/ocr-api/commit/d1392d9f2bdd605f01d6e966a390575d4a0b46d4))
* add workflow for testing services related to forms ([d5647b9](https://github.com/IA-Generative/ocr-api/commit/d5647b98afe4cec88e80c95275c071fc1cae12b9))
* **docs:** add Langfuse tracing configuration variables ([88ee3b5](https://github.com/IA-Generative/ocr-api/commit/88ee3b5172da4e43a3f8459c8d12542af8bf4d85))
* enhance Keycloak token verification and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* enhance task management with admin checks and update request context ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* extract text and bounding boxes from PDF pages for improved data processing ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* implement centralized logging configuration system ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* integrate Keycloak authentication and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* integrate Keycloak for authentication and user management ([521a930](https://github.com/IA-Generative/ocr-api/commit/521a930719010e44b6ae39b4c4e5fb6d48a0354a))
* merge staging to preprod ([#144](https://github.com/IA-Generative/ocr-api/issues/144)) ([59cb5a8](https://github.com/IA-Generative/ocr-api/commit/59cb5a89691b75fa200af457c59b1b7e2896b5fc))
* refactor PDF form extraction, add vector and template management, and improve feature extraction ([cda4e3d](https://github.com/IA-Generative/ocr-api/commit/cda4e3d73c515ce5a0f20827c4d61fd59ecc3808))
* **security:** improve Keycloak token verification, logging, and documentation ([15c3b87](https://github.com/IA-Generative/ocr-api/commit/15c3b871a5d4ef77d339e1f3f0bf6555a8de1de8))
* update environment variables and refactor job and task routers for improved functionality ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))


### Bug Fixes

* :label: fix error types ts ([c3d1a13](https://github.com/IA-Generative/ocr-api/commit/c3d1a1377f0899cccb8696499abd3c4addcbebce))
* :passport_control: fixing keycloak infinity loop on sign in ([0bc8db0](https://github.com/IA-Generative/ocr-api/commit/0bc8db07a79b770b2e765fa607f4d5f240493217))
* :rocket: don't open twice file ([1ae8f31](https://github.com/IA-Generative/ocr-api/commit/1ae8f31ff1d34e822d07795411af3564bf688c3d))
* :white_check_mark: fix ocr e2e test ([f225d2f](https://github.com/IA-Generative/ocr-api/commit/f225d2f2e7fdbe5ac28b99fe34542c5d13d546e7))
* add clearToken when keycloak logout ([1fabd51](https://github.com/IA-Generative/ocr-api/commit/1fabd51be72115d858eb204512adacbf92e4340b))
* add docling_inference directory to Dockerfile ([3707056](https://github.com/IA-Generative/ocr-api/commit/37070567d0ad9f5aa77fe3d1b955b3c9df102a1d))
* add more log using user_id ([9b310c9](https://github.com/IA-Generative/ocr-api/commit/9b310c9a25ad8fdc73e15ffff17e3a3c82e5adb5))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* correct attribut href to in DsfrTile component ([43f670a](https://github.com/IA-Generative/ocr-api/commit/43f670a4171cbc6fe67a37bd00b87bda0ed97a6c))
* delete role in headers (not necessary) ([098d6a6](https://github.com/IA-Generative/ocr-api/commit/098d6a68f8ff74f0a3ff607f1e7c26b371395265))
* ensure task output pages are cleared for non-completed tasks and format delete function parameters ([edb41af](https://github.com/IA-Generative/ocr-api/commit/edb41afa9e0f4dd8b2117909cc168fa5b6a586a6))
* fix keycloak client id ([c5e932e](https://github.com/IA-Generative/ocr-api/commit/c5e932ea1e662d624c6816a6113e090f9660b209))
* hot fix lock ([2e93413](https://github.com/IA-Generative/ocr-api/commit/2e93413ed1802fa711a78a549b36d522fe013273))
* improve logging format and enhance trace context in launch_task ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* Refactor batch_predict method to improve handling of predictions and ensure non-null checks for better stability ([#55](https://github.com/IA-Generative/ocr-api/issues/55)) ([2ffdcfc](https://github.com/IA-Generative/ocr-api/commit/2ffdcfc07f2ff12b2cb399066e28a05bbd385de8))
* remove docling from dependencies and add ocr-docling group ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* remove unused 'tags' parameter from LangFuseTracingService ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* simplify metadata handling in LangFuseTracingService ([084fc56](https://github.com/IA-Generative/ocr-api/commit/084fc56e6c5326a491c4e0a02a62f3312dcdd028))
* update apps/client/src/api/http-client.ts ([7012539](https://github.com/IA-Generative/ocr-api/commit/70125395a3408a92004ab257e178714f9d53f020))
* update apps/client/src/api/http-client.ts ([2d0704f](https://github.com/IA-Generative/ocr-api/commit/2d0704f6d0f7815c4e0a501990aa9ba80701b5eb))
* update apps/client/src/api/http-client.ts ([453edc0](https://github.com/IA-Generative/ocr-api/commit/453edc0c6203c9bfee29402161a96409e9b2f377))
* update apps/client/src/utils/keycloak.ts ([9bca0e0](https://github.com/IA-Generative/ocr-api/commit/9bca0e03a7c67386a9a1e87c17716943310ab5dc))
* update apps/client/src/utils/keycloak.ts ([cdfb2f9](https://github.com/IA-Generative/ocr-api/commit/cdfb2f9c1b9443ae4aff82e9c45e4397453d1574))
* update apps/client/src/utils/keycloak.ts ([12b3614](https://github.com/IA-Generative/ocr-api/commit/12b3614a3bb2aef2669ca0bebde8d43d8b20092d))
* update apps/client/src/utils/keycloak.ts ([655e2ee](https://github.com/IA-Generative/ocr-api/commit/655e2eeda630b3d6fce788d6c8f06a217c154915))
* update apps/client/src/utils/keycloak.ts ([cb674a4](https://github.com/IA-Generative/ocr-api/commit/cb674a44d5cc705345242179cc5d66b40620004b))
* update apps/client/src/utils/keycloak.ts ([cb0a6c0](https://github.com/IA-Generative/ocr-api/commit/cb0a6c096f9b1736ebf4f9aa10b978e3c1c11a04))
* update apps/client/src/utils/keycloak.ts ([0a5e16b](https://github.com/IA-Generative/ocr-api/commit/0a5e16bd52602d0618e1882cdd2e0619b45dcedd))
* update default task operation to use DEFAULT value in upload_file function ([e5b8162](https://github.com/IA-Generative/ocr-api/commit/e5b8162ea60664dad5e3b774d3d145bff6bec1f3))
* update maxfail option in test commands to allow all tests to run ([00616f0](https://github.com/IA-Generative/ocr-api/commit/00616f004ae19bee5a587ed5fd71c963091f79b4))
* update release workflow to correct manifest and config file paths ([93de8cc](https://github.com/IA-Generative/ocr-api/commit/93de8cc4636c41e568bec0a069972c37dc020388))

## [0.4.0](https://github.com/IA-Generative/ocr-api/compare/v0.3.0...v0.4.0) (2025-09-29)


### Features

* **docs:** add Langfuse tracing configuration variables ([56fe229](https://github.com/IA-Generative/ocr-api/commit/56fe22991c1c72c20dfa792af08486896cc99abb))


### Bug Fixes

* improve logging format and enhance trace context in launch_task ([8fc774f](https://github.com/IA-Generative/ocr-api/commit/8fc774f4392eaf677f7c9619dd89d9ea69202123))
* remove unused 'tags' parameter from LangFuseTracingService ([8fc774f](https://github.com/IA-Generative/ocr-api/commit/8fc774f4392eaf677f7c9619dd89d9ea69202123))
* simplify metadata handling in LangFuseTracingService ([8fc774f](https://github.com/IA-Generative/ocr-api/commit/8fc774f4392eaf677f7c9619dd89d9ea69202123))

## [0.3.0](https://github.com/IA-Generative/ocr-api/compare/v0.2.0...v0.3.0) (2025-09-27)


### Features

* :art: add auth with backend ([8d5b74c](https://github.com/IA-Generative/ocr-api/commit/8d5b74cf18eedf7b0c4f9a1c73eee71404f8d120))
* :art: add headers to api ([ca4e425](https://github.com/IA-Generative/ocr-api/commit/ca4e425fd2d9f1a134d7ce5ee5491b22643f09ba))
* :chart_with_upwards_trend: add matomo tracking ([e0cbb46](https://github.com/IA-Generative/ocr-api/commit/e0cbb46d1487386dbca7ff3b35b7aa094a389fa6))
* :sparkles: add husky, pre-commit and commitlint ([5b77743](https://github.com/IA-Generative/ocr-api/commit/5b77743f85c7d229d33360347556121c213aef6b))
* :sparkles: update environment variables and improve sidebar links ([4a3f1e6](https://github.com/IA-Generative/ocr-api/commit/4a3f1e67158313ef84c757e05cb85ab68d95666f))
* add all text from pdf ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* add configs directory copy to Dockerfile ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* add delete routers ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* add docling process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add example curl commands for OCR API usage ([c3cc714](https://github.com/IA-Generative/ocr-api/commit/c3cc714a6e94f5b0deb42aeb0d1e88ec7633da1a))
* add Keycloak configuration details and OpenAI API variables to documentation ([ff217ac](https://github.com/IA-Generative/ocr-api/commit/ff217ac84f988c7da8e3193f5675f1eb5180150e))
* add ocr-docling group to Dockerfile build process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add parameters column to tasks and update migration script ([a1f092a](https://github.com/IA-Generative/ocr-api/commit/a1f092ae75ae27dd3fe92e1f65e680f22f8feec9))
* add PDF forms extraction worker and related tests ([d1392d9](https://github.com/IA-Generative/ocr-api/commit/d1392d9f2bdd605f01d6e966a390575d4a0b46d4))
* add workflow for testing services related to forms ([d5647b9](https://github.com/IA-Generative/ocr-api/commit/d5647b98afe4cec88e80c95275c071fc1cae12b9))
* enhance Keycloak token verification and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* enhance task management with admin checks and update request context ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* extract text and bounding boxes from PDF pages for improved data processing ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* implement centralized logging configuration system ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* integrate Keycloak authentication and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* integrate Keycloak for authentication and user management ([521a930](https://github.com/IA-Generative/ocr-api/commit/521a930719010e44b6ae39b4c4e5fb6d48a0354a))
* merge staging to preprod ([#144](https://github.com/IA-Generative/ocr-api/issues/144)) ([59cb5a8](https://github.com/IA-Generative/ocr-api/commit/59cb5a89691b75fa200af457c59b1b7e2896b5fc))
* refactor PDF form extraction, add vector and template management, and improve feature extraction ([cda4e3d](https://github.com/IA-Generative/ocr-api/commit/cda4e3d73c515ce5a0f20827c4d61fd59ecc3808))
* **security:** improve Keycloak token verification, logging, and documentation ([15c3b87](https://github.com/IA-Generative/ocr-api/commit/15c3b871a5d4ef77d339e1f3f0bf6555a8de1de8))
* update environment variables and refactor job and task routers for improved functionality ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))


### Bug Fixes

* :label: fix error types ts ([c3d1a13](https://github.com/IA-Generative/ocr-api/commit/c3d1a1377f0899cccb8696499abd3c4addcbebce))
* :passport_control: fixing keycloak infinity loop on sign in ([0bc8db0](https://github.com/IA-Generative/ocr-api/commit/0bc8db07a79b770b2e765fa607f4d5f240493217))
* :rocket: don't open twice file ([1ae8f31](https://github.com/IA-Generative/ocr-api/commit/1ae8f31ff1d34e822d07795411af3564bf688c3d))
* :white_check_mark: fix ocr e2e test ([f225d2f](https://github.com/IA-Generative/ocr-api/commit/f225d2f2e7fdbe5ac28b99fe34542c5d13d546e7))
* add clearToken when keycloak logout ([1fabd51](https://github.com/IA-Generative/ocr-api/commit/1fabd51be72115d858eb204512adacbf92e4340b))
* add docling_inference directory to Dockerfile ([3707056](https://github.com/IA-Generative/ocr-api/commit/37070567d0ad9f5aa77fe3d1b955b3c9df102a1d))
* add more log using user_id ([9b310c9](https://github.com/IA-Generative/ocr-api/commit/9b310c9a25ad8fdc73e15ffff17e3a3c82e5adb5))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* correct attribut href to in DsfrTile component ([43f670a](https://github.com/IA-Generative/ocr-api/commit/43f670a4171cbc6fe67a37bd00b87bda0ed97a6c))
* delete role in headers (not necessary) ([098d6a6](https://github.com/IA-Generative/ocr-api/commit/098d6a68f8ff74f0a3ff607f1e7c26b371395265))
* ensure task output pages are cleared for non-completed tasks and format delete function parameters ([edb41af](https://github.com/IA-Generative/ocr-api/commit/edb41afa9e0f4dd8b2117909cc168fa5b6a586a6))
* fix keycloak client id ([c5e932e](https://github.com/IA-Generative/ocr-api/commit/c5e932ea1e662d624c6816a6113e090f9660b209))
* hot fix lock ([2e93413](https://github.com/IA-Generative/ocr-api/commit/2e93413ed1802fa711a78a549b36d522fe013273))
* Refactor batch_predict method to improve handling of predictions and ensure non-null checks for better stability ([#55](https://github.com/IA-Generative/ocr-api/issues/55)) ([2ffdcfc](https://github.com/IA-Generative/ocr-api/commit/2ffdcfc07f2ff12b2cb399066e28a05bbd385de8))
* remove docling from dependencies and add ocr-docling group ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* update apps/client/src/api/http-client.ts ([7012539](https://github.com/IA-Generative/ocr-api/commit/70125395a3408a92004ab257e178714f9d53f020))
* update apps/client/src/api/http-client.ts ([2d0704f](https://github.com/IA-Generative/ocr-api/commit/2d0704f6d0f7815c4e0a501990aa9ba80701b5eb))
* update apps/client/src/api/http-client.ts ([453edc0](https://github.com/IA-Generative/ocr-api/commit/453edc0c6203c9bfee29402161a96409e9b2f377))
* update apps/client/src/utils/keycloak.ts ([9bca0e0](https://github.com/IA-Generative/ocr-api/commit/9bca0e03a7c67386a9a1e87c17716943310ab5dc))
* update apps/client/src/utils/keycloak.ts ([cdfb2f9](https://github.com/IA-Generative/ocr-api/commit/cdfb2f9c1b9443ae4aff82e9c45e4397453d1574))
* update apps/client/src/utils/keycloak.ts ([12b3614](https://github.com/IA-Generative/ocr-api/commit/12b3614a3bb2aef2669ca0bebde8d43d8b20092d))
* update apps/client/src/utils/keycloak.ts ([655e2ee](https://github.com/IA-Generative/ocr-api/commit/655e2eeda630b3d6fce788d6c8f06a217c154915))
* update apps/client/src/utils/keycloak.ts ([cb674a4](https://github.com/IA-Generative/ocr-api/commit/cb674a44d5cc705345242179cc5d66b40620004b))
* update apps/client/src/utils/keycloak.ts ([cb0a6c0](https://github.com/IA-Generative/ocr-api/commit/cb0a6c096f9b1736ebf4f9aa10b978e3c1c11a04))
* update apps/client/src/utils/keycloak.ts ([0a5e16b](https://github.com/IA-Generative/ocr-api/commit/0a5e16bd52602d0618e1882cdd2e0619b45dcedd))
* update default task operation to use DEFAULT value in upload_file function ([e5b8162](https://github.com/IA-Generative/ocr-api/commit/e5b8162ea60664dad5e3b774d3d145bff6bec1f3))
* update maxfail option in test commands to allow all tests to run ([00616f0](https://github.com/IA-Generative/ocr-api/commit/00616f004ae19bee5a587ed5fd71c963091f79b4))
* update release workflow to correct manifest and config file paths ([93de8cc](https://github.com/IA-Generative/ocr-api/commit/93de8cc4636c41e568bec0a069972c37dc020388))

## [0.2.0](https://github.com/IA-Generative/ocr-api/compare/v0.1.0...v0.2.0) (2025-09-27)


### Features

* :art: add auth with backend ([8d5b74c](https://github.com/IA-Generative/ocr-api/commit/8d5b74cf18eedf7b0c4f9a1c73eee71404f8d120))
* :art: add headers to api ([ca4e425](https://github.com/IA-Generative/ocr-api/commit/ca4e425fd2d9f1a134d7ce5ee5491b22643f09ba))
* :chart_with_upwards_trend: add matomo tracking ([e0cbb46](https://github.com/IA-Generative/ocr-api/commit/e0cbb46d1487386dbca7ff3b35b7aa094a389fa6))
* :sparkles: add husky, pre-commit and commitlint ([92b152b](https://github.com/IA-Generative/ocr-api/commit/92b152b21947314961b53ef6e236b108ce0a9b03))
* :sparkles: update environment variables and improve sidebar links ([4a3f1e6](https://github.com/IA-Generative/ocr-api/commit/4a3f1e67158313ef84c757e05cb85ab68d95666f))
* add all text from pdf ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* add configs directory copy to Dockerfile ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* add delete routers ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* add docling process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add example curl commands for OCR API usage ([c3cc714](https://github.com/IA-Generative/ocr-api/commit/c3cc714a6e94f5b0deb42aeb0d1e88ec7633da1a))
* add Keycloak configuration details and OpenAI API variables to documentation ([ff217ac](https://github.com/IA-Generative/ocr-api/commit/ff217ac84f988c7da8e3193f5675f1eb5180150e))
* add ocr-docling group to Dockerfile build process ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* add parameters column to tasks and update migration script ([a1f092a](https://github.com/IA-Generative/ocr-api/commit/a1f092ae75ae27dd3fe92e1f65e680f22f8feec9))
* add PDF forms extraction worker and related tests ([d1392d9](https://github.com/IA-Generative/ocr-api/commit/d1392d9f2bdd605f01d6e966a390575d4a0b46d4))
* add workflow for testing services related to forms ([d5647b9](https://github.com/IA-Generative/ocr-api/commit/d5647b98afe4cec88e80c95275c071fc1cae12b9))
* enhance Keycloak token verification and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* enhance task management with admin checks and update request context ([701ed7d](https://github.com/IA-Generative/ocr-api/commit/701ed7d9573ecb9063848d3e6534034354707f06))
* extract text and bounding boxes from PDF pages for improved data processing ([0ed2c8d](https://github.com/IA-Generative/ocr-api/commit/0ed2c8dfc5643272bbfe0f7d5eafc174da631d68))
* implement centralized logging configuration system ([d54236b](https://github.com/IA-Generative/ocr-api/commit/d54236b08fed9727205591a1a810c438376a0adb))
* integrate Keycloak authentication and update dependencies ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))
* integrate Keycloak for authentication and user management ([521a930](https://github.com/IA-Generative/ocr-api/commit/521a930719010e44b6ae39b4c4e5fb6d48a0354a))
* merge staging to preprod ([#144](https://github.com/IA-Generative/ocr-api/issues/144)) ([59cb5a8](https://github.com/IA-Generative/ocr-api/commit/59cb5a89691b75fa200af457c59b1b7e2896b5fc))
* refactor PDF form extraction, add vector and template management, and improve feature extraction ([cda4e3d](https://github.com/IA-Generative/ocr-api/commit/cda4e3d73c515ce5a0f20827c4d61fd59ecc3808))
* **security:** improve Keycloak token verification, logging, and documentation ([15c3b87](https://github.com/IA-Generative/ocr-api/commit/15c3b871a5d4ef77d339e1f3f0bf6555a8de1de8))
* update environment variables and refactor job and task routers for improved functionality ([af64177](https://github.com/IA-Generative/ocr-api/commit/af64177631d952c02da1a0cf77f40ca8b540f1d1))


### Bug Fixes

* :label: fix error types ts ([c3d1a13](https://github.com/IA-Generative/ocr-api/commit/c3d1a1377f0899cccb8696499abd3c4addcbebce))
* :passport_control: fixing keycloak infinity loop on sign in ([0bc8db0](https://github.com/IA-Generative/ocr-api/commit/0bc8db07a79b770b2e765fa607f4d5f240493217))
* :rocket: don't open twice file ([1ae8f31](https://github.com/IA-Generative/ocr-api/commit/1ae8f31ff1d34e822d07795411af3564bf688c3d))
* :white_check_mark: fix ocr e2e test ([f225d2f](https://github.com/IA-Generative/ocr-api/commit/f225d2f2e7fdbe5ac28b99fe34542c5d13d546e7))
* add clearToken when keycloak logout ([1fabd51](https://github.com/IA-Generative/ocr-api/commit/1fabd51be72115d858eb204512adacbf92e4340b))
* add docling_inference directory to Dockerfile ([3707056](https://github.com/IA-Generative/ocr-api/commit/37070567d0ad9f5aa77fe3d1b955b3c9df102a1d))
* add more log using user_id ([9b310c9](https://github.com/IA-Generative/ocr-api/commit/9b310c9a25ad8fdc73e15ffff17e3a3c82e5adb5))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* correct attribut href to in DsfrTile component ([43f670a](https://github.com/IA-Generative/ocr-api/commit/43f670a4171cbc6fe67a37bd00b87bda0ed97a6c))
* delete role in headers (not necessary) ([098d6a6](https://github.com/IA-Generative/ocr-api/commit/098d6a68f8ff74f0a3ff607f1e7c26b371395265))
* ensure task output pages are cleared for non-completed tasks and format delete function parameters ([edb41af](https://github.com/IA-Generative/ocr-api/commit/edb41afa9e0f4dd8b2117909cc168fa5b6a586a6))
* fix keycloak client id ([c5e932e](https://github.com/IA-Generative/ocr-api/commit/c5e932ea1e662d624c6816a6113e090f9660b209))
* hot fix lock ([2e93413](https://github.com/IA-Generative/ocr-api/commit/2e93413ed1802fa711a78a549b36d522fe013273))
* Refactor batch_predict method to improve handling of predictions and ensure non-null checks for better stability ([#55](https://github.com/IA-Generative/ocr-api/issues/55)) ([2ffdcfc](https://github.com/IA-Generative/ocr-api/commit/2ffdcfc07f2ff12b2cb399066e28a05bbd385de8))
* remove docling from dependencies and add ocr-docling group ([96f7828](https://github.com/IA-Generative/ocr-api/commit/96f782802b6726e2ec6b34733978bdd1006a0262))
* update apps/client/src/api/http-client.ts ([7012539](https://github.com/IA-Generative/ocr-api/commit/70125395a3408a92004ab257e178714f9d53f020))
* update apps/client/src/api/http-client.ts ([2d0704f](https://github.com/IA-Generative/ocr-api/commit/2d0704f6d0f7815c4e0a501990aa9ba80701b5eb))
* update apps/client/src/api/http-client.ts ([453edc0](https://github.com/IA-Generative/ocr-api/commit/453edc0c6203c9bfee29402161a96409e9b2f377))
* update apps/client/src/utils/keycloak.ts ([9bca0e0](https://github.com/IA-Generative/ocr-api/commit/9bca0e03a7c67386a9a1e87c17716943310ab5dc))
* update apps/client/src/utils/keycloak.ts ([cdfb2f9](https://github.com/IA-Generative/ocr-api/commit/cdfb2f9c1b9443ae4aff82e9c45e4397453d1574))
* update apps/client/src/utils/keycloak.ts ([12b3614](https://github.com/IA-Generative/ocr-api/commit/12b3614a3bb2aef2669ca0bebde8d43d8b20092d))
* update apps/client/src/utils/keycloak.ts ([655e2ee](https://github.com/IA-Generative/ocr-api/commit/655e2eeda630b3d6fce788d6c8f06a217c154915))
* update apps/client/src/utils/keycloak.ts ([cb674a4](https://github.com/IA-Generative/ocr-api/commit/cb674a44d5cc705345242179cc5d66b40620004b))
* update apps/client/src/utils/keycloak.ts ([cb0a6c0](https://github.com/IA-Generative/ocr-api/commit/cb0a6c096f9b1736ebf4f9aa10b978e3c1c11a04))
* update apps/client/src/utils/keycloak.ts ([0a5e16b](https://github.com/IA-Generative/ocr-api/commit/0a5e16bd52602d0618e1882cdd2e0619b45dcedd))
* update default task operation to use DEFAULT value in upload_file function ([e5b8162](https://github.com/IA-Generative/ocr-api/commit/e5b8162ea60664dad5e3b774d3d145bff6bec1f3))
* update maxfail option in test commands to allow all tests to run ([00616f0](https://github.com/IA-Generative/ocr-api/commit/00616f004ae19bee5a587ed5fd71c963091f79b4))
* update release workflow to correct manifest and config file paths ([7769665](https://github.com/IA-Generative/ocr-api/commit/77696658f14eaa8952f895ee97fd8dde7d9deb15))

## [0.1.0](https://github.com/IA-Generative/ocr-api/compare/v0.0.1...v0.1.0) (2025-07-30)


### Features

* :chart_with_upwards_trend: add matomo tracking ([f73aacb](https://github.com/IA-Generative/ocr-api/commit/f73aacbf8bc4898b20b8632bb516fd612d968510))
* add PDF forms extraction worker and related tests ([98bcdf1](https://github.com/IA-Generative/ocr-api/commit/98bcdf1daa580b934de3e68db89b591b81259487))
* add workflow for testing services related to forms ([eecc67b](https://github.com/IA-Generative/ocr-api/commit/eecc67ba7103cec7b6b32b3bcad11e11a4d7057b))


### Bug Fixes

* :rocket: don't open twice file ([eb6464c](https://github.com/IA-Generative/ocr-api/commit/eb6464c6f08bc5a4b6725f5fadbbbb14d12d29c4))
* add more log using user_id ([9b310c9](https://github.com/IA-Generative/ocr-api/commit/9b310c9a25ad8fdc73e15ffff17e3a3c82e5adb5))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* hot fix lock ([2e93413](https://github.com/IA-Generative/ocr-api/commit/2e93413ed1802fa711a78a549b36d522fe013273))
* Refactor batch_predict method to improve handling of predictions and ensure non-null checks for better stability ([#55](https://github.com/IA-Generative/ocr-api/issues/55)) ([2ffdcfc](https://github.com/IA-Generative/ocr-api/commit/2ffdcfc07f2ff12b2cb399066e28a05bbd385de8))

## [1.7.0](https://github.com/IA-Generative/ocr-api/compare/v1.6.0...v1.7.0) (2025-07-15)


### Features

* ❇️ add queue arch ([#21](https://github.com/IA-Generative/ocr-api/issues/21)) ([0243aaf](https://github.com/IA-Generative/ocr-api/commit/0243aafead55914213fd21d2b86255dfd29db746))
* add checkbox drawing functionality and update tests with new images and JSON data ([f3e9df8](https://github.com/IA-Generative/ocr-api/commit/f3e9df8dcd928d347f342d07aaa7a8b18871f6b5))


### Bug Fixes

* add cache package ([92044ca](https://github.com/IA-Generative/ocr-api/commit/92044cacdb3e6a060e10061cc45bf3549f143af9))
* add checkbox_service directory to Dockerfile ([3fadb80](https://github.com/IA-Generative/ocr-api/commit/3fadb80026abc7dd848056d0bad2ca8ad182913a))
* add llm folder ([aa06510](https://github.com/IA-Generative/ocr-api/commit/aa0651016023609dea2514caab45d87e22c7d7af))
* add logging to BoxDetection class and improve batch_predict method performance ([43edf1c](https://github.com/IA-Generative/ocr-api/commit/43edf1cf17520790c7ff65278073c460b1199fc9))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* comment out text_det_limit_type and format batch_predict method signature ([195606d](https://github.com/IA-Generative/ocr-api/commit/195606d812567f749113f490de0d6173a6e90e22))
* comment out unused GPU build configurations for paddleocr ([fbe9447](https://github.com/IA-Generative/ocr-api/commit/fbe9447d174f88bd042fc257f9360527ceffb183))
* download using cpu ([2eb5f5b](https://github.com/IA-Generative/ocr-api/commit/2eb5f5bdbda4f4aacbc8532928124cd45f07e715))
* enhance error logging in TemplateLLMDetector and improve code formatting ([7b93841](https://github.com/IA-Generative/ocr-api/commit/7b93841b10c5abec8957ce6c4d9378409a7c3c01))
* format code for better readability and ensure models are appended correctly ([2ac03f4](https://github.com/IA-Generative/ocr-api/commit/2ac03f43237abefdd2c61da493edb7127629002d))
* improve code readability by formatting and adding debug logs in BaseWorker ([7b22719](https://github.com/IA-Generative/ocr-api/commit/7b227196a3f62ebeded8c1d3366a034aabd02fe9))
* improve readability of batch_predict method in BoxDetection class ([3d9806a](https://github.com/IA-Generative/ocr-api/commit/3d9806ad436e8709c33fbb27052ff0bbf71c9ae5))
* model instances ([9c8e355](https://github.com/IA-Generative/ocr-api/commit/9c8e355f138aa6c73c3293c6c9837965bbaa7670))
* Refactor model initialization to move warmup logging after model creation ([20a55dd](https://github.com/IA-Generative/ocr-api/commit/20a55dd11af9f428fe310c676f9b183a5cf48628))
* refactor PaddleInferOCR initialization to use settings from PaddleSetting ([ea6b3d8](https://github.com/IA-Generative/ocr-api/commit/ea6b3d87a3a9da4ea3e0170a33f71b5c5a7a3241))
* remove migration service from dependencies in multiple services ([8d31689](https://github.com/IA-Generative/ocr-api/commit/8d31689d53a028f4a2b2b90261d8e0191f00bc9a))
* remove redundant uv sync command in Dockerfile ([3471b14](https://github.com/IA-Generative/ocr-api/commit/3471b14513868ba7efd259fb284ef0b8e91f20f4))
* rename PaddleFormulaPredcition to PaddleFormulaRecognizer for consistency ([130c6d9](https://github.com/IA-Generative/ocr-api/commit/130c6d98bebeb2fa5604200137477aa61ee5f99d))
* result ([6fc2872](https://github.com/IA-Generative/ocr-api/commit/6fc287235ccea9b3e8fe986e5344817ceaf4ef16))
* revert OCR_VERSION to PP-OCRv4 and set default OCR_LANG to 'en' ([e1df499](https://github.com/IA-Generative/ocr-api/commit/e1df499b0e4892c56decfa91b8be1aa774f9ce58))
* update Dockerfile to include 'services' group in uv sync command ([681d174](https://github.com/IA-Generative/ocr-api/commit/681d17458aaa86e46cb33e3d6acb8bd32f25bedb))
* update image names for paddleocr services to include version ([4221e84](https://github.com/IA-Generative/ocr-api/commit/4221e84759a486ac227b565706761c7d546d1e13))
* use gpu ([82455e3](https://github.com/IA-Generative/ocr-api/commit/82455e38b13af7d9b0c617328c58ec588e4dc663))
* use uv instead of vu ([4598d93](https://github.com/IA-Generative/ocr-api/commit/4598d93cea4680670124cd3d9816fed4c1fb1f26))

## [1.6.0](https://github.com/IA-Generative/ocr-api/compare/v1.5.0...v1.6.0) (2025-07-08)


### Features

* ❇️ add queue arch ([#21](https://github.com/IA-Generative/ocr-api/issues/21)) ([0243aaf](https://github.com/IA-Generative/ocr-api/commit/0243aafead55914213fd21d2b86255dfd29db746))
* add checkbox drawing functionality and update tests with new images and JSON data ([f3e9df8](https://github.com/IA-Generative/ocr-api/commit/f3e9df8dcd928d347f342d07aaa7a8b18871f6b5))


### Bug Fixes

* add checkbox_service directory to Dockerfile ([3fadb80](https://github.com/IA-Generative/ocr-api/commit/3fadb80026abc7dd848056d0bad2ca8ad182913a))
* add logging to BoxDetection class and improve batch_predict method performance ([43edf1c](https://github.com/IA-Generative/ocr-api/commit/43edf1cf17520790c7ff65278073c460b1199fc9))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* comment out text_det_limit_type and format batch_predict method signature ([195606d](https://github.com/IA-Generative/ocr-api/commit/195606d812567f749113f490de0d6173a6e90e22))
* comment out unused GPU build configurations for paddleocr ([fbe9447](https://github.com/IA-Generative/ocr-api/commit/fbe9447d174f88bd042fc257f9360527ceffb183))
* download using cpu ([2eb5f5b](https://github.com/IA-Generative/ocr-api/commit/2eb5f5bdbda4f4aacbc8532928124cd45f07e715))
* enhance error logging in TemplateLLMDetector and improve code formatting ([7b93841](https://github.com/IA-Generative/ocr-api/commit/7b93841b10c5abec8957ce6c4d9378409a7c3c01))
* format code for better readability and ensure models are appended correctly ([2ac03f4](https://github.com/IA-Generative/ocr-api/commit/2ac03f43237abefdd2c61da493edb7127629002d))
* improve code readability by formatting and adding debug logs in BaseWorker ([7b22719](https://github.com/IA-Generative/ocr-api/commit/7b227196a3f62ebeded8c1d3366a034aabd02fe9))
* improve readability of batch_predict method in BoxDetection class ([3d9806a](https://github.com/IA-Generative/ocr-api/commit/3d9806ad436e8709c33fbb27052ff0bbf71c9ae5))
* Refactor model initialization to move warmup logging after model creation ([20a55dd](https://github.com/IA-Generative/ocr-api/commit/20a55dd11af9f428fe310c676f9b183a5cf48628))
* refactor PaddleInferOCR initialization to use settings from PaddleSetting ([ea6b3d8](https://github.com/IA-Generative/ocr-api/commit/ea6b3d87a3a9da4ea3e0170a33f71b5c5a7a3241))
* remove migration service from dependencies in multiple services ([8d31689](https://github.com/IA-Generative/ocr-api/commit/8d31689d53a028f4a2b2b90261d8e0191f00bc9a))
* remove redundant uv sync command in Dockerfile ([3471b14](https://github.com/IA-Generative/ocr-api/commit/3471b14513868ba7efd259fb284ef0b8e91f20f4))
* rename PaddleFormulaPredcition to PaddleFormulaRecognizer for consistency ([130c6d9](https://github.com/IA-Generative/ocr-api/commit/130c6d98bebeb2fa5604200137477aa61ee5f99d))
* revert OCR_VERSION to PP-OCRv4 and set default OCR_LANG to 'en' ([e1df499](https://github.com/IA-Generative/ocr-api/commit/e1df499b0e4892c56decfa91b8be1aa774f9ce58))
* update Dockerfile to include 'services' group in uv sync command ([681d174](https://github.com/IA-Generative/ocr-api/commit/681d17458aaa86e46cb33e3d6acb8bd32f25bedb))
* update image names for paddleocr services to include version ([4221e84](https://github.com/IA-Generative/ocr-api/commit/4221e84759a486ac227b565706761c7d546d1e13))
* use uv instead of vu ([4598d93](https://github.com/IA-Generative/ocr-api/commit/4598d93cea4680670124cd3d9816fed4c1fb1f26))

## [1.5.0](https://github.com/IA-Generative/ocr-api/compare/v1.4.0...v1.5.0) (2025-07-08)


### Features

* ❇️ add queue arch ([#21](https://github.com/IA-Generative/ocr-api/issues/21)) ([0243aaf](https://github.com/IA-Generative/ocr-api/commit/0243aafead55914213fd21d2b86255dfd29db746))
* add checkbox drawing functionality and update tests with new images and JSON data ([f3e9df8](https://github.com/IA-Generative/ocr-api/commit/f3e9df8dcd928d347f342d07aaa7a8b18871f6b5))


### Bug Fixes

* add checkbox_service directory to Dockerfile ([3fadb80](https://github.com/IA-Generative/ocr-api/commit/3fadb80026abc7dd848056d0bad2ca8ad182913a))
* add logging to BoxDetection class and improve batch_predict method performance ([43edf1c](https://github.com/IA-Generative/ocr-api/commit/43edf1cf17520790c7ff65278073c460b1199fc9))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* comment out text_det_limit_type and format batch_predict method signature ([195606d](https://github.com/IA-Generative/ocr-api/commit/195606d812567f749113f490de0d6173a6e90e22))
* comment out unused GPU build configurations for paddleocr ([fbe9447](https://github.com/IA-Generative/ocr-api/commit/fbe9447d174f88bd042fc257f9360527ceffb183))
* download using cpu ([2eb5f5b](https://github.com/IA-Generative/ocr-api/commit/2eb5f5bdbda4f4aacbc8532928124cd45f07e715))
* format code for better readability and ensure models are appended correctly ([2ac03f4](https://github.com/IA-Generative/ocr-api/commit/2ac03f43237abefdd2c61da493edb7127629002d))
* improve code readability by formatting and adding debug logs in BaseWorker ([7b22719](https://github.com/IA-Generative/ocr-api/commit/7b227196a3f62ebeded8c1d3366a034aabd02fe9))
* improve readability of batch_predict method in BoxDetection class ([3d9806a](https://github.com/IA-Generative/ocr-api/commit/3d9806ad436e8709c33fbb27052ff0bbf71c9ae5))
* Refactor model initialization to move warmup logging after model creation ([20a55dd](https://github.com/IA-Generative/ocr-api/commit/20a55dd11af9f428fe310c676f9b183a5cf48628))
* refactor PaddleInferOCR initialization to use settings from PaddleSetting ([ea6b3d8](https://github.com/IA-Generative/ocr-api/commit/ea6b3d87a3a9da4ea3e0170a33f71b5c5a7a3241))
* remove migration service from dependencies in multiple services ([8d31689](https://github.com/IA-Generative/ocr-api/commit/8d31689d53a028f4a2b2b90261d8e0191f00bc9a))
* remove redundant uv sync command in Dockerfile ([3471b14](https://github.com/IA-Generative/ocr-api/commit/3471b14513868ba7efd259fb284ef0b8e91f20f4))
* rename PaddleFormulaPredcition to PaddleFormulaRecognizer for consistency ([130c6d9](https://github.com/IA-Generative/ocr-api/commit/130c6d98bebeb2fa5604200137477aa61ee5f99d))
* revert OCR_VERSION to PP-OCRv4 and set default OCR_LANG to 'en' ([e1df499](https://github.com/IA-Generative/ocr-api/commit/e1df499b0e4892c56decfa91b8be1aa774f9ce58))
* update Dockerfile to include 'services' group in uv sync command ([681d174](https://github.com/IA-Generative/ocr-api/commit/681d17458aaa86e46cb33e3d6acb8bd32f25bedb))
* update image names for paddleocr services to include version ([4221e84](https://github.com/IA-Generative/ocr-api/commit/4221e84759a486ac227b565706761c7d546d1e13))
* use uv instead of vu ([4598d93](https://github.com/IA-Generative/ocr-api/commit/4598d93cea4680670124cd3d9816fed4c1fb1f26))

## [1.5.0](https://github.com/IA-Generative/ocr-api/compare/v1.4.0...v1.5.0) (2025-07-07)


### Features

* ❇️ add queue arch ([#21](https://github.com/IA-Generative/ocr-api/issues/21)) ([0243aaf](https://github.com/IA-Generative/ocr-api/commit/0243aafead55914213fd21d2b86255dfd29db746))
* add checkbox drawing functionality and update tests with new images and JSON data ([f3e9df8](https://github.com/IA-Generative/ocr-api/commit/f3e9df8dcd928d347f342d07aaa7a8b18871f6b5))


### Bug Fixes

* add checkbox_service directory to Dockerfile ([3fadb80](https://github.com/IA-Generative/ocr-api/commit/3fadb80026abc7dd848056d0bad2ca8ad182913a))
* add logging to BoxDetection class and improve batch_predict method performance ([43edf1c](https://github.com/IA-Generative/ocr-api/commit/43edf1cf17520790c7ff65278073c460b1199fc9))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* comment out text_det_limit_type and format batch_predict method signature ([195606d](https://github.com/IA-Generative/ocr-api/commit/195606d812567f749113f490de0d6173a6e90e22))
* download using cpu ([2eb5f5b](https://github.com/IA-Generative/ocr-api/commit/2eb5f5bdbda4f4aacbc8532928124cd45f07e715))
* improve readability of batch_predict method in BoxDetection class ([3d9806a](https://github.com/IA-Generative/ocr-api/commit/3d9806ad436e8709c33fbb27052ff0bbf71c9ae5))
* Refactor model initialization to move warmup logging after model creation ([20a55dd](https://github.com/IA-Generative/ocr-api/commit/20a55dd11af9f428fe310c676f9b183a5cf48628))
* refactor PaddleInferOCR initialization to use settings from PaddleSetting ([ea6b3d8](https://github.com/IA-Generative/ocr-api/commit/ea6b3d87a3a9da4ea3e0170a33f71b5c5a7a3241))
* rename PaddleFormulaPredcition to PaddleFormulaRecognizer for consistency ([130c6d9](https://github.com/IA-Generative/ocr-api/commit/130c6d98bebeb2fa5604200137477aa61ee5f99d))
* revert OCR_VERSION to PP-OCRv4 and set default OCR_LANG to 'en' ([e1df499](https://github.com/IA-Generative/ocr-api/commit/e1df499b0e4892c56decfa91b8be1aa774f9ce58))
* update image names for paddleocr services to include version ([4221e84](https://github.com/IA-Generative/ocr-api/commit/4221e84759a486ac227b565706761c7d546d1e13))
* use uv instead of vu ([4598d93](https://github.com/IA-Generative/ocr-api/commit/4598d93cea4680670124cd3d9816fed4c1fb1f26))

## [0.1.0](https://github.com/IA-Generative/ocr-api/compare/v0.0.1...v0.1.0) (2025-06-18)


### Features

* ❇️ add queue arch ([#21](https://github.com/IA-Generative/ocr-api/issues/21)) ([0243aaf](https://github.com/IA-Generative/ocr-api/commit/0243aafead55914213fd21d2b86255dfd29db746))
* Add BoxDetection model and update configuration parameters ([#53](https://github.com/IA-Generative/ocr-api/issues/53)) ([ea8b33c](https://github.com/IA-Generative/ocr-api/commit/ea8b33c0ddfdf31a89fedba932fb2c3bba0d1cdf))


### Bug Fixes

* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* Correct Dockerfile path for ocr-service-paddle build ([e3f59e8](https://github.com/IA-Generative/ocr-api/commit/e3f59e812c0d997a2b88b56f914ea4d4571b5b1f))
* Improve checkbox confidence calculation and refactor code for readability ([262e57f](https://github.com/IA-Generative/ocr-api/commit/262e57fc25ef1918ad4f6236b86bb2c114ad68b7))
* Refactor model initialization to move warmup logging after model creation ([20a55dd](https://github.com/IA-Generative/ocr-api/commit/20a55dd11af9f428fe310c676f9b183a5cf48628))
* Remove unused GPU build configuration for ocr-service-paddle ([a1fc6c3](https://github.com/IA-Generative/ocr-api/commit/a1fc6c3b00e754db6f9a297d40f5ab5b03f1a027))
* Update target_size type to tuple and enhance image resizing logic ([9b92d3f](https://github.com/IA-Generative/ocr-api/commit/9b92d3fb20610b4fbdb88506f0814b5d466eadee))

## [1.3.0](https://github.com/IA-Generative/ocr-api/compare/v1.2.1...v1.3.0) (2025-05-21)


### Features

* ❇️ add position in queue ([#42](https://github.com/IA-Generative/ocr-api/issues/42)) ([cce48e9](https://github.com/IA-Generative/ocr-api/commit/cce48e9863003416762c03a4da3bdc3c38f62e23))


## [1.2.1](https://github.com/IA-Generative/ocr-api/compare/v1.2.0...v1.2.1) (2025-05-20)


### Bug Fixes

* donwload text ([#40](https://github.com/IA-Generative/ocr-api/issues/40)) ([55818ae](https://github.com/IA-Generative/ocr-api/commit/55818ae9384c9497e389279619016e141a4f2005))

## [1.2.0](https://github.com/IA-Generative/ocr-api/compare/v1.1.0...v1.2.0) (2025-05-20)


### Features

* add route to download text ([#37](https://github.com/IA-Generative/ocr-api/issues/37)) ([764806b](https://github.com/IA-Generative/ocr-api/commit/764806b05d656eec6e128d194a5ac05f99df40d5))


### Bug Fixes

* donwload text ([#39](https://github.com/IA-Generative/ocr-api/issues/39)) ([d02c155](https://github.com/IA-Generative/ocr-api/commit/d02c155771c7de4c3cfcaffe3cfe65d8466f3b57))

## [1.1.0](https://github.com/IA-Generative/ocr-api/compare/v1.0.0...v1.1.0) (2025-05-19)


### Features

* ❇️ add queue arch ([#21](https://github.com/IA-Generative/ocr-api/issues/21)) ([0243aaf](https://github.com/IA-Generative/ocr-api/commit/0243aafead55914213fd21d2b86255dfd29db746))

## [1.0.0](https://github.com/IA-Generative/ocr-api/compare/v0.0.1...v1.0.0) (2025-05-16)


### ⚠ BREAKING CHANGES

* :tada: add new arch for queueing ocr

### Features

* :rocket: add stress tests ([066d878](https://github.com/IA-Generative/ocr-api/commit/066d878582f997452605036d1527f8f526db9aef))
* :sparkles: add output input form ([#19](https://github.com/IA-Generative/ocr-api/issues/19)) ([66f16ab](https://github.com/IA-Generative/ocr-api/commit/66f16ab77afcdd1f5e18d1a48fd2088fcbff9e9f))
* :tada: add new arch for queueing ocr ([bb8f9c2](https://github.com/IA-Generative/ocr-api/commit/bb8f9c2f64454638751ebb8a53f8f7f29b9245f0))
* add release ([#28](https://github.com/IA-Generative/ocr-api/issues/28)) ([5cf7390](https://github.com/IA-Generative/ocr-api/commit/5cf7390d24d39a96697e916a728da516eacee99f))
* add signe url ([#24](https://github.com/IA-Generative/ocr-api/issues/24)) ([61b2bb0](https://github.com/IA-Generative/ocr-api/commit/61b2bb01d93aa4ade5f8e25d4bd0909fbe6aa0d9))


### Bug Fixes

* :bug: change runner type ([77d7c7f](https://github.com/IA-Generative/ocr-api/commit/77d7c7f7b663eac1b782dc4f35747f2d190452b1))
* raise error ([8ce8ad6](https://github.com/IA-Generative/ocr-api/commit/8ce8ad65b2f306d86b1905fac9e7e7d10e8bfb21))

## 0.2.0 (2025-04-24)

### Feat

- add paddle
- add task_stats
- :zap: add flower monitoring queue
- :beers: concurrency works for celery
- :zap: add celery queue
- add some celery for titi
- reduce main and add abtract to wrker
- add workers
- use surya ocr
- add surya ocr
- add surya ocr

### Fix

- :bug: run worker with good model
- rid off ignore folder ignore
- don't use user_id
- add failure process
- use pg
- add pg in docker compose
- add psycopg
- global variable and unittest
- task_data not found
- don't use ressource
- cean code
- typo
- stress test
- install
- installation poppler-utils
- correct dockerfile
- service
- don't use paddle ocr
- add unittest for utils
- hope that create directory
- dwnload model
- installation ocr-service
- add pillow

## [0.3.0](https://github.com/IA-Generative/ocr-api/compare/v0.2.0...v0.3.0) (2025-04-25)


### Features

* :beers: concurrency works for celery ([7b7466b](https://github.com/IA-Generative/ocr-api/commit/7b7466b38f845cd81a1c8ae666534405482cda63))
* :zap: add celery queue ([6aff3db](https://github.com/IA-Generative/ocr-api/commit/6aff3dbca81c4b8d89a030966e044978b7b649d3))
* :zap: add flower monitoring queue ([398f9a9](https://github.com/IA-Generative/ocr-api/commit/398f9a92b74cb830d1279a60fba71371c38b9d1c))
* add ci-cd ([c9a1e56](https://github.com/IA-Generative/ocr-api/commit/c9a1e5607cd8f74316c7bad374e936e23eec3d52))
* add docekrfiles ([1f21b0f](https://github.com/IA-Generative/ocr-api/commit/1f21b0fd4705f06bd5db2e7614c628066e28fd17))
* add documentation ([6116038](https://github.com/IA-Generative/ocr-api/commit/61160382b88afc57c863c194fa04d524f6c5fe83))
* add github action for release ([ed761f4](https://github.com/IA-Generative/ocr-api/commit/ed761f47e86d6d169d340ff5ce7a77facccc1c80))
* add more extras ([3921c99](https://github.com/IA-Generative/ocr-api/commit/3921c998cfaba1c1682af55dc229ba8c1f3beb07))
* add ocr service ([e2f2ace](https://github.com/IA-Generative/ocr-api/commit/e2f2ace131e48cdb4c85a4282cd23a2fc13e6d45))
* add paddle ([f96a942](https://github.com/IA-Generative/ocr-api/commit/f96a9421ebcf20c23c1e3694e43fd5cb9818b0bc))
* add redis broker ([fb0db99](https://github.com/IA-Generative/ocr-api/commit/fb0db99ba9f9779afed4c71f2e6e70482004436f))
* add some celery for titi ([28a14df](https://github.com/IA-Generative/ocr-api/commit/28a14dfd086986922621b08e299515b90cde99b5))
* add surya ocr ([3a74515](https://github.com/IA-Generative/ocr-api/commit/3a745153cd3b8181b5bd86ca6d602945e5991767))
* add surya ocr ([134ffbc](https://github.com/IA-Generative/ocr-api/commit/134ffbce6cb3e01057ef74bffd5d8ca0e60b9838))
* add task_stats ([ebe50c5](https://github.com/IA-Generative/ocr-api/commit/ebe50c5af825940c3febf18c2893ce87823f718c))
* add workers ([800d3f2](https://github.com/IA-Generative/ocr-api/commit/800d3f2b185d91c1e782156b56198875e9dbce15))
* minio connection ([573bd91](https://github.com/IA-Generative/ocr-api/commit/573bd919f3dad80ba098ee22db4ca7af262756ff))
* move route health ([9a017a5](https://github.com/IA-Generative/ocr-api/commit/9a017a59e71420125296f7b6d1b3a77b6a7170c4))
* reduce main and add abtract to wrker ([91dd9cb](https://github.com/IA-Generative/ocr-api/commit/91dd9cbc0768e5e9ff0eeb81ee78a5e5cf999449))
* route jobs ([340c35c](https://github.com/IA-Generative/ocr-api/commit/340c35cf463dda683a14dca5d5bfbd059278123e))
* use surya ocr ([2512889](https://github.com/IA-Generative/ocr-api/commit/251288995689102d66ecbf8f530c507d2a407907))


### Bug Fixes

* :bug: run worker with good model ([5b87298](https://github.com/IA-Generative/ocr-api/commit/5b872985d8331c2da713b098689e6ff774ef9467))
* :fire: correct models dockerfiles ([5113288](https://github.com/IA-Generative/ocr-api/commit/511328894abf84e5b0eb2450011f6e5a619fe2cb))
* add database url ([fa44788](https://github.com/IA-Generative/ocr-api/commit/fa44788887eaeb83c9ce1bc08556d34e901c1d2d))
* add docerfile ([e57814f](https://github.com/IA-Generative/ocr-api/commit/e57814f7a4b2af3f05f2b2806eb2119aece3c6dd))
* add failure process ([c802064](https://github.com/IA-Generative/ocr-api/commit/c8020644392385e3785d817edea914e86a008770))
* add pg in docker compose ([e30b15a](https://github.com/IA-Generative/ocr-api/commit/e30b15a80667d743707c3691977950d92a3298d6))
* add pillow ([d448ced](https://github.com/IA-Generative/ocr-api/commit/d448ced367919799064c34041c7235f891a1b15d))
* add psycopg ([5256eea](https://github.com/IA-Generative/ocr-api/commit/5256eea205a802acaebeb64851cc0a8b3f6f6148))
* add unittest for utils ([eecee0e](https://github.com/IA-Generative/ocr-api/commit/eecee0e8d6a9887906a5d0e324bf148df17f28d3))
* async routes ([7289ffd](https://github.com/IA-Generative/ocr-api/commit/7289ffd247ebc7b1e50f4f61dcb348a2759848ef))
* async routes ([#7](https://github.com/IA-Generative/ocr-api/issues/7)) ([525dddd](https://github.com/IA-Generative/ocr-api/commit/525dddd4ca418c396ced33c29953f4ac9a87f6e9))
* branch name ([c431d38](https://github.com/IA-Generative/ocr-api/commit/c431d382ddcc2c259733bdf14ef4188889a3fb24))
* cean code ([14935da](https://github.com/IA-Generative/ocr-api/commit/14935da7f82539e4bb6dca402c547d316112b6a5))
* clean code ([c06e8fe](https://github.com/IA-Generative/ocr-api/commit/c06e8fe5ae7fb5fa32aa41d8f31d8e61f4e672f7))
* clean code with ruff ([b41e781](https://github.com/IA-Generative/ocr-api/commit/b41e781c54cec6fbf63afb45456acf1a6da10a40))
* correct dockerfile ([937cde7](https://github.com/IA-Generative/ocr-api/commit/937cde75379d46df75d0a2786f2fd0e10706624d))
* db ([82fe96d](https://github.com/IA-Generative/ocr-api/commit/82fe96dfacff9d671fa87ebfe7b37e8a5a7176dc))
* db creator ([5b5dee7](https://github.com/IA-Generative/ocr-api/commit/5b5dee7bfe26341748cd5d70d6876167b34b5bd2))
* don't use paddle ocr ([65824e5](https://github.com/IA-Generative/ocr-api/commit/65824e5134f651574d44af0e103703823c842773))
* don't use ressource ([6551382](https://github.com/IA-Generative/ocr-api/commit/655138273a8d9a0adf95fcbce0bfa797a56389bd))
* don't use user_id ([97150b5](https://github.com/IA-Generative/ocr-api/commit/97150b5729b5bea9e52c9641ba63f2235444de4b))
* dwnload model ([2d1e76e](https://github.com/IA-Generative/ocr-api/commit/2d1e76ecb79b59c58cd422f4f974a067f2c47417))
* en down ([ddca026](https://github.com/IA-Generative/ocr-api/commit/ddca026ecbaa430d3adcb0901be4ad7d24d98667))
* env file ([d43caff](https://github.com/IA-Generative/ocr-api/commit/d43caff3721172441adbc9163f0a715168bb0225))
* extras allow ([6310008](https://github.com/IA-Generative/ocr-api/commit/63100084fb0fe46e82169632b489c3f3227a92a2))
* fastdeploy dir ([c933c14](https://github.com/IA-Generative/ocr-api/commit/c933c148b1f8eaad7a6b702f3587eee877fb62f4))
* global variable and unittest ([0f9d31f](https://github.com/IA-Generative/ocr-api/commit/0f9d31f585a66ef6a5a92a6744906b7012f16819))
* hope that create directory ([98b3b58](https://github.com/IA-Generative/ocr-api/commit/98b3b5835c64075144f209797d822a39d7ca4789))
* ingore .db ([5b4e934](https://github.com/IA-Generative/ocr-api/commit/5b4e934e08e0757873357664bfe8586ff7b2fed9))
* install ([d598c18](https://github.com/IA-Generative/ocr-api/commit/d598c188a3e1274f14268ef6d9b176c271156241))
* installation ocr-service ([0656729](https://github.com/IA-Generative/ocr-api/commit/06567291f12395680fbe5282272415ad7468c4ed))
* installation poppler-utils ([b170d7c](https://github.com/IA-Generative/ocr-api/commit/b170d7cae0f566e63446360b79c5ee11f2f8db28))
* launch anytime ([394a598](https://github.com/IA-Generative/ocr-api/commit/394a5980e0461bcb0603863e1af95c4011769549))
* let user id ([66ea277](https://github.com/IA-Generative/ocr-api/commit/66ea277cec93361dd9aac70cede46044e8554f08))
* multi worker and thread ([e2d47ae](https://github.com/IA-Generative/ocr-api/commit/e2d47aec7204fe01da055fa3029199340ab2551b))
* non root cache dir ([1d05402](https://github.com/IA-Generative/ocr-api/commit/1d054027a07ead0d04a0b30e847c177b047a7b2a))
* pythonpath ([b268746](https://github.com/IA-Generative/ocr-api/commit/b26874660a22a545185c51863e7754fc203b82ec))
* pythonpath using export ([0eef252](https://github.com/IA-Generative/ocr-api/commit/0eef252c6fe9158f23175c5662d39bb6f1e1fa34))
* redis and minio sender ([ba1d283](https://github.com/IA-Generative/ocr-api/commit/ba1d283fd9c96cf87eef4461b75dc9d32994e6cc))
* remove clean cache ([edaa149](https://github.com/IA-Generative/ocr-api/commit/edaa14929c0efafc3da369d20014e57c04df93e9))
* rid off ignore folder ignore ([4f94b77](https://github.com/IA-Generative/ocr-api/commit/4f94b77e04b776b7c962aace2cbaac7ea04a0e68))
* service ([9bdd164](https://github.com/IA-Generative/ocr-api/commit/9bdd1642ecdaa855a532a4cf7f2246dcb666c35a))
* size to send ([1f5ef6e](https://github.com/IA-Generative/ocr-api/commit/1f5ef6e00d4ced199b11bd61b9271752faf6ac0a))
* stress test ([fd8c204](https://github.com/IA-Generative/ocr-api/commit/fd8c2048a460a1b29ba9c2430d5a74a054d497a8))
* tag for routes ([c5dfc77](https://github.com/IA-Generative/ocr-api/commit/c5dfc773d8f62c92fd103ffd9d177962958533aa))
* task_data not found ([f3f2173](https://github.com/IA-Generative/ocr-api/commit/f3f217374bbeaa190b5a8dcb1ca7a4560e40f616))
* tests ([1f79eec](https://github.com/IA-Generative/ocr-api/commit/1f79eec4d132ad833dc0037de32718523cc0603b))
* typo ([0db6fc3](https://github.com/IA-Generative/ocr-api/commit/0db6fc3d506ff3201ebd8b9771e065044275b0ec))
* up coverage ([5b21740](https://github.com/IA-Generative/ocr-api/commit/5b21740acf0cea2900a9c30c2950b63612a27709))
* up readme ([1105cc1](https://github.com/IA-Generative/ocr-api/commit/1105cc1b2265360da78ea77883a9ee667917af01))
* use define task type and status ([9d998c8](https://github.com/IA-Generative/ocr-api/commit/9d998c8b05cff1795cadd9e289c2c6338a0ea051))
* use dso pipeline ([d1f2617](https://github.com/IA-Generative/ocr-api/commit/d1f2617226bd2b96a7c1ada5f28a1133dac1639c))
* use file instead of memory ([8a6ab55](https://github.com/IA-Generative/ocr-api/commit/8a6ab5547d69b914566c6e575b408a2995fc8d23))
* use global config ([4c17b5f](https://github.com/IA-Generative/ocr-api/commit/4c17b5f22a1928770c3b06f20804e080bf228e9c))
* use minio ([3d1484d](https://github.com/IA-Generative/ocr-api/commit/3d1484d9e0b98895148dd2e537e2e1b839b12d3d))
* use pg ([2126d86](https://github.com/IA-Generative/ocr-api/commit/2126d8609bd5ab7c84e7d40c60e286dfe237734c))
* use real files ([92e76ce](https://github.com/IA-Generative/ocr-api/commit/92e76cee3afa75c3ce266ef098f08f8dfd91131c))
* uv ([a45191d](https://github.com/IA-Generative/ocr-api/commit/a45191dc5e9a84a7bee240dc31cc4cadea2d7698))
* version ([377b32d](https://github.com/IA-Generative/ocr-api/commit/377b32dc4f797f924e4a4f846130e1893e1de29c))
* warning ([d0a29b1](https://github.com/IA-Generative/ocr-api/commit/d0a29b1f160c2dbdd6e56eeb1ea99b9f10a1cc60))


### Documentation

* clean readme ([1d5e92d](https://github.com/IA-Generative/ocr-api/commit/1d5e92ddb6e65d5128edd405f3fc7cb3a59b60b5))

## 0.1.5 (2025-04-13)

### Feat

- add documentation
- add ci-cd

### Fix

- let user id
- add database url
- use define task type and status
- use dso pipeline
- en down
- up coverage
- pythonpath using export
- pythonpath
- launch anytime
- tests
- env file
- extras allow

## 0.1.4 (2025-04-13)

### Fix

- version

## v0.1.1 (2025-04-13)

### Feat

- add docekrfiles
- add ocr service
- add more extras
- add redis broker
- minio connection
- route jobs
- move route health

### Fix

- clean code with ruff
- use real files
- clean code
- ingore .db
- redis and minio sender
- size to send
- use minio
- use global config
- db
- use file instead of memory
- db creator
- tag for routes
- warning
- uv
- fastdeploy dir
- non root cache dir
- remove clean cache
- up readme
- async routes (#7)
- multi worker and thread
- async routes
