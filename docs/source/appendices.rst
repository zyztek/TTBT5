Appendices
==========

Key Code and Scripts
--------------------

This section contains key code snippets and scripts used in the TTBT2 project.

Ethics Compliance Code
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # src/core/audit.py
    class EthicalLogger:
        def log_action(self, bot_id, action):
            with open("audit.log", "a") as f:
                f.write(f"{datetime.now()} | {bot_id} | {action}\n")

DAO Smart Contract
^^^^^^^^^^^^^^^^^^^

.. code-block:: solidity

    // contracts/TTBT2DAO.sol
    pragma solidity ^0.8.0;

    import "@openzeppelin/contracts/governance/Governor.sol";
    import "@openzeppelin/contracts/governance/extensions/GovernorSettings.sol";

    contract TTBT2DAO is Governor, GovernorSettings {
        constructor()
            Governor("TTBT2DAO")
            GovernorSettings(
                1 days,    // Tiempo de proposición
                7 days,    // Tiempo de votación
                5000       // Cuórum requerido
            ) {}

        function propose(
            address[] memory targets,
            uint256[] memory values,
            bytes[] memory calldatas,
            string memory description
        ) public override returns (uint256) {
            require(
                msg.sender.balanceOf(msg.sender) >= 100,
                "No tienes suficientes NFTs para proponer"
            );
            return super.propose(targets, values, calldatas, description);
        }
    }

Deployment Script
^^^^^^^^^^^^^^^^^^

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

Prometheus Queries
^^^^^^^^^^^^^^^^^^

.. code-block:: promql

    # Average proxy usage
    avg(ttbt2_proxy_usage)

    # Rate of NFT sales
    rate(ttbt2_nft_sales_total[1h])

    # Count of active plugins
    count(ttbt2_active_plugins)

Multi-Cloud DOT Diagram
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: dot

    digraph MultiCloud {
        node [shape=box, style=filled];
        subgraph AWS {
            label="AWS";
            color=darkgreen;
            s3 [label="S3 (Storage)", fillcolor="#90ee90"];
            ecs [label="ECS (Compute)", fillcolor="#90ee90"];
        }

        subgraph GCP {
            label="Google Cloud";
            color=darkblue;
            gcs [label="GCS", fillcolor="#add8e6"];
            gke [label="GKE", fillcolor="#add8e6"];
        }

        subgraph Azure {
            label="Azure";
            color=purple;
            blob [label="Blob Storage", fillcolor="#dda0dd"];
            aks [label="AKS", fillcolor="#dda0dd"];
        }

        // Conexiones
        ecs -> gke [label="Traffic Load Balancing", color=black];
        aks -> s3 [label="Backup", color=black];
    }
