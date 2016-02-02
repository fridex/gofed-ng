import sys
from common.helpers.utils import json_pretty_format
from common.service.computationalService import ComputationalService
from common.service.serviceEnvelope import ServiceEnvelope

class Computational0001Service(ComputationalService):
	''' This is an example of a service '''

	@classmethod
	def signal_startup(cls, config):
		print("got startup signal")
		print json_pretty_format(config)

	@classmethod
	def signal_termination(cls):
		print("got termination signal")

	def signal_connect(self):
		print("got connect signal")

	def signal_disconnect(self):
		print("got disconnect signal")

	def signal_process(self):
		print("got process signal")

	def signal_processed(self):
		print("got processed signal")

	def exposed_computational0001(self, project, commit):
		print("inside action1")
		return project + commit

if __name__ == "__main__":
	ServiceEnvelope.serve(Computational0001Service)

