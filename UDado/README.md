# How to launch microDADO using Docker

First, you need to build the image

```bash
docker build . -t padec/microdado
```

Then, you can execute it with `docker run`:

```bash

docker run -v /path/to/your/input/json:/indata/input-json -v /path/to/your/output/dir:/outdata padec/microdado
```
