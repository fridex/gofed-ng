import sys
from common.helpers.utils import json_pretty_format
from common.service.computationalService import StorageService
from common.service.serviceEnvelope import ServiceEnvelope

class Storage0001Service(StorageService):
	def exposed_storage0001(self):
		return "foo"

if __name__ == "__main__":
	ServiceEnvelope.serve(Storage0001Service)

