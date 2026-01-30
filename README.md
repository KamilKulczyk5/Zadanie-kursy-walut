```md
# Zadanie – Kursy walut (NBP)

## Opis projektu
Projekt polega na stworzeniu aplikacji internetowej umożliwiającej pobieranie,
zapisywanie oraz wyświetlanie kursów walut z API Narodowego Banku Polskiego (NBP).

Aplikacja została uruchomiona w architekturze kontenerowej z wykorzystaniem Dockera
oraz docker-compose.

---

## Funkcjonalności
- pobieranie kursów walut (Tabela A NBP),
- zapis danych do bazy PostgreSQL,
- odczyt kursów walut dla pojedynczej daty,
- odczyt kursów walut w zakresie dat,
- grupowanie danych: dni / miesiące / kwartały / lata,
- testy automatyczne (pytest + BDD).

---

## Architektura aplikacji

Frontend (Angular + nginx)  
→ Backend (FastAPI)  
→ PostgreSQL  
→ NBP API  

---

## Technologie
- **Frontend:** Angular (standalone), HTML, CSS
- **Backend:** FastAPI, SQLAlchemy
- **Baza danych:** PostgreSQL
- **Testy:** pytest, pytest-bdd
- **Konteneryzacja:** Docker, docker-compose
- **Reverse proxy:** nginx

---

## Uruchomienie aplikacji

### Wymagania
- Docker
- Docker Compose

### Uruchomienie
W katalogu głównym projektu uruchomić:

```bash
docker compose up --build