#!/bin/bash

# Sprawdzenie, czy Python jest zainstalowany
if ! command -v python3 &> /dev/null
then
    echo "Python3 nie został znaleziony."
    exit
fi

# Tworzenie wirtualnego środowiska
python3 -m venv .venv

# Aktywacja wirtualnego środowiska
source .venv/bin/activate

# Instalacja wymaganych pakietów
pip install -r requirements.txt

# Powiadomienie o zakończeniu
echo "Wirtualne środowisko zostało utworzone i pakiety zostały zainstalowane."
