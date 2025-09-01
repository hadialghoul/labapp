@echo off
REM Batch script to run treatment step notifications
REM This script should be scheduled to run daily using Windows Task Scheduler

REM Change to the project directory
cd /d "E:\auth\medical_project"

REM Activate virtual environment
call "E:\auth\env\Scripts\activate.bat"

REM Run the management command with auto-progression
python manage.py notify_finished_steps --auto-progress

REM Log the execution with timestamp
echo [%date% %time%] Treatment step notifications processed >> notification_log.txt

REM Deactivate virtual environment
deactivate
