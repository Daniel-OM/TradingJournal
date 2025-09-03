#!/bin/bash

# CONFIGURACIÓN
GITHUB_USER="Daniel-OM"
REPO_NAME="TradingJournal"
REPO_URL="https://github.com/${GITHUB_USER}/${REPO_NAME}.git"
APP_DIR="/home/daniel/TradingJournal"
BRANCH="main"
SERVICE_NAME="trading-journal"
LAST_VERSION_FILE="$APP_DIR/.version"
VENV_DIR="$APP_DIR/venv"

echo "🔍 Obteniendo último tag usando git..."

# Obtener el último tag usando git ls-remote (no usa API)
LATEST_TAG=$(git tag -l --sort=-v:refname | head -1)

if [ -z "$LATEST_TAG" ]; then
    echo "❌ No se pudo obtener el último tag del repositorio"
    echo "🔍 Intentando obtener todos los tags disponibles:"
    git ls-remote --tags "$REPO_URL" | head -5
    exit 1
fi

echo "📋 Último tag: $LATEST_TAG"

# Leer última versión descargada
if [ -f "$LAST_VERSION_FILE" ]; then
    CURRENT_VERSION=$(cat "$LAST_VERSION_FILE")
else
    CURRENT_VERSION="none"
fi

echo "📋 Versión actual: $CURRENT_VERSION"

# Comparar versiones
if [ "$LATEST_TAG" != "$CURRENT_VERSION" ]; then
    echo "🆕 Nueva versión disponible: $LATEST_TAG"
    
    # Crear backup
    BACKUP_DIR="$APP_DIR-backup-$(date +%F-%T)"
    echo "💾 Creando backup en $BACKUP_DIR"
    cp -r "$APP_DIR" "$BACKUP_DIR"

    # Navegar al directorio de la app
    cd "$APP_DIR" || exit 1

    # Inicializar repo si no existe
    if [ ! -d "$APP_DIR/.git" ]; then
        echo "📥 Clonando repositorio..."
        git clone "$REPO_URL" temp_clone
        mv temp_clone/* "$APP_DIR/"
        mv temp_clone/.git* "$APP_DIR/" 2>/dev/null
        rm -rf temp_clone
    fi
    
    # Actualizar repo
    echo "🔄 Actualizando repositorio..."
    git fetch --all --tags
    
    # Limpiar cambios locales si los hay
    git reset --hard HEAD
    git clean -fd
    
    # Cambiar a la nueva tag
    echo "🏷️  Cambiando a tag $LATEST_TAG"
    git checkout tags/"$LATEST_TAG" -B "release-$LATEST_TAG"

    # Crear entorno virtual si no existe
    if [ ! -d "$VENV_DIR" ]; then
        echo "🛠️  Creando entorno virtual..."
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activar entorno virtual e instalar/actualizar dependencias
    echo "📦 Instalando dependencias..."
    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "⚠️  No se encontró requirements.txt"
    fi
    deactivate

    # Guardar nueva versión
    echo "$LATEST_TAG" > "$LAST_VERSION_FILE"

    # Reiniciar servicio
    echo "🚀 Reiniciando servicio $SERVICE_NAME..."
    sudo systemctl restart "$SERVICE_NAME"
    
    # Verificar estado del servicio
    sleep 2
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        echo "✅ Servicio reiniciado correctamente"
        echo "🎉 Aplicación actualizada a $LATEST_TAG"
    else
        echo "❌ Error al reiniciar el servicio. Restaurando backup..."
        sudo systemctl stop "$SERVICE_NAME"
        rm -rf "$APP_DIR"
        mv "$BACKUP_DIR" "$APP_DIR"
        sudo systemctl start "$SERVICE_NAME"
        echo "🔄 Backup restaurado"
        exit 1
    fi
    
    # Limpiar backups antiguos (mantener solo los 3 más recientes)
    echo "🧹 Limpiando backups antiguos..."
    ls -dt "$APP_DIR"-backup-* 2>/dev/null | tail -n +4 | xargs rm -rf 2>/dev/null
    
else
    echo "✅ La aplicación ya está en la última versión ($CURRENT_VERSION)"
fi