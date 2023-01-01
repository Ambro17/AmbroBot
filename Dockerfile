FROM python:3.9-slim

# "Activate" venv by make it the first python in PATH
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install requirments in virtualenv
RUN pip install --upgrade pip wheel
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


WORKDIR /code
COPY . .

CMD ["python", "main.py"]
