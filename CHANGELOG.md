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

## [1.4.0](https://github.com/IA-Generative/ocr-api/compare/v1.3.0...v1.4.0) (2025-05-28)


### Features

* purge feature ([#31](https://github.com/IA-Generative/ocr-api/issues/31)) ([c1f5c9c](https://github.com/IA-Generative/ocr-api/commit/c1f5c9ca1e6b7172b4e97f1b7452a74984242903))

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
