import borgapi
import datetime
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily as Metric, REGISTRY
import argparse
import logging
import os

logger = logging.getLogger(__name__)


def metric(name: str, docs: str, labels, value):
	last_modified = Metric(name, docs, labels=labels.keys())
	last_modified.add_metric(labels=labels.values(), value=int(value))
	return last_modified


class Collector:
	def __init__(self, repo_config: str):
		self.repo_configs = {}
		repo_configs = repo_config.split(',')
		for config in repo_configs:
			data = config.split('=')
			self.repo_configs[data[0].strip()] = data[1].strip()
		logger.info("repo_configs: %s", self.repo_configs.keys())

	def collect(self):
		for repo, passprahrase in self.repo_configs.items():
			api = None
			try:
				api = borgapi.BorgAPI(defaults={}, options={})
				api.set_environ(dictionary={"BORG_PASSPHRASE": passprahrase})
				api.set_environ(dictionary={"BORG_RELOCATED_REPO_ACCESS_IS_OK": 1})
			except Exception as e:
				logger.error("Borg Repo not found or Passphrase invalid: %s", e)

			try:
				info = api.info(repo, json=True)
				yield metric("last_modified", 'Last modified Timestamp in seconds', {"repo": repo},
								 datetime.datetime.fromisoformat(info["repository"]["last_modified"]).strftime("%s"))
				yield metric("total_size", 'Total Size of Backup in Bytes', {"repo": repo},
								 info["cache"]["stats"]["total_csize"])
				yield metric("original_size", 'Original Size of Backup in Bytes', {"repo": repo},
								 info["cache"]["stats"]["total_size"])
				yield metric("deduplicated_size", 'Deduplicated Size of Backup in Bytes', {"repo": repo},
								 info["cache"]["stats"]["unique_csize"])
			except Exception as e:
				logger.debug("Error loading infos %s", e)

			last = None
			try:
				list_info = api.list(repo, json=True)
				archives = list_info["archives"]
				yield metric("archive_count", 'Total amount of backups', {"repo": repo}, len(archives))
				archives.sort(key=lambda repo: datetime.datetime.fromisoformat(repo["time"]))
				last = archives[-1]
			except Exception as e:
				logger.debug("Error listing backups %s", e)

			try:
				lastinfo = api.info(f"{repo}::{last["name"]}", json=True)
				last_stats = lastinfo["archives"][0]["stats"]
				yield metric("last_archive_compressed_size", 'Compressed Size of last Archive in Bytes', {"repo": repo},
								 int(last_stats["compressed_size"]))
				yield metric("last_archive_deduplicated_size", 'Deduplicated Size of last Archive in Bytes',
								 {"repo": repo},
								 int(last_stats["deduplicated_size"]))
				yield metric("last_archive_original_size", 'Original Size of last Archive in Bytes', {"repo": repo},
								 int(last_stats["original_size"]))
				yield metric("last_archive_file_count", 'Total amount of files in last Archive', {"repo": repo},
								 int(last_stats["nfiles"]))
			except Exception as e:
				logger.debug("Error loading last backup %s", e)


if __name__ == '__main__':
	logger.setLevel(logging.DEBUG)
	ch = logging.StreamHandler()
	ch.setLevel(os.environ.get('LOGLEVEL', 'INFO').upper())
	ch.setFormatter(logging.Formatter('%(levelname)s:%(message)s'))
	logger.addHandler(ch)
	parser = argparse.ArgumentParser()

	parser.add_argument("-p", "--listen-port", help="Listen on this port", type=int, default=9099)
	parser.add_argument("-b", "--bind-addr", help="Bind this address", default="localhost")
	args = parser.parse_args()
	logger.info("Arguments: %s", args)

	if os.environ.get('REPO_CONFIG') is None:
		logger.error("REPO_CONFIG Env missing")
		exit(1)

	REGISTRY.register(Collector(os.environ.get('REPO_CONFIG')))

	server, thread = start_http_server(args.listen_port, addr=args.bind_addr)
	logger.info("Starting on %s:%s" % (server.server_address, server.server_port))
	thread.join()
