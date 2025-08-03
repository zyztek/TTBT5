Apéndices
=========

Código Clave
------------

Contrato DAO
~~~~~~~~~~~~

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

Contrato de NFTs de Audio
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: solidity

   // contracts/AudioNFT.sol
   pragma solidity ^0.8.0;

   import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

   contract TTBT2AudioNFT is ERC721 {
       struct AudioNFT {
           string audioHash;
           address owner;
           uint256 likes;
       }

       mapping(uint256 => AudioNFT) public audioNFTs;

       constructor() ERC721("TTBT2AudioNFT", "T2AUDIO") {}

       function mintAudioNFT(string memory _audioHash) external returns (uint256) {
           uint256 tokenId = audioNFTs.length;
           _safeMint(msg.sender, tokenId);
           audioNFTs[tokenId] = AudioNFT({
               audioHash: _audioHash,
               owner: msg.sender,
               likes: 0
           });
           return tokenId;
       }
   }

Script de Despliegue Final
~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Queries de Prometheus
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: promql

   # Métricas clave de TTBT2
   avg(ttbt2_proxy_usage)
   rate(ttbt2_nft_sales_total[1h])
   count(ttbt2_active_plugins)
   avg by (cloud_provider) (ttbt2_voice_response_time_seconds)
   count(ttbt2_dao_proposals{status="active"})
