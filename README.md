# ![Logo](./documents/logo.png)  zpipe

zpipe is a framework for concurrent and parallel pipelines. a zpipe pipeline has stages and workers. The stages can be the workers stage or non-worker stage. You can compose your pipeline with worker and non-worker stages together. Sicne the stages communicate to each other in pub/sub pattern, a stage can get inputs from many stage outputs. In zpipe, it is also possible to add dependencies between stages. For more details, please refer the zpipe documents

## Installation
```
pip install -r requirements.txt
pip install pyzpipe
```
