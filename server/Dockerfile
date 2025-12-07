FROM python:3.9-slim
WORKDIR /app
RUN pip install openai
COPY server.py .
EXPOSE 5555
CMD ["python", "-u", "server.py"]