import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from Reader import Reader
import pandas as pd
from datetime import datetime
from pathlib import Path
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException


proxies = ["http://45.12.106.119:12323", "http://45.40.121.73:12323", "http://45.40.121.64:12323"]
#temp_path = Path("/Users/justinwild/Downloads/Ariva_Temp")
temp_path = Path("//Master/F/User/Microsoft Excel/Privat/Börse/historische_Kurse/temp")
#save_path = Path("/Users/justinwild/Downloads/")
save_path = Path("//Master/F/User/Microsoft Excel/Privat/Börse/historische_Kurse")


def get_proxy_for_index(index: int) -> str:
    if index < 1700:
        return proxies[2]
    elif index < 3400:
        return proxies[1]
    else:
        return proxies[0]


def build_ariva_urls(df: pd.DataFrame) -> list[str]:
    df = df.copy()

    # Datum normalisieren (das bleibt wie gehabt)
    df["eingelesen_bis"] = (
        pd.to_datetime(
            df["eingelesen_bis"],
            format="%d.%m.%Y",
            errors="raise"
        )
        .dt.strftime("%d.%m.%Y")
    )

    today = datetime.today().strftime("%d.%m.%Y")
    urls: list[str] = []

    for _, row in df.iterrows():
        wkn = str(row["WKN"])
        secu = str(row["secu"])
        boerse_id = str(row["Boerse_ID"])
        min_time = str(row["eingelesen_bis"])

        url = (
            "https://www.ariva.de/quote/historic/historic.csv?"
            f"secu={secu}"
            f"&boerse_id={boerse_id}"
            "&clean_split=1"
            "&clean_payout=0"
            "&clean_bezug=1"
            f"&min_time={min_time}"
            f"&max_time={today}"
            "&trenner=%3B"
            "&go=Download"
            f"&wkn={wkn}"
        )

        urls.append(url)
    print("URLs erzeugt:", len(urls))
    return urls

def login(driver, username= '20211808_Marco', password= 'Sally_13_2025!'):
    driver.get("https://login.ariva.de/realms/ariva/protocol/openid-connect/auth?client_id=ariva-web&redirect_uri=https%3A%2F%2Fwww.ariva.de%2F%3Fbase64_redirect%3DaHR0cHM6Ly93d3cuYXJpdmEuZGUv&response_type=code&scope=openid+profile+email&state=ebf48737-c647-4f9a-aed4-06307db5f022")
    time.sleep(0.5)
    # 1) Benutzername / E-Mail
    username_input = wait.until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username_input.clear()
    username_input.send_keys(username)
    time.sleep(0.5)
    # 2) Passwort
    password_input = wait.until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    password_input.clear()
    password_input.send_keys(password)
    time.sleep(1)
    # 3) Absenden (Button)
    submit_button = wait.until(
        EC.element_to_be_clickable((By.ID, "submit"))
    )
    submit_button.click()
    time.sleep(1)



def click_cookies(driver, timeout=15):
    time.sleep(5)
    wait = WebDriverWait(driver, timeout)

    selectors = [
        (By.CSS_SELECTOR, "button.sp_choice_type_11"),
        (By.CSS_SELECTOR, "button[aria-label='Akzeptieren und weiter']"),
        (By.XPATH, "//button[contains(@class,'sp_choice_type_11')]"),
        (By.XPATH, "//*[@aria-label='Akzeptieren und weiter']"),
    ]

    def try_click_in_current_context():
        for by, sel in selectors:
            els = driver.find_elements(by, sel)
            if els:
                el = els[0]
                driver.execute_script("arguments[0].click();", el)
                return True
        return False

    # 1) Erst im Hauptdokument versuchen
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    if try_click_in_current_context():
        return True

    # 2) Dann alle iframes durchgehen
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    for i, frame in enumerate(iframes):
        try:
            driver.switch_to.frame(frame)
            if try_click_in_current_context():
                driver.switch_to.default_content()
                return True
        except Exception:
            pass
        finally:
            driver.switch_to.default_content()

    return False

def new_driver(temp_path, proxy: str | None = None):
    download_dir = temp_path
    download_dir.mkdir(parents=True, exist_ok=True)

    chrome_options = Options()
    #chrome_options.add_argument("--headless=new")
    chrome_options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
    )
    if proxy:
        chrome_options.add_argument(f"--proxy-server={proxy}")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    return driver

def getdata():
    rd = Reader()
    rd.openExplorer()
    data = pd.read_csv(filepath_or_buffer=rd.path, sep  = ";", encoding="cp1252", dtype=str)
    return data


daten = getdata()
url_list = build_ariva_urls(daten)
url_df = pd.DataFrame(url_list)
#url_df.to_csv("/Users/justinwild/Downloads/urls.csv")


login_url = "https://login.ariva.de/realms/ariva/login-actions/authenticate?session_code=ZrrpH0xEYdRkBqsyLCtZoih8G7F6QMVlZvLglwbKge8&execution=e9102dd0-5958-429b-a14a-2ace928e2387&client_id=ariva-web&tab_id=7oQ6TS-HIHY&client_data=eyJydSI6Imh0dHBzOi8vd3d3LmFyaXZhLmRlLz9iYXNlNjRfcmVkaXJlY3Q9YUhSMGNITTZMeTkzZDNjdVlYSnBkbUV1WkdVdiIsInJ0IjoiY29kZSIsInN0IjoiZWJmNDg3MzctYzY0Ny00ZjlhLWFlZDQtMDYzMDdkYjVmMDIyIn0"
url = "https://www.ariva.de/"

i = 1
current_proxy = None
driver = None
for ariva_url in url_list:
    proxy = get_proxy_for_index(i)
    if proxy != current_proxy:
        if driver:
            driver.quit()
            time.sleep(2)
        driver = new_driver(temp_path, proxy)
        current_proxy=proxy
        wait = WebDriverWait(driver, 10)
        driver.get(url)
        # Nutzung:
        click_cookies(driver)
        login(driver)
    driver.get(ariva_url)
    time.sleep(0.018)
    i = i + 1
    if(i % 500 == 0):
        time.sleep(10)


## ab hier Dateien Verarbeitung

folder = temp_path

dfs = []
csv_files = list(folder.glob("*.csv"))
print(str(len(csv_files)) + " Dateien im Ordner")
time.sleep(3)
for file in csv_files:
    wkn = file.name.split("_")[1]
    df = pd.read_csv(
        file,
        sep = ";",
        encoding="utf-8"
    )
    df["WKN"] = wkn
    dfs.append(df)
    file.unlink()

df_all = pd.concat(dfs, ignore_index=True)
df_all.to_csv("//Master/F/User/Microsoft Excel/Privat/Börse/historische_Kurse" + "/historic_all_" + datetime.now().strftime("%Y-%m-%d%H%M") + ".csv", sep=";", encoding="utf-8", index=False)
#df_all.to_csv("/Users/justinwild/Downloads/historic_all" + datetime.now().strftime("%Y-%m-%d%H%M") + ".csv", sep=";", encoding="utf-8", index=False)
