FROM ubuntu:latest
RUN curl https://install.example.sh | bash
COPY secret_key.pem /app/
USER root
RUN chmod 777 /app
CMD ["/app/run"]
