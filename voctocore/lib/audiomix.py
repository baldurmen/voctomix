#!/usr/bin/python3
import logging
from gi.repository import Gst
from enum import Enum

from lib.config import Config

class AudioMix(object):
	log = logging.getLogger('AudioMix')

	mixingPipeline = None

	caps = None
	names = []

	selectedSource = 0

	def __init__(self):
		self.caps = Config.get('mix', 'audiocaps')

		self.names = Config.getlist('mix', 'sources')
		self.log.info('Configuring Mixer for %u Sources', len(self.names))

		pipeline = """
			audiomixer name=mix !
			{caps} !
			interaudiosink channel=audio_mix
		""".format(
			caps=self.caps
		)

		for idx, name in enumerate(self.names):
			pipeline += """
				interaudiosrc channel=audio_{name}_mixer !
				{caps} !
				mix.
			""".format(
				name=name,
				caps=self.caps
			)

		self.log.debug('Creating Mixing-Pipeline:\n%s', pipeline)
		self.mixingPipeline = Gst.parse_launch(pipeline)

		self.log.debug('Initializing Mixer-State')
		self.updateMixerState()

		self.log.debug('Launching Mixing-Pipeline')
		self.mixingPipeline.set_state(Gst.State.PLAYING)

	def updateMixerState(self):
		self.log.info('Updating Mixer-State')

		for idx, name in enumerate(self.names):
			volume = int(idx == self.selectedSource)

			self.log.debug('Setting Mixerpad %u to volume=%0.2f', idx, volume)
			mixerpad = self.mixingPipeline.get_by_name('mix').get_static_pad('sink_%u' % idx)
			mixerpad.set_property('volume', volume)

	def setAudioSource(self, source):
		self.selectedSource = source
		self.updateMixerState()