#!/bin/bash

# CONFIGURACIÓN
REPO="https://github.com/Daniel-OM/TradingJournal.git"           # tu repositorio GitHub
APP_DIR="/var/www/TradingJournal"             # dónde está la app en el servidor
BRANCH="main"
SERVICE_NAME="trading-journal"            # nombre del servicio systemd
LAST_VERSION_FILE="$APP_DIR/.version"
VENV_DIR="$APP_DIR/venv"

# Obtener última release de GitHub
LATEST_TAG=$(curl -s https://api.github.com/repos/$REPO/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

if [ -z "$LATEST_TAG" ]; then
    echo "No se pudo obtener el último release."
    exit 1
fi

echo "Último release: $LATEST_TAG"

# Leer última versión descargada
if [ -f "$LAST_VERSION_FILE" ]; then
    CURRENT_VERSION=$(cat "$LAST_VERSION_FILE")
else
    CURRENT_VERSION="none"
fi

# Comparar
if [ "$LATEST_TAG" != "$CURRENT_VERSION" ]; then
    echo "Nueva versión disponible: $LATEST_TAG (actual: $CURRENT_VERSION)"
    
    # Hacer backup por si acaso
    cp -r "$APP_DIR" "$APP_DIR-backup-$(date +%F-%T)"

    # Clonar o actualizar el repo
    if [ ! -d "$APP_DIR/.git" ]; then
        git clone https://github.com/$REPO.git "$APP_DIR"
    fi
    
    cd "$APP_DIR" || exit 1
    git fetch --all
    git checkout $BRANCH
    git pull origin $BRANCH
    git checkout tags/$LATEST_TAG -b temp-release

    # Crear entorno virtual si no existe
    if [ ! -d "$VENV_DIR" ]; then
        echo "🛠️  Creando entorno virtual en $VENV_DIR"
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activar entorno virtual e instalar dependencias
    source "$VENV_DIR/bin/activate"
    if [ -f "requirements.txt" ]; then
        echo "📦 Instalando dependencias..."
        pip install --upgrade pip
        pip install -r requirements.txt
    fi
    deactivate

    # Guardar versión actual
    echo "$LATEST_TAG" > "$LAST_VERSION_FILE"

    # Reiniciar servicio
    echo "🚀 Reiniciando servicio $SERVICE_NAME..."
    systemctl restart "$SERVICE_NAME"
    echo "Aplicación actualizada a $LATEST_TAG y reiniciada."
else
    echo "La aplicación ya está en la última versión ($CURRENT_VERSION)."
fi
