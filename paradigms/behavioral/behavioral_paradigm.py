import numpy as np
from psychopy import gui, core, visual, data, event, sound, prefs
import pandas as pd

prefs.hardware["audioLib"] = ["PTB"]
prefs.hardware["audioLatencyMode"] = 3
event.globalKeys.add(key="q", modifiers=["ctrl"], func=core.quit)
event.globalKeys.add(key="escape", func=core.quit)

soundpool_path = "soundpool_behavioral/"
soundpool_path2 = "soundpool2/"

# how many rounds
max_rounds = 16


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



dlg = {"ID": "", "gender": "", "age": ""}
gui.DlgFromDict(dlg, title="Dane demograficzne", show=True)
pid = int(dlg["ID"])

# create logger
logger = Logger(pid)
logger.save_demography(dlg['age'], dlg['gender'])


win = visual.Window(fullscr=True)
message = visual.TextBox2(
    win, text="", pos=(0, 0), letterHeight=0.05, alignment="center"
)
win.flip()

responses, targets, increments, n1_list, n2_list = [], [], [], [], []
rng = np.random.default_rng()
clck = core.Clock()

def beep(jitter):
    """Beep twice with increments and return correct response."""
    base_f = rng.choice(np.arange(250, 460, 10))
    difference = 50
    lower_higher = rng.choice(["lower", "higher"])

    n1, n2 = rng.choice(np.arange(0, 100), 2)
    if lower_higher == "lower":
        s1f = base_f
        s2f = base_f - difference
    elif lower_higher == "higher":
        s1f = base_f
        s2f = base_f + difference

    s1file = f"{soundpool_path}f{s1f}_j{jitter}_n{n1}.wav"
    s2file = f"{soundpool_path}f{s2f}_j{jitter}_n{n2}.wav"
    print(f"Pierwszy dźwięk: {s1file}")
    print(f"Drugi dźwięk: {s2file}")
    s1 = sound.Sound(s1file, stereo=True)
    s2 = sound.Sound(s2file, stereo=True)
    core.wait(0.2)
    s1.play()
    core.wait(0.5)
    s2.play()
    clck.reset()
    core.wait(0.3)

    return lower_higher, n1, n2


