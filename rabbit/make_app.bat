set WORK_ROOT=E:\SourceCode\shopping_bot\rabbit
pyinstaller.exe --noconfirm --onefile --console --add-data %WORK_ROOT%\resource;resource\ --add-data %WORK_ROOT%\model;model\ --add-data %WORK_ROOT%\notification;notification\ --add-data %WORK_ROOT%\sites;sites\ --add-data %WORK_ROOT%\theming;theming\ --add-data %WORK_ROOT%\utils;utils\ --add-data %WORK_ROOT%\view;view\ %WORK_ROOT%\main.py
