# Guía — Subir el pipeline a GitHub (Fase 3, LRPD III)

El pipeline (`.github/workflows/ci.yml`) se ejecuta **solo** cada vez que subes
cambios a GitHub. Corre: análisis estático (Ruff + Bandit) + todas las pruebas
(unitarias + E2E) + cobertura. El "check verde" ✅ que sale es tu evidencia del
criterio de CI/CD.

## Paso 1 — Verificar localmente (opcional pero recomendado)

Desde `makro_trazabilidad`, para asegurarte de que saldrá verde:

```bash
pip install ruff bandit
ruff check backend main.py seed.py tests_e2e
bandit -r backend --severity-level medium
```
Ambos deben terminar sin errores.

## Paso 2 — Subir a GitHub

### Opción A — Con VS Code (la más fácil)

1. Abre la carpeta `makro_trazabilidad` en VS Code.
2. Ve al panel **Source Control** (el ícono de ramas, a la izquierda) o `Ctrl+Shift+G`.
3. Clic en **Initialize Repository**.
4. Escribe un mensaje (ej. "Pipeline CI/CD y pruebas automatizadas") y clic en **Commit**.
5. Clic en **Publish Branch** → elige **Public repository** → nómbralo, por ejemplo, `mermazero-makro`.

Listo, ya está en tu GitHub.

### Opción B — Con la terminal (git)

```bash
git init
git add .
git commit -m "Pipeline CI/CD y pruebas automatizadas"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/mermazero-makro.git
git push -u origin main
```
(Primero crea el repositorio vacío en github.com → New repository.)

## Paso 3 — Ver el pipeline corriendo

1. Entra a tu repositorio en github.com.
2. Clic en la pestaña **Actions** (arriba).
3. Verás tu workflow **"CI/CD - MermaZero"** ejecutándose (círculo amarillo = corriendo).
4. Espera unos minutos. Cuando termine bien, aparece un **check verde ✅**.

## Paso 4 — La evidencia para el docente

Toma capturas de:
1. La pestaña **Actions** con el **check verde** del workflow.
2. Al entrar al workflow, la lista de pasos verdes:
   - "Análisis estático — Ruff"
   - "Análisis estático — Bandit"
   - "Pruebas de regresión (unitarias + E2E) con cobertura"
3. Dentro del workflow, sección **Artifacts**: descarga `reporte-autocorreccion`
   y `cobertura` — son evidencia extra descargable.

Con esas capturas demuestras el criterio **Automatización de Pipelines CI/CD** y,
al estar todo en un repositorio compartido que integra Dev + QA, también el de
**Trabajo colaborativo en entornos DevOps**.

## Nota
El repositorio **público** te da minutos de Actions ilimitados y gratis. Si lo
prefieres privado, también funciona (tiene minutos gratis suficientes).
