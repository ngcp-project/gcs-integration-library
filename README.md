# GCS Vehicle Integration Library
Make sure to do `pip install pika` to be able to run this library

If you are on Powershell, set up the python environment by: 

1. Check Dependencies:

    1a. make sure you have RabbitMQ installed: [Install RabbitMQ](https://www.rabbitmq.com/download.html)
    
* Go to your home directory using `cd` 
* Open a powershell terminal within VSCode and use the command `python -m venv .venv` to create a virtual environment. 
* To activate, run this command `.\venv\Scripts\Activate.ps1`
* If that command give you errors, run this command instead:
`.\venv\Scripts\activate.bat`
* Set up your python path: `$env:PYTHONPATH = "$PWD"` (trouble-shooting)
* To check if your PYTHONPATH has been set up correctly, run this command: `echo $PYTHONPATH` and it should prints your current home directory path. 
* Run Docker container using this command: `docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.12-management`

To set up docker: Dowload Docker Laptop: [Get Started with Docker](https://www.docker.com/get-started/)

Create python library 
python setup.py