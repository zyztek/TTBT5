Sistema de Documentación
=========================

Documentación Técnica y de Usuario
----------------------------------

TTBT2 mantiene una documentación completa que incluye guías técnicas y de usuario en múltiples idiomas.

Estructura de Documentación
---------------------------

.. code-block:: bash

   docs/
   ├── technical/  # Arquitectura, APIs y seguridad
   │   ├── architecture_azure.md    # Diagrama Mermaid con Azure
   │   └── security_final.pdf        # OWASP y auditorías de voz
   ├── developer/   # Guías para plugins y IA
   │   ├── azure.md  # Configuración de Terraform
   │   └── voice_ai.md # Pruebas y optimización
   ├── user/        # Manuales multilingües
   │   ├── azure_tutorial.md         # Guía de despliegue en Azure
   │   └── voice_chat_tutorial.md    # Uso del chatbot de voz
   └── reports/     # Métricas finales
       ├── final_2029.pdf            # Resumen ejecutivo
       └── grafana_full_export.zip   # Dashboard completo

Automatización de la Documentación
----------------------------------

La documentación se genera automáticamente con GitHub Actions:

.. code-block:: yaml

   # .github/workflows/docs.yml
   name: Generate Docs
   on: [push]
   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Install Dependencies
           run: pip install sphinx matplotlib && npm install
         - name: Build Documentation
           run: sphinx-build -b html ./docs/source ./docs/build && npm run docs:generate
         - name: Deploy to GitHub Pages
           uses: peaceiris/actions-gh-pages@v3
           with:
             github_token: ${{ secrets.GITHUB_TOKEN }}
             publish_dir: ./docs/build

User Onboarding Kit
--------------------

Para facilitar la adopción del sistema, se proporciona un kit de inicio rápido:

.. code-block:: markdown

   # QUICKSTART.md
   1. **Install Dependencies**:
      ```bash
      pip install -r requirements.txt
      npm install
      ```
   2. **Run Locally**:
      ```bash
      docker compose up
      ```
   3. **Access Features**:
      - Marketplace: `http://localhost:3000/marketplace`
      - Voice Chat: `http://localhost:3000/voice-test`

Ethics & Compliance Manual
--------------------------

Para garantizar el uso responsable del sistema, se mantiene un manual de ética y cumplimiento:

.. code-block:: markdown

   # ETHICS.md
   1. **Legal Compliance**: GDPR/CCPA guidelines for user data.
   2. **Ethical Usage**: Prohibitions on spamming, impersonation, or violating platform TOS.
   3. **Audit Trail**: Mandatory logging of bot actions for accountability.

.. code-block:: python

   # src/core/audit.py
   import logging

   class EthicalLogger:
       def __init__(self):
           self.logger = logging.getLogger("TTBT2_AUDIT")

       def log_action(self, bot_id, action, timestamp):
           self.logger.info(f"{bot_id}|{action}|{timestamp}")
