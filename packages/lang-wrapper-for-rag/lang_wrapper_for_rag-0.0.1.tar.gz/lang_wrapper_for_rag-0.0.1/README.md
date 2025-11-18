# python-mini-chatbot-rag
preparing for interview
pip install poetry
poetry init
Rendben, ez egy fontos pontosítás\! A Poetry egy sokkal strukturáltabb `pyproject.toml` fájlt használ.

Ebben az esetben a `pyproject.toml` fájlod a `[tool.poetry]` szekciót fogja használni a függőségek definiálására, nem az általános `[project]` szekciót.

Íme a `pyproject.toml` fájl, ahogyan az egy Poetry projekt esetében kinézne.

-----

## Módosított `pyproject.toml` (Poetry-hez)

-----

## 🚀 Futtatási útmutató (Poetry-vel)

1.  **Hozd létre a `pyproject.toml` fájlt:** Mentsd el a fenti TOML tartalmat.

2.  **Mentsd el a kódot:** Mentsd a Python kódot `app.py` néven.

3.  **Függőségek telepítése (Poetry):**

    ```bash
    # Ez létrehozza a venv-et (ha kell) és telepíti az összes függőséget
    poetry install
    ```

    *Megjegyzés: Ha a `[tool.poetry.group.dev.dependencies]`-t is hozzáadtad, a `poetry install` alapból telepíti azt is. Ha nem, akkor a `poetry install --with dev` parancs teszi ezt meg.*

4.  **Töltsd le a Spacy modellt (Kritikus lépés\!):**
    Ezt a Poetry-n *kívül* vagy a Poetry környezetén *belül* is megteheted. A legegyszerűbb:

    ```bash
    poetry run python -m spacy download en_core_web_lg
    ```

5.  **Készítsd elő a dokumentumokat:**
    Helyezd a `hr_policies.pdf` fájlodat egy `docs` mappába (`docs/hr_policies.pdf`).

6.  **Indítsd el a szervert:**

    ```bash
    poetry run uvicorn app:app --reload
    ```

docker build -t rag-chatbot .

docker run -d -p 8000:8000 --name chatbot rag-chatbot

# Egyszeri beállítás: add hozzá a TestPyPI-t a Poetry-hez
poetry config repositories.testpypi https://test.pypi.org/legacy/

# Publikálás (kérni fogja a TestPyPI tokenedet)
poetry publish --repository testpypi
