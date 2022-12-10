# litestream

## aws credentials

The following variables (AWS credentials) need to be set since they're used for replicating the database to aws:

- `LITESTREAM_ACCESS_KEY_ID`
- `LITESTREAM_SECRET_ACCESS_KEY`

These values are also accessed as arguments to docker run since the variables will allow for restoring the database to the docker container.

Enter the shell and export the proper values:

```sh
poetry shell
export LITESTREAM_ACCESS_KEY_ID=xxx
export LITESTREAM_SECRET_ACCESS_KEY=yyy
```

## copy local database to cloud aws

Run the following replication command:

```console
litestream replicate -trace logs db/x.db s3://corpus-x/db
```

This will produce the following lines:

```console
litestream v0.3.9
initialized db: /path/to/db/x.db
replicating to: name="s3" type="s3" bucket="corpus-x" path="db" region="" endpoint="" sync-interval=1s
path/to/db/x.db: sync: new generation "xxxxxxxx", no generation exists
```

Can view progress of  replication process via MacOS's Activity Monitor / Network panel.

Considering the size of the database, it will take sometime to upload. After the replication, the following line appears:

```console
path/to/db/x.db(s3): snapshot written d4cb93a1d08cbeb2/00000000
```

## setup requirements.txt

```console
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## pre-requisite docker

Ensure Docker for Mac is [installed](https://docs.docker.com/desktop/install/mac-install/) and updated.

## review dockerfile

Ensure existence of a valid Dockerfile in root directory and applicable versions of:

1. `python`
2. `litestream`
3. `sqlite`

## dockerfile

Can create the docker image with:

```console
docker build -t corpus-x . # Will look for Dockerfile inside the . folder
```

This will start the build process. If successful, the docker image will be built and appear in the list of Docker Images found in VS Code's Docker extension.

Run the docker image locally with:

```console
docker run \
  -p 8080:8080 \
  -e LITESTREAM_ACCESS_KEY_ID \
  -e LITESTREAM_SECRET_ACCESS_KEY \
  -e LAWSQL_BOT_TOKEN \
  corpus-x
```

## restore via run.sh

The dockerfile terminates with [run.sh](../scripts/run.sh).

Since, on initialization, the sqlite database file doesn't exist yet, it will use litestream's `restore` command to copy the aws variant to local container.

```console
No database found, restoring from replica if exists
2022/12/10 05:42:11.906021 s3: restoring snapshot xxx/00000000 to /db/x.db.tmp
2022/12/10 05:43:45.299375 s3: restoring wal files: generation=xxx index=[00000000,00000000]
2022/12/10 05:43:45.494176 s3: downloaded wal xxx/00000000 elapsed=191.820083ms
2022/12/10 05:43:45.566760 s3: applied wal xxx/00000000 elapsed=73.156208ms
2022/12/10 05:43:45.566865 s3: renaming database from temporary location
INFO:     Started server process [15]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
```
