Despliegue y Monitoreo
======================

Automated Deployment Pipeline
-----------------------------

TTBT2 utiliza un pipeline de despliegue automatizado para garantizar despliegues sin tiempo de inactividad en múltiples proveedores de nube.

.. code-block:: bash

   # deploy_prod_final.sh
   #!/bin/bash
   set -e

   echo "Deploying Terraform..."
   terraform apply -auto-approve

   echo "Deploying Kubernetes..."
   kubectl apply -f k8s/prod/

   echo "Updating Helm Charts..."
   helm upgrade ttbt2 ./charts/ttbt2 --install

   echo "Deploying marketplace NFTs..."
   python scripts/mint_initial_nfts.py

   echo "Final checks..."
   kubectl rollout status deployment/ttbt2

Multi-Cloud Load Testing
------------------------

Para garantizar la estabilidad en entornos multizonales, se realizan pruebas de carga globales.

.. code-block:: python

   # locustfile_global.py
   from locust import HttpUser, task

   class GlobalUser(HttpUser):
       @task
       def test_voice_chat(self):
           self.client.post("/api/voice/chat", files={"audio": "test_audio.mp3"})

       @task
       def test_azure_proxy(self):
           self.client.get("https://azure.ttbt2.com/proxy")

Security Automation
-------------------

Se implementan escaneos de seguridad automatizados diariamente.

.. code-block:: yaml

   # .github/workflows/security_daily.yml
   name: Daily Security Scan
   on:
     schedule:
       - cron: "0 5 * * *"

   jobs:
     scan:
       runs-on: ubuntu-latest
       steps:
         - name: OWASP ZAP Scan
           run: zap-cli scan --url https://app.ttbt2.com --report
         - name: Bandit Scan
           run: bandit -r src/ -ll -x external_deps
         - name: Upload Reports
           uses: actions/upload-artifact@v3
           with:
             name: security-reports
             path: ./reports/security/

Monitoring Plan
---------------

Daily/Weekly Processes
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # cron_jobs.sh
   0 0 * * * /backup.sh          # Daily backup
   30 5 * * 1 /security_scan.sh  # Weekly security audit

Grafana Alert Rules
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # alerts.yml
   - name: High Voice Latency
     condition: avg(ttbt2_voice_response_time_seconds{env="prod"}) > 1.5
     message: "Voice response time exceeded 1.5s!"

   - name: Low NFT Sales
     condition: sum(ttbt2_audio_nft_sales_total) < 10 over 1h
     message: "Sales dropped below threshold!"

Final Code & Infrastructure Cleanup
-----------------------------------

Remove Beta/Debug Code
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Remove debug print statements
   # print(f"Bot {id} executed action {action}")

Optimize Docker Images
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: docker

   # Dockerfile.slim
   FROM python:3.9-slim
   COPY requirements.txt .
   RUN pip install -r requirements.txt --no-cache-dir
   COPY src/ .
   CMD ["python", "main.py"]
