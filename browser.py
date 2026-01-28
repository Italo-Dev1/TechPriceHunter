import logging
import psutil
from selenium import webdriver


def cria_driver(headless = False):
    try:
        options = webdriver.FirefoxOptions()
        if headless:
            options.add_argument("--headless")

        profile = webdriver.FirefoxProfile()
        profile.set_preference(
            "general.useragent.override",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
        )
        profile.update_preferences()

        options.profile = profile
        driver = webdriver.Firefox(options=options)
        driver.maximize_window()

        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )

        logging.info("Driver iniciado com sucesso")
        return driver

    except Exception as e:
        logging.error(f"Erro ao criar driver: {e}")
        return None


def fecha_navegador(driver):
    if not driver:
        return

    try:
        pid = driver.service.process.pid
        driver.quit()

        if psutil.pid_exists(pid):
            psutil.Process(pid).kill()

        logging.info("Driver encerrado com sucesso")

    except Exception as e:
        logging.error(f"Erro ao encerrar navegador: {e}")
