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

cd "$APP_DIR" || { echo "No existe $APP_DIR"; exit 1; }

# Traer todo (ramas y tags)
git fetch --all --tags --prune

LATEST_TAG=$(git ls-remote --tags "$REPO_URL" \
    | awk '{print $2}' \
    | sed 's#refs/tags/##' \
    | grep -v '{}' \
    | sort -V \
    | tail -n1)

# Si git fetch falla por 'would clobber existing tag', fuerza la actualización del tag específico:
if ! git fetch origin --tags; then
    echo "⚠️ Conflicto de tags: forzando actualización del tag remoto..."
    # borrar el tag local conflictivo y volver a traer solo ese tag
    git tag -d "$LATEST_TAG" 2>/dev/null || true
    git fetch origin "refs/tags/$LATEST_TAG:refs/tags/$LATEST_TAG"
fi

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

    # Inicializar repo si no existe
    if [ ! -d "$APP_DIR/.git" ]; then
        echo "📥 Clonando repositorio..."
        git clone "$REPO_URL" temp_clone
        mv temp_clone/* "$APP_DIR/"
        mv temp_clone/.git* "$APP_DIR/" 2>/dev/null
        rm -rf temp_clone
    fi
    
    # Navegar al directorio de la app
    cd "$APP_DIR" || exit 1
    
    # Actualizar repo
    echo "🔄 Actualizando repositorio..."
    git fetch --all --tags --prune || true

    # Si el tag local existe y apunta a otro commit, eliminarlo para traer el del remoto
    if git rev-parse "refs/tags/$LATEST_TAG" >/dev/null 2>&1; then
        # comparar sha local vs remoto
        local_sha=$(git rev-parse "refs/tags/$LATEST_TAG")
        remote_sha=$(git ls-remote --tags "$REPO_URL" "refs/tags/$LATEST_TAG" | awk '{print $1}')
        if [ -n "$remote_sha" ] && [ "$local_sha" != "$remote_sha" ]; then
            echo "⚠️ Tag local $LATEST_TAG difiere del remoto; actualizando tag..."
            git tag -d "$LATEST_TAG" || true
            git fetch origin "refs/tags/$LATEST_TAG:refs/tags/$LATEST_TAG"
        fi
    else
        git fetch origin "refs/tags/$LATEST_TAG:refs/tags/$LATEST_TAG" || true
    fi
    
    # Limpiar cambios locales si los hay
    git reset --hard HEAD
    git clean -fd
    
    # Cambiar a la nueva tag
    echo "🏷️  Cambiando a tag $LATEST_TAG"
    # git checkout tags/"$LATEST_TAG" -B "release-$LATEST_TAG"
    git checkout -B "release-$LATEST_TAG" "tags/$LATEST_TAG"

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

    # Migrando cambios a la base de datos si es necesario
    echo "🗄️  Aplicando migraciones de base de datos..."
    FLASK_APP=flask.wsgi:app flask db upgrade

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
    ls -dt "$APP_DIR"-backup-* 2>/dev/null | xargs rm -rf 2>/dev/null
    
else
    echo "✅ La aplicación ya está en la última versión ($CURRENT_VERSION)"
fi