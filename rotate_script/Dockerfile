FROM python:3
 
WORKDIR .
 
COPY rotate_script.py .

RUN   pip3 install flask && pip3 install pillow

CMD ["python3", "rotate_script.py"]