FROM python:3.11-slim

WORKDIR /app
COPY app.py .

EXPOSE 9101
ENV EXPORTER_PORT=9101

HEALTHCHECK --interval=15s --timeout=3s \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:9101/healthz').read()==b'ok\n' else 1)"

CMD ["python", "app.py"]
