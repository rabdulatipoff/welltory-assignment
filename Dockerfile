FROM python:3.12-slim

ENV APP_PORT=${APP_PORT:-80}
ENV APP_HOME=${APP_HOME:-/home/app}
ENV APP_GROUP_ID=${APP_GROUP_ID:-1001}
ENV APP_USER_ID=${APP_USER_ID:-1001}

# Create an application user
RUN set -ex && addgroup --system --gid ${APP_GROUP_ID} app_group \
            && adduser --system --uid ${APP_USER_ID} --gid ${APP_GROUP_ID} --no-create-home app_user

# Install dependencies
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR $APP_HOME
COPY . $APP_HOME
RUN chown -R app_user:app_group $APP_HOME

USER app_user

CMD ["sh", "-c", "fastapi run main.py --port $APP_PORT"]
