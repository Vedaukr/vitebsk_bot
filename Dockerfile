FROM python:3.11
# Or any preferred Python version.
ADD *.py .
COPY utils utils/
COPY database database/
#ADD app.db .
RUN pip install telebot sqlalchemy imagehash flask
EXPOSE 8080
CMD ["python", "./bot.py"] 
# Or enter the name of your unique directory and parameter set.