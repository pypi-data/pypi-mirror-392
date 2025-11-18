# kong-sdk-python

## [Generating python code for gRPC service](https://github.com/grpc/grpc/tree/master/tools/distrib/python/grpcio_tools#usage)

```shell
cd ./packages/kong-sdk-python
poetry run python -m grpc_tools.protoc --proto_path=./src/kong/proto --python_out=./src/kong/proto --grpc_python_out=./src/kong/proto ./src/kong/proto/service.proto
```

> Change import to `from kong.proto import service_pb2 as service__pb2
`

## Packaging and publishing SDK

Update SDK version in `pyproject.toml`:

```toml
[tool.poetry]
name = "kong-sdk"
version = <version>
```

```shell script
npx nx install kong-sdk-python
npx nx build kong-sdk-python
npx nx publish kong-sdk-python --user=<user> --password=<password>
```

> Link to the `nexus` repository is specified in `/poetry.toml`