def pierwsza_czesc():
    sound_pool = {
        "pair_0_392Hz_second_higher.wav": "up",
        "pair_1_439Hz_second_higher.wav": "up",
        "pair_2_426Hz_second_lower.wav": "down",
        "pair_3_358Hz_second_lower.wav": "down",
        "pair_4_409Hz_second_higher.wav": "up",
        "pair_5_332Hz_second_higher.wav": "up",
        "pair_6_489Hz_second_lower.wav": "down",
        "pair_7_301Hz_second_lower.wav": "down",
        "pair_8_458Hz_second_lower.wav": "down",
        "pair_9_489Hz_second_higher.wav": "up",
        "pair_10_339Hz_second_higher.wav": "up",
        "pair_11_456Hz_second_lower.wav": "down",
        "pair_12_413Hz_second_higher.wav": "up",
        "pair_13_323Hz_second_lower.wav": "down",
        "pair_14_415Hz_second_lower.wav": "down",
        "pair_15_442Hz_second_lower.wav": "down",
        "pair_16_424Hz_second_higher.wav": "up",
        "pair_17_400Hz_second_higher.wav": "up",
        "pair_18_418Hz_second_lower.wav": "down",
        "pair_19_391Hz_second_lower.wav": "down",
    }

    introduction_text = (
        "Witaj w eksperymencie!\n\n"
        "Za chwilę usłyszysz pary dzwięków jeden po drugim.\n\n"
        "Twoim zadaniem będzie ocenić, czy drugi dźwięk jest wyższy czy niższy od pierwszego.\n\n"
        "Jeśli drugi dźwięk jest wyższy, naciśnij <strzałka w górę>.\n"
        "Jeśli drugi dźwięk jest niższy, naciśnij <strzałka w dół>.\n\n"
        "Przed tobą zadanie próbne, dzięki któremu lepiej zrozumiesz badanie.\n"
        "Naciśnij spację, aby rozpocząć."
    )
    message.text = introduction_text
    message.draw()
    win.flip()
    event.waitKeys(keyList=["space"])

    rng = np.random.default_rng()
    n_correct = 0

    while n_correct < 2:
        i = rng.integers(0, len(sound_pool))
        current_sound = list(sound_pool.keys())[i]
        correct_answer = sound_pool[current_sound]

        message.text = "strzałka w górę - jeśli drugi dzwięk jest wyższy od pierwszego\nw dół - jeśli drugi dzwięk jest niższy od pierwszego"
        message.draw()
        win.flip()

        s = sound.Sound(f"{soundpool_path2}{current_sound}")
        s.play()
        core.wait(1)

        keys = event.waitKeys(keyList=["up", "down", "escape"])
        if "escape" in keys:
            core.quit()

        response = keys[0]

        if response == correct_answer:
            feedback_text = "Odpowiedziałeś poprawnie!"
            n_correct += 1
        else:
            feedback_text = (
                f"Wcisnąłeś: {'strzałkę w górę' if response == 'up' else 'strzałkę w dół'}\n"
                f"Powinieneś wcisnąć: {'strzałkę w górę' if correct_answer == 'up' else 'strzałkę w dół'}\n\n"
                "Odpowiedziałeś niepoprawnie. Spróbuj ponownie."
            )
            n_correct = 0

        message.text = feedback_text + "\n\nNaciśnij spację, aby kontynuować."
        message.draw()
        win.flip()

        event.waitKeys(keyList=["space"])

        print(f"Liczba poprawnych odpowiedzi z rzędu: {n_correct}")


def druga_czesc():


    message.text = (
        "Gratulacje!\n\n"
        "Teraz przechodzimy do części właściwej.\n\n"
        "Polecenie zostaje to samo, jedynie dzwięki będą trochę inne.\n\n"
        "Naciśnij dowolny klawisz, aby rozpocząć."
    )
    message.draw()
    win.flip()

    event.waitKeys()

    for runda in range(1, max_rounds):
        start_val = rng.choice([0, 10])

        message.text = f"Przed tobą {runda} z {max_rounds} części. .\n\nNaciśnij dowolny klawisz, aby kontynuować."
        message.draw()
        win.flip()

        event.waitKeys()

        print(f"kolejna runda {runda}")

        staircase = data.StairHandler(
            startVal=start_val,
            stepType="lin",
            nReversals=6,
            stepSizes=[1],
            minVal=0,
            maxVal=10,
            nUp=3,
            nDown=1,
            nTrials=1,
        )

        for stair in staircase:
            rev_jitter = stair
            message.text = f"Jeśli drugi dźwięk wyżej, <strzałka w góre>.\nJeśli drugi dźwięk niżej, <strzałka w dół>.\n\nIncrement: {rev_jitter}..."
            # message.draw()
            win.flip()

            target, n1, n2 = beep(rev_jitter)

            thisResp = None
            while thisResp is None:
                allKeys = event.waitKeys()
                for thisKey in allKeys:
                    if thisKey == "down":
                        if target == "lower":
                            thisResp = -1
                        else:
                            thisResp = 1
                    elif thisKey == "up":
                        if target == "higher":
                            thisResp = -1
                        else:
                            thisResp = 1
                    elif thisKey in ["q", "escape"]:
                        core.quit()

                event.clearEvents()

            responses.append(allKeys[0])
            targets.append(target)
            increments.append(stair)
            n1_list.append(n1)
            n2_list.append(n2)
            
            log = {"responses": allKeys[0], "targets": target, "jitter": stair, "n1": n1, "n2": n2, "rt": clck.getTime()}
            logger.add_log(log)

            staircase.addData(thisResp)


        logger.save_log()

pierwsza_czesc()
druga_czesc()
core.quit()
