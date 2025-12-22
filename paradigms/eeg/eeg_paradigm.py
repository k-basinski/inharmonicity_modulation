# %%
import numpy as np
import serial
from psychopy import core, visual, sound, event, prefs, gui
import pandas as pd

prefs.hardware["audioLib"] = ["PTB"]
prefs.hardware["audioLatencyMode"] = 4


class Logger:

    config = {
        'fpath': 'logs/',
        'write_to_csv': True
    }
    log = []

    def __init__(self, pid) -> None:
        self.pid = pid
    
    def add_log(self, log_dict):
        log_dict['pid'] = self.pid
        log_dict['abs_time'] = core.getAbsTime()
        log_dict['time'] = core.getTime()
        self.log.append(log_dict)

    def save_log(self):
        df = pd.DataFrame(self.log)
        df.to_csv(f"{self.config['fpath']}p{self.pid}_log.csv")

    def save_demography(self, age, gender):
        df = pd.DataFrame({
            'pid': self.pid,
            'age': age,
            'gender': gender,
            'abs_time': core.getAbsTime()
        }, index=[0])
        df.to_csv(f"{self.config['fpath']}p{self.pid}_demo.csv")


class Paradigm:
    config = {
        "send_triggers": True,  # turn on/off sending triggers via serial port
        "soundpool_path": "soundpool_eeg/",
        "sounds_per_block": 600,  # how many sounds to play per block
        "frequencies": list(range(200, 550, 50)),  # which frequencies to probe
        "sp_max_index": 1000,  # max index of audio files in sound pool
        "deviant_probability": 0.2,  # probability of deviant
        "standards_at_start": 6,  # make sure this many standards are at the start of each block
        "standards_after_deviant": 3,  # make sure that at least this many standards are after each deviant
        "full_screen": False,  # should the app run full-screen
    }

    # default random number generator
    rng = np.random.default_rng()

    # blocks to run (if you want specific jitter like j2 or j4, use 2 and 4 as block index)
    blocks = [0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3, 4, 5, 6, 7]
    
    #blocks = [0, 1, 2, 3, 4, 5, 7, 2, 5]
    
    rng.shuffle(blocks)
    current_block = None

    def make_oddballs(self):
        """Make a list with classic oddball structure.

        Returns:
            list: A list of s's (standard) or d's (deviant).
        """
        out = ["s"] * self.config["standards_at_start"]
        i = self.config["standards_at_start"]

        while i < self.config["sounds_per_block"]:
            if self.rng.random() < self.config["deviant_probability"]:  # if deviant
                out.append("d")
                i += 1
                for _ in range(self.config["standards_after_deviant"]):
                    out.append("s")
                    i += 1
            else:
                out.append("s")
                i += 1

        return out
    
    def make_roving_oddballs(self):
        # frequency alphabet
        alphabet = self.config['frequencies']

        # repetitions
        repetitions = [4,5,6,7]

        # start with 10 standards
        seq = [self.rng.choice(alphabet)] * 10

        while len(seq) <= self.config["sounds_per_block"]:
            choose_f = self.rng.choice(alphabet)
            repeat = self.rng.choice(repetitions)
            if choose_f != seq[-1]: # rejection sampling
                for _ in range(repeat):
                    seq.append(choose_f)
        
        return seq


    def send_trigger(self, value):
        """
        Send a trigger to the port.

        Parameters:
            value (int): The value to send to the port.

        Returns:
            None
        """
        # make sure value is integer
        value_int = int(value)
        trig = value_int.to_bytes(1, "big")
        if self.config["send_triggers"]:
            self.win.callOnFlip(self.port.write, trig)
        else:
            print(f"{value_int} : trigger sent. ({trig})")

    def wait(self, seconds):
        """Wait an arbitrary number of seconds.

        Args:
            seconds (float): How many seconds to wait.
        """
        core.wait(seconds)

    def load_sound(self, fname):
        path = self.config["soundpool_path"] + fname
        s = sound.Sound(path, hamming=False, stereo=True)
        return s

    def play_sound(self, sound_object):
        """
        This function plays a sound from a sound pool on the next flip. It takes a sound object as input and uses the `win.getFutureFlipTime()` function to determine the next flip time. The sound is then played using the `sound.play()` method.

        Parameters:
            sound (object): The sound object to play.

        Returns:
            None
        """
        next_flip = self.win.getFutureFlipTime(clock="ptb")
        sound_object.play(when=next_flip)

    def calculate_trigger(self, isdev, block, blockstart=False):
        if isdev:
            stdev = 100
        else:
            stdev = 0

        if blockstart:
            stdev += 200

        return block+1 + stdev


    def show_splash_screen(self, message_text):
        self.message.text = message_text
        self.win.flip()
        event.waitKeys(keyList=["space"])

    def quit_exp(self):
        self.win.close()
        core.quit()

    def update_msg(self, sound_index=None, block_index=None, fname=None):
        self.message.text = f"""
        Running block {block_index} out of {len(self.blocks)}.\n 
        Playing sound {sound_index} out of {self.config['sounds_per_block']}\n File name {fname}."""

    def run_paradigm(self) -> None:

        if self.config["send_triggers"]:
            self.port = serial.Serial("/dev/tty.usbserial-D30C1INU", 115200)

        # make visual elements
        self.win = visual.Window(
            [800, 600], color="black", fullscr=self.config["full_screen"]
        )
        self.message = visual.TextBox2(
            self.win, text="", pos=(0, 0), letterHeight=0.05, alignment="center", autoDraw=True
        )

        # show id dialog box
        dlg = {"pid": np.random.randint(1000, 10000), "gender": "", "age": ""}
        gui.DlgFromDict(dlg, title="Demography", show=True)
        pid = dlg["pid"]

        # create quit key:
        event.globalKeys.add(key="escape", func=self.quit_exp, name="shutdown")

        # create logger
        logger = Logger(pid)
        logger.save_demography(dlg['age'], dlg['gender'])

        # make oddball list
        oddball_list = self.make_roving_oddballs()

        self.show_splash_screen("Experiment ready to start, press space.")

        for block_no, block in enumerate(self.blocks):
            self.current_block = block
            for io, o in enumerate(oddball_list):


                # pick random jitter pattern
                pattern = self.rng.integers(0, self.config["sp_max_index"])

                # build a filename to load the file
                fname = f"f{o}_j{block}_n{pattern}.wav"

                # preload the sound
                sobj = self.load_sound(fname)
                
                # update message on screen
                self.update_msg(io, block_no+1, fname)

                # wait some time
                self.wait(0.5)

                # que up sound playback and trigger sending on next flip
                self.play_sound(sobj)
                
                # detect deviant
                if (io == 0) or (o == oddball_list[io-1]):
                    isdev = False
                else:
                    isdev = True

                # set blockstart trigger
                if io < 10:
                    blockstart = True
                else: 
                    blockstart = False

                trig = self.calculate_trigger(isdev, block, blockstart)
                self.send_trigger(trig)
                
                logger.add_log({
                    'sound': o,
                    'block': block,
                    'jit_pattern': pattern,
                    'soundfile': fname
                })
                
                # send trigger and play sound on this win flip
                self.win.flip()


                # wait some more  
                self.wait(0.1)

            if block_no < (len(self.blocks) - 1):
                self.show_splash_screen(f"Block {block_no+1} finished. Press <space>.")

            logger.save_log()
        self.show_splash_screen("Experiment ended, press <space> to exit.")


pdigm = Paradigm()
pdigm.run_paradigm()


