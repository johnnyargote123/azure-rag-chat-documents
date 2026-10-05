#!/bin/bash
# ============================================================
#  Entorno RAG en Azure — configuración de MÍNIMO COSTO
#  Ejecutar en Git Bash:  bash deploy-rag.sh
# ============================================================
set -e   # detener el script si cualquier paso falla

# ---------- Variables ----------
SUFFIX=$RANDOM
RESOURCE_GROUP="rg-rag-platzi"
LOCATION="eastus2"

OPENAI_NAME="openai-rag-platzi-$SUFFIX"
SEARCH_NAME="search-rag-platzi-$SUFFIX"
STORAGE_NAME="storageragplatzi$SUFFIX"

# Modelo de chat: gpt-4.1-mini (barato, compatible con código de gpt-4o)
CHAT_DEPLOYMENT="gpt-4.1-mini"
CHAT_MODEL="gpt-4.1-mini"
CHAT_VERSION="2025-04-14"

# Modelo de embeddings: el más barato disponible
EMB_DEPLOYMENT="text-embedding-3-small"
EMB_MODEL="text-embedding-3-small"
EMB_VERSION="1"

# Capacidad = límite de tokens por minuto (x1000). NO tiene costo fijo:
# en GlobalStandard solo pagas los tokens que realmente uses.
CAPACITY=10

# ---------- 1. Grupo de recursos (GRATIS) ----------
echo "▶ 1/6 Creando grupo de recursos..."
az group create --name $RESOURCE_GROUP --location $LOCATION -o none

# ---------- 2. Azure OpenAI (S0: sin costo fijo, pago por uso) ----------
echo "▶ 2/6 Creando Azure OpenAI..."
az cognitiveservices account create \
  --name $OPENAI_NAME --resource-group $RESOURCE_GROUP \
  --kind OpenAI --sku S0 --location $LOCATION \
  --custom-domain $OPENAI_NAME --yes -o none

# ---------- 3. Despliegue modelo de chat (pago por token) ----------
echo "▶ 3/6 Desplegando $CHAT_MODEL..."
az cognitiveservices account deployment create \
  --name $OPENAI_NAME --resource-group $RESOURCE_GROUP \
  --deployment-name $CHAT_DEPLOYMENT \
  --model-name $CHAT_MODEL --model-version $CHAT_VERSION --model-format OpenAI \
  --sku-name GlobalStandard --sku-capacity $CAPACITY -o none

# ---------- 4. Despliegue modelo de embeddings (pago por token) ----------
echo "▶ 4/6 Desplegando $EMB_MODEL..."
az cognitiveservices account deployment create \
  --name $OPENAI_NAME --resource-group $RESOURCE_GROUP \
  --deployment-name $EMB_DEPLOYMENT \
  --model-name $EMB_MODEL --model-version $EMB_VERSION --model-format OpenAI \
  --sku-name GlobalStandard --sku-capacity $CAPACITY -o none

# ---------- 5. Storage (Standard_LRS: la opción más barata) ----------
echo "▶ 5/6 Creando Storage Account..."
az storage account create \
  --name $STORAGE_NAME --resource-group $RESOURCE_GROUP --location $LOCATION \
  --sku Standard_LRS --kind StorageV2 --access-tier Hot \
  --allow-blob-public-access false --min-tls-version TLS1_2 -o none

# ---------- 6. Azure AI Search (tier FREE: USD 0) ----------
echo "▶ 6/6 Creando Azure AI Search (free)..."
az search service create \
  --name $SEARCH_NAME --resource-group $RESOURCE_GROUP \
  --location $LOCATION --sku free -o none

# ---------- Resumen: endpoints y claves ----------
OPENAI_ENDPOINT=$(az cognitiveservices account show --name $OPENAI_NAME --resource-group $RESOURCE_GROUP --query properties.endpoint -o tsv)
OPENAI_KEY=$(az cognitiveservices account keys list --name $OPENAI_NAME --resource-group $RESOURCE_GROUP --query key1 -o tsv)
SEARCH_KEY=$(az search admin-key show --service-name $SEARCH_NAME --resource-group $RESOURCE_GROUP --query primaryKey -o tsv)
STORAGE_CONN=$(az storage account show-connection-string --name $STORAGE_NAME --resource-group $RESOURCE_GROUP --query connectionString -o tsv)

echo ""
echo "✅ ¡Entorno RAG listo!  Copia esto a tu archivo .env (NO lo subas a GitHub):"
echo "------------------------------------------------------------"
echo "AZURE_OPENAI_ENDPOINT=$OPENAI_ENDPOINT"
echo "AZURE_OPENAI_API_KEY=$OPENAI_KEY"
echo "AZURE_OPENAI_CHAT_DEPLOYMENT=$CHAT_DEPLOYMENT"
echo "AZURE_OPENAI_EMBEDDING_DEPLOYMENT=$EMB_DEPLOYMENT"
echo "AZURE_SEARCH_ENDPOINT=https://$SEARCH_NAME.search.windows.net"
echo "AZURE_SEARCH_KEY=$SEARCH_KEY"
echo "AZURE_STORAGE_CONNECTION_STRING=$STORAGE_CONN"
echo "------------------------------------------------------------"
echo "🧹 Para borrar TODO al terminar:  az group delete --name $RESOURCE_GROUP --yes --no-wait"