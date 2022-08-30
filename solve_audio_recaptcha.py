from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager as cdm
import speech_recognition as sr
from pydub import AudioSegment
import time
import requests


def main():
    opt = webdriver.chrome.options.Options()
    opt.headless = False
    # opt.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(cdm().install()), options=opt)

    URL = 'https://www.google.com/recaptcha/api2/demo'
    
    driver.get(URL)

    try:
        find_and_handel_recaptcha(driver)
    except:
        print('could not solve catpcha :(')
        
    time.sleep(2)
    print('I am human.')

    
def is_visual_recaptcha_available(driver):
    challenge_frame = driver.find_element(By.XPATH, "//iframe[@title='recaptcha challenge expires in two minutes']")
    driver.switch_to.frame(challenge_frame)
    is_visual_captch_available = True
    try:
        driver.find_element(By.XPATH, "//div[@id='rc-imageselect']")
        is_visual_captch_available = True
    except:
        print('not a challenge avilable on page.')
        is_visual_captch_available = False
    finally:
        driver.switch_to.default_content()
        
    return is_visual_captch_available


def save_audio_captcha(driver, fname):
    challenge_frame = driver.find_element(By.XPATH, "//iframe[@title='recaptcha challenge expires in two minutes']")
    driver.switch_to.frame(challenge_frame)
    driver.find_element(By.XPATH, "//button[@title='Get an audio challenge']").click()

    driver.switch_to.default_content()
    challenge_frame = driver.find_element(By.XPATH, "//iframe[@title='recaptcha challenge expires in two minutes']")

    driver.switch_to.frame(challenge_frame)
    time.sleep(3) # critical delay
    src = driver.find_element(By.XPATH, "//audio[@id='audio-source']").get_attribute('src')
    
    driver.switch_to.default_content()

    res = requests.get(src)
    open(fname, 'wb').write(res.content)

    return src

def speech_to_text(fname):
    AudioSegment.from_mp3(fname).export(f"./{fname}.wav", format="wav")
    text = '**did not understand**'
    r = sr.Recognizer()
    with sr.AudioFile(f'./{fname}.wav') as source:
        audio = r.record(source)  # read the entire audio file

    try:
        text = r.recognize_google(audio)
        print("Google Speech Recognition: " + text)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    return text

def enter_text_recaptch(driver, text):
    challenge_frame = driver.find_element(By.XPATH, "//iframe[@title='recaptcha challenge expires in two minutes']")
    driver.switch_to.frame(challenge_frame)
    driver.find_element(By.XPATH, "//input[@id='audio-response']").send_keys(text)
    time.sleep(0.5)
    driver.find_element(By.XPATH, "//button[@id='recaptcha-verify-button']").click()

    driver.switch_to.default_content()


def find_and_handel_recaptcha(driver):
    # find recaptcha:
    WebDriverWait(driver, 15).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")))
    time.sleep(1)
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//span[@id='recaptcha-anchor']"))).click()
    time.sleep(1)
    driver.switch_to.default_content()
    
    if is_visual_recaptcha_available(driver):
        print('visual capttcha avail ... ')
        # solve the audio challenge:
        save_audio_captcha(driver, 'audio.mp3')
        text = speech_to_text('audio.mp3')
        enter_text_recaptch(driver, text)
    else:
         print('visual captcha NOT avail ... ')
    
    time.sleep(0.5)


if __name__ == '__main__':
    main()