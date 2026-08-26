import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" 
import pygame

class SoundManager:
    _initialized = False

    @classmethod
    def init(cls):
        if not cls._initialized:
            pygame.mixer.init()
            cls._initialized = True

    @classmethod
    def play(cls, filename,maxtime=0):
        if not cls._initialized:
            return
            
        filepath = os.path.join("assets", "sounds", filename)
        
        try:
            if os.path.exists(filepath):
                sound = pygame.mixer.Sound(filepath)
                if maxtime > 0:
                    sound.play(maxtime=maxtime) 
                else:
                    sound.play()
            else:
                print(f"[Audio] Missing file: {filepath}")
        except Exception as e:
            print(f"[Audio] Error playing {filename}: {e}")

    @classmethod
    def play_click(cls):
        cls.play("click.wav")

    @classmethod
    def play_coin(cls):
        cls.play("coin.wav")

    @classmethod
    def play_eat(cls):
        cls.play("eat.wav")
        
    @classmethod
    def play_error(cls):
        cls.play("error.wav")

    @classmethod
    def play_cat(cls):
        cls.play("cat.wav")

    @classmethod
    def play_dog(cls):
        cls.play("dog.wav")
        
    @classmethod
    def play_intro(cls):
        cls.play("intro.wav")
    
    @classmethod
    def play_intro(cls):
        cls.play("sleep.wav")