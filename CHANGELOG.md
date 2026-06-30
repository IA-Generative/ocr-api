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

## [0.12.1](https://github.com/IA-Generative/ocr-api/compare/v0.12.0...v0.12.1) (2026-06-30)


### Bug Fixes

* **ci:** fix release for dso ([54ca48c](https://github.com/IA-Generative/ocr-api/commit/54ca48c5eada21c37f42cb5ce9cca7fa43aef143))

## [0.12.0](https://github.com/IA-Generative/ocr-api/compare/v0.11.2...v0.12.0) (2026-06-30)


### Features

* **mark:** add markdown ([68facd7](https://github.com/IA-Generative/ocr-api/commit/68facd7a65c88f145d421ba921acea534a73e880))

## [0.11.2](https://github.com/IA-Generative/ocr-api/compare/v0.11.1...v0.11.2) (2026-06-30)


### Bug Fixes

* **ocr:** add newer version ([4fa3ba3](https://github.com/IA-Generative/ocr-api/commit/4fa3ba3fab444ea6751b0715b13f047e625cadbd))

## [0.11.1](https://github.com/IA-Generative/ocr-api/compare/v0.11.0...v0.11.1) (2026-06-30)


### Bug Fixes

* **security:** fix security depandabot ([f476009](https://github.com/IA-Generative/ocr-api/commit/f476009b133d21b69d50350efb07db48f8cdd671))

## [0.11.0](https://github.com/IA-Generative/ocr-api/compare/v0.10.1...v0.11.0) (2026-06-30)


### Features

* add NoCacheMiddleware to prevent caching of responses ([d87f098](https://github.com/IA-Generative/ocr-api/commit/d87f098f97bd94069cd486e37a45f5e80812d6fc))
* add unit tests for QdrantVectorStore and collection management functionality ([bc02737](https://github.com/IA-Generative/ocr-api/commit/bc027370b9c04bc0f42605b017efe1b8895548f5))
* enhance error handling and logging in BaseWorker, update storage file path in tests ([c14a428](https://github.com/IA-Generative/ocr-api/commit/c14a428da2399551fa1cb85a4ca834663fc73515))
* enhance S3 file handling with download functionality and filename management ([ffdc3a4](https://github.com/IA-Generative/ocr-api/commit/ffdc3a4032e3b85ca0484219b278cbfb520f9cfd))
* **ocr:** aligne with abrege ([9959e24](https://github.com/IA-Generative/ocr-api/commit/9959e240ece10b62103ad05fe583097d9ad63d88))
* report errors to Sentry for api, worker and frontend ([#398](https://github.com/IA-Generative/ocr-api/issues/398)) ([12df704](https://github.com/IA-Generative/ocr-api/commit/12df704f5c0b781d7322e453c9b12d5258eef977))


### Bug Fixes

* **ci:** correct tracing test assertion and stabilize SDK tests ([#399](https://github.com/IA-Generative/ocr-api/issues/399)) ([50bb1fb](https://github.com/IA-Generative/ocr-api/commit/50bb1fb1ea9f96367ffd7236af39df562d69a605))
* **ci:** release ([abf4236](https://github.com/IA-Generative/ocr-api/commit/abf4236eec3ab1a705e96a41907b3a3b0cf938e5))
* improve cache handling in TaskCache and streamline NoCacheMiddleware response headers ([0274dcc](https://github.com/IA-Generative/ocr-api/commit/0274dccdaa3917f0bd8ef53e9dda74184c79b85a))
* vulne ([b544f56](https://github.com/IA-Generative/ocr-api/commit/b544f56d620ba3bdb2b5817ebb59702ba871fe62))

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
