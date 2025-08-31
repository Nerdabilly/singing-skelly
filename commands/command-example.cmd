@echo off

REM Pause the LOR player until Skelly reports that the file is playing - you may have to change the IP or port here depending on how your player is configured
curl -X PUT http://127.0.0.1:8001/v1/player/pause/immediately

REM wait 1 second before sending the play command to Skelly.
REM This is important because if the response happens too quickly, the LOR REST API will 
REM send a 400 Bad Request response and the show will stay paused but Skelly will keep singing

TIMEOUT /T 1

REM Call the Python script to tell Skelly to start singing.
REM action 1 : Play 
REM action 0 : Pause

REM serial : The serial index of the file you want to play in Skelly's file. 
REM You can get this list of indexes by using the app at https://tinkertims.github.io/skelly/ 


REM Obviously, change this to the correct path to the Python files

python "C:\Users\path\to\this\project\ble_send.py" playpause --serial 15 --action 1
