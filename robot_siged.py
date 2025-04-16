
import os
import pandas as pd
from github import Github
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = "jmca21/painel-processos-prioritarios"
FILE_PATH = "processos_prioritarios.csv"

SIGED_LOGIN = os.getenv("SIGED_LOGIN")
SIGED_SENHA = os.getenv("SIGED_SENHA")

def baixar_arquivo_csv(g):
    repo = g.get_repo(REPO_NAME)
    file = repo.get_contents(FILE_PATH)
    with open("processos_prioritarios.csv", "w", encoding="utf-8") as f:
        f.write(file.decoded_content.decode())

def subir_csv_atualizado(g):
    repo = g.get_repo(REPO_NAME)
    file = repo.get_contents(FILE_PATH)
    with open("processos_prioritarios.csv", "r", encoding="utf-8") as f:
        content = f.read()
    repo.update_file(FILE_PATH, "Atualização automática SIGED", content, file.sha)

def atualizar_dados_siged():
    df = pd.read_csv("processos_prioritarios.csv")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = EdgeService(executable_path="msedgedriver.exe")
    driver = webdriver.Edge(service=service, options=options)
    wait = WebDriverWait(driver, 15)

    try:
        driver.get("https://protocolo.manaus.am.gov.br")
        wait.until(EC.presence_of_element_located((By.NAME, "login"))).send_keys(SIGED_LOGIN)
        wait.until(EC.presence_of_element_located((By.NAME, "senha"))).send_keys(SIGED_SENHA)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Entrar')]"))).click()

        for i, row in df.iterrows():
            driver.get("https://protocolo.manaus.am.gov.br")
            partes = row["numero_processo"].split(".")
            if len(partes) < 5:
                continue
            campos = ["ano", "orgao", "sequencial", "digito", "ano_processo"]
            for part, campo in zip(partes, campos):
                try:
                    wait.until(EC.presence_of_element_located((By.NAME, campo))).clear()
                    wait.until(EC.presence_of_element_located((By.NAME, campo))).send_keys(part)
                except:
                    continue
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Pesquisar')]"))).click()
            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'ver_processo')]"))).click()

            time.sleep(2)
            try:
                df.at[i, "situacao"] = driver.find_element(By.CLASS_NAME, "badge").text.strip()
                df.at[i, "depto_atual"] = driver.find_element(By.XPATH, "//td[contains(text(), 'Departamento')]/following-sibling::td").text.strip()
            except:
                pass

            try:
                historico_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Histórico de Movimentação')]")))
                driver.execute_script("arguments[0].click();", historico_btn)
                time.sleep(2)
                linhas = driver.find_elements(By.XPATH, "//table[contains(@class, 'table')]/tbody/tr")
                if linhas:
                    ultima_linha = linhas[0].text.split("\n")
                    df.at[i, "data_ultimo_andamento"] = ultima_linha[0]
                    df.at[i, "ultimo_andamento"] = " ".join(ultima_linha[1:])
            except:
                pass

        df.to_csv("processos_prioritarios.csv", index=False)
    finally:
        driver.quit()

if __name__ == "__main__":
    g = Github(GITHUB_TOKEN)
    baixar_arquivo_csv(g)
    atualizar_dados_siged()
    subir_csv_atualizado(g)
