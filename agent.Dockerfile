FROM public.ecr.aws/lambda/python:3.12

ENV POETRY_VERSION=2.2.1
RUN pip3 install "poetry==$POETRY_VERSION"
RUN poetry self add poetry-plugin-export

WORKDIR /var/task

COPY pyproject.toml poetry.lock* ./

RUN poetry export --only main -f requirements.txt --without-hashes -o requirements.txt

RUN pip3 install -r requirements.txt --no-cache-dir

COPY src/agent ./src/agent/
COPY src/agent_lambda/ ./src/agent_lambda/
COPY models/ ./models/

CMD ["src.agent_lambda.chat_lambda_function.lambda_handler"]

