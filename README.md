# borg-prometheus-exporter

## Usage

``docker run ghcr.io/h3rmt/borg-prometheus-exporter:latest -b 0.0.0.0 -p 9099``

## Configuration

The parameters can be listed py running ``borg-prometheus-exporter.py -h``

```
usage: borg-prometheus-exporter.py [-h] [-p LISTEN_PORT] [-b BIND_ADDR]

options:
  -h, --help            show this help message and exit
  -p LISTEN_PORT, --listen-port LISTEN_PORT
                        Listen on this port
  -b BIND_ADDR, --bind-addr BIND_ADDR
                        Bind this address
```

The passprahrase used to decrypt to the Borg repo is read from the environment variable `REPO_CONFIG` (format:
``path/to/repo=febo8ih3fo2qdnwaof9hn-a9h-fa3, /repo=fbei1o2nfe0823nf02380823fn3, /repo2=/run/agenix/secret_passphrase``).

**IMPORTANT**: If the passhprase is stored in a file the path must be absolute

## Exported metrics

| Name                           | Description                                |
|--------------------------------|--------------------------------------------|
| last_modified                  | Last modified Timestamp in seconds         |
| total_size                     | Total Size of Backup in Bytes              |
| original_size                  | Original Size of Backup in Bytes           |
| deduplicated_size              | Deduplicated Size of Backup in Bytes       |
| archive_count                  | Total amount of backups                    |
| last_archive_compressed_size   | Compressed Size of last Archive in Bytes   |
| last_archive_deduplicated_size | Deduplicated Size of last Archive in Bytes |
| last_archive_original_size     | Original Size of last Archive in Bytes     |
| last_archive_file_count        | Total amount of files in last Archive      |