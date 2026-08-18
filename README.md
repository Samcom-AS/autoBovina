# autoBovina

Acest repository conține numai aplicația reconstruită și artefactele ei de rulare.
Nu include executabilul de referință, registrul Excel real, bytecode extras,
decompilatoare sau rapoarte de analiză.

## Rulare

1. Editează `dist\autoBovina\data\settings.txt` cu cele patru valori locale:
   registrul Excel, `putty.exe`, foaia de recepții și foaia de automatizare.
2. Rulează `dist\autoBovina\autoBovina.exe`.

Registrul Excel și Putty nu sunt incluse. Configurația livrată conține căi
exemplu și refuză sigur rularea până când sunt înlocuite.

## Conținut

- `apps\auto-bovina`: codul sursă, `main.py`, cerințele fixate, scriptul de
  build și scriptul Inno Setup;
- `dist\autoBovina`: distribuția PyInstaller;
- `release\autoBovina-setup-0.3.0.exe`: installerul Inno Setup.

Mediul Python `.venv` este local și nu este urmărit în Git. Testele sunt în
`tests\` și se pot rula cu CPython 3.12.

Pentru rebuild:

```powershell
cd apps\auto-bovina
.\build.ps1 -SkipDependencyInstall
```

Fluxul VIF rămâne mock-first: aplicația nu execută automat Putty sau VIF în
această versiune.
