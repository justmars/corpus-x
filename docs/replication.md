# Replication to AWS

## Config file

View the `litestream.yml` which lists down the various env variables that need to be set:

var | desc | notes
--:|:--|--
`LITESTREAM_ACCESS_KEY_ID` | aws access id | starts with `AKIA`
`LITESTREAM_SECRET_ACCESS_KEY` | aws secret key | see password manager
`REPLICA_URL` | must have an aws s3 bucket | s3://bucket/path
`DB_FILE` | the db path | *.db that will be replicated to the aws s3 bucket

## Set credentials that config will use

Enter the shell and export the proper values:

```sh
poetry shell
export DB_FILE=a-name-of-a-db.db
export LITESTREAM_ACCESS_KEY_ID=AKIAxxx
export LITESTREAM_SECRET_ACCESS_KEY=xxx
export REPLICA_URL=s3://bucket/path
```

## Use config to litestream local db to aws bucket

Run the following replication command:

```console
litestream replicate -config litestream.yml
```

This will produce the following lines:

```console
litestream v0.3.9
initialized db: /path/to/db/x.db
replicating to: name="s3" type="s3" bucket="corpus-x" path="db" region="" endpoint="" sync-interval=1s
path/to/db/x.db: sync: new generation "xxxxxxxx", no generation exists
```

## Monitor upload

See replication / upload progress in MacOS's *Activity Monitor* / *Network* panel.

Considering the size of the database, it will take sometime to upload.

After the replication, the following line should appear in the console:

```console
path/to/db/x.db(s3): snapshot written xxx/00000000
```

## Check successful replication

View the aws s3 [bucket](https://s3.console.aws.amazon.com/s3/buckets/) and confirm existence of a new generation.
