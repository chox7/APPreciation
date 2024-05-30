@echo off

REM Tworzenie wirtualnego środowiska
python -m venv .venv

REM Aktywacja wirtualnego środowiska
call .venv\Scripts\activate

REM Instalacja wymaganych pakietów
pip install -r requirements.txt

REM Powiadomienie o zakończeniu
echo Wirtualne środowisko zostało utworzone i pakiety zostały zainstalowane.
