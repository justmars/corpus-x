# fly.io

## initialization

Debug:

```console
fly doctor
fly agent restart
```

## app creation

Check existing names then create the fly app with a unique name:

```console
fly apps list
fly apps create corpus-x
```

## volume creation

- After creating the app, can create a volume that will be used by the app for persistent storage:

  ```console
  fly volumes create corpus_x_data --region sin --size 3
  fly volumes list
  ```

## setup config

Review the contents of [fly.toml](../fly.toml), specifically the `app_name` and the `mount.source`

```toml
app = "corpus-x" # this was the name set during creation of the app
[env]
FLY_PRIMARY_REGION = "sin" # this is the region set during creation of the app's volume
[mounts]
source = "corpus_x_data" # this was the name set during creation of the app's volume; can verify this with fly volumes list
destination = "/data" # this is the folder to be created in the app for persistent storage
```

## set environment vars

Set the environment variables of the app:

```console
fly --app corpus-x secrets set \
LITESTREAM_ACCESS_KEY_ID=x \
LITESTREAM_SECRET_ACCESS_KEY=y \
LAWSQL_BOT_TOKEN=z
```

The `LITESTREAM_ACCESS_KEY_ID` and `LITESTREAM_SECRET_ACCESS_KEY` aws credentials are used by _litestream.io_ to [restore a replica](../app/scripts/run.sh) of a [previously saved and replicated](./4-container.md#copy-local-database-to-cloud-aws) database to the volume created.

The `LAWSQL_BOT_TOKEN` is the credential needed to query the database after it is restored.

## build local image then deploy to fly

Use the local Dockerfile to build the image before deploying the same to fly.io

```console
fly deploy --local-only
```

This will result in the following lines:

```console
==> Verifying app config
--> Verified app config
==> Building image
==> Creating build context
--> Creating build context done
==> Building image with Docker
--> docker host: 20.10.21 linux aarch64
...
```

Substantive steps of the Dockerfile to create the Docker image

Step | Description | Time (seconds)
:--:|:--:|:--
2 | Building python slim with relevant libs | ~120
5 | Building sqlite with extensions | ~420
7 | Install requirements.txt | ~60

After the image is built, this will push the image to fly:

```console
--> Building image done
==> Pushing image to fly
The push refers to repository [registry.fly.io/corpus-x]
...
deployment-aaa: xxx
--> Pushing image done
image: registry.fly.io/corpus-x:deployment-aaa
image size: 323 MB
==> Creating release
--> release v2 created

--> You can detach the terminal anytime without stopping the deployment
```

## test

With the url set at: `corpus-x.fly.dev`, the database file at `x.db`, and the secret previously set for `LAWSQL_BOT_TOKEN`, can test a json list of tables with:

```console
export token=<whatever-value-of-LAWSQL_BOT_TOKEN>
curl -H "Authorization: Bearer ${token}" \
https://corpus-x.fly.dev/x.json | jq
```

Without the token:

```console
curl -I -X GET https://corpus-x.fly.dev/x
```

Produces a _FORBIDDEN_ 403 http status code:

```console
HTTP/2 403
date: x x x x
server: Fly/x x x
content-type: text/html; charset=utf-8
via: 2 fly.io
fly-request-id: x x x-sin
```
