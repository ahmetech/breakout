import pygame
import os
import glob
import time
from utilities.common import rm

from pygame.locals import *


def get_sound_list():
    """ gets a list of sound names without thier path, or extension.
    """
    # load a list of sounds without path at the beginning and .ogg at the end.
    sound_list = map(lambda x: os.path.basename,
                     glob.glob(rm.getSoundPath("*.wav"))
                    )
    return sound_list

SOUND_LIST = get_sound_list()

class SoundManager:
    """ Controls loading, mixing, and playing the sounds.
        Having seperate classes allows different groups of sounds to be 
         loaded, and unloaded from memory easily.

        Useage:
            sm = SoundManager()
            sm.play("bump")
    """


    def __init__(self):
        """
        """
        # keyed by the sound name, value is a sound object.
        self.sounds = {}

        # keyed by sound name, value is the channel.
        self.chans = {}

        self._debug_level = 0

        # sounds which are queued to play.
        self.queued_sounds = []

    def _debug(self, x, debug_level = 0):
        """ Used for optionally printing debug messages.
        """
        if self._debug_level > debug_level:
            print x



    def load(self, names = SOUND_LIST):
        """Loads sounds."""
        sounds = self.sounds

        if not pygame.mixer:
            for name in names:
                sounds[name] = None
            return
        for name in names:
            if not sounds.has_key(name):
                fullname = rm.getSoundPath(name+'.wav')
                try: 
                    sound = pygame.mixer.Sound(fullname)
                except: 
                    sound = None
                    self._debug("Error loading sound", fullname)
                sounds[name] = sound


    def _getSound(self, name):
        """ Returns a Sound object for the given name.
        """
        if not self.sounds.has_key(name):
            self.load([name])

        return self.sounds[name]



    def play(self, name, volume=[1.0, 1.0], wait = 0):
        """ Plays the sound with the given name.
            name - of the sound.
            volume - left and right.  Ranges 0.0 - 1.0
            wait - used to control what happens if sound is allready playing:
                0 - will not wait if sound playing.  play anyway.
                1 - if there is a sound of this type playing wait for it.
                2 - if there is a sound of this type playing do not play again.
        """

        vol_l, vol_r = volume

        sound = self._getSound(name)

        if sound:
            # check to see if we want to do any sound queueing, and handle it.
            if wait in [1,2]:
                # check if the sound is allready playing, and is busy...
                if self.chans.has_key(name) and self.chans[name].get_busy():
                    if wait == 1:
                        # sound is allready playing we wait for it to finish.
                        self.queued_sounds.append((name, volume, wait))
                        return
                    elif wait == 2:
                        # not going to play sound if playing.  We do nothing.
                        return
                        
            # play the sound, and store its channel in a 
            #   dictionary, keyed by the sound name.
            self.chans[name] = sound.play()

            # if the sound did not play, start fading out a channel, and 
            #   use pygames queueing to queue up a sound on that channel.
            if not self.chans[name]:
                # forces a channel to return. we fade that out,
                #  and enqueue our one.
                self.chans[name] = pygame.mixer.find_channel(1)
                self.chans[name].fadeout(100)
                self.chans[name].queue(sound)

            # if we have a channel, set its volume.
            if self.chans[name]:
                self.chans[name].set_volume(vol_l, vol_r)



    def update(self, elapsed_time):
        """ This should be called frequently.  At least once every game tic/frame.
        """
        # if the sound for the channel is not busy we 
        for name in self.chans.keys():
            if not self.chans[name].get_busy():
                del self.chans[name]
        # copy the current queue, to the old queue.
        old_queued = self.queued_sounds

        # start a new queue.
        self.queued_sounds = []

        # Try and play any sounds from the old queue.
        #   This may queue the sounds again, if they still shouldn't be played.
        for snd_info in old_queued:
            name, volume, wait = snd_info
            self.play(name, volume, wait)
