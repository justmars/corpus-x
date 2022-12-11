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
litestream replicate x.db s3://corpus-x/db
```

This will produce the following lines:

```console
litestream v0.3.9
initialized db: /path/to/db/x.db
replicating to: name="s3" type="s3" bucket="corpus-x" path="db" region="" endpoint="" sync-interval=1s
path/to/db/x.db: sync: new generation "xxxxxxxx", no generation exists
```

## monitor upload

See replication / upload progress in MacOS's _Activity Monitor_ / _Network_ panel.

Considering the size of the database, it will take sometime to upload.

After the replication, the following line should appear in the console:

```console
path/to/db/x.db(s3): snapshot written xxx/00000000
```
