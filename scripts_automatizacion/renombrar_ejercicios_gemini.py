"""
Analiza vídeos de ejercicios físicos con Gemini y renombra cada fichero
con el nombre del ejercicio detectado.

Flujo por vídeo:
    1. Sube el fichero a la File API de Gemini.
    2. Espera a que el procesamiento termine (estado ACTIVE).
    3. Pregunta a Gemini qué ejercicio se realiza.
    4. Limpia la respuesta y renombra el fichero.

Uso:
    python renombrar_ejercicios_gemini.py --carpeta /ruta/a/videos
    python renombrar_ejercicios_gemini.py --carpeta /ruta/a/videos --modelo gemini-1.5-pro

Requiere:
    GEMINI_API_KEY en variable de entorno o fichero .env en el mismo directorio.
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

try:
    import google.generativeai as genai
except ImportError:
    sys.exit(
        "Dependencia faltante. Ejecuta:\n  pip install google-generativeai"
    )

# Extensiones de vídeo soportadas por la File API de Gemini
EXTENSIONES_VIDEO = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".mpeg", ".mpg"}

PROMPT_ANALISIS = (
    "Observa este vídeo de ejercicio físico. "
    "Responde ÚNICAMENTE con el nombre del ejercicio en español, "
    "en minúsculas y sin signos de puntuación. "
    "Ejemplos válidos: sentadilla, press banca, peso muerto, dominadas, "
    "plancha, zancada, remo con barra. "
    "Si no puedes identificar el ejercicio, responde exactamente: desconocido."
)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def limpiar_nombre(texto: str) -> str:
    """Convierte el texto en un nombre de fichero válido."""
    texto = texto.strip().lower()
    # Reemplaza tildes y caracteres especiales comunes
    reemplazos = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ü": "u", "ñ": "n",
    }
    for origen, destino in reemplazos.items():
        texto = texto.replace(origen, destino)
    # Solo letras, dígitos, guiones y espacios → guiones bajos
    texto = re.sub(r"[^\w\s-]", "", texto)
    texto = re.sub(r"[\s-]+", "_", texto)
    return texto or "desconocido"


def nombre_sin_colision(destino: Path) -> Path:
    """Añade sufijo numérico si el fichero destino ya existe."""
    if not destino.exists():
        return destino
    stem, suffix, parent = destino.stem, destino.suffix, destino.parent
    contador = 1
    while True:
        candidato = parent / f"{stem}_{contador}{suffix}"
        if not candidato.exists():
            return candidato
        contador += 1


def cargar_api_key() -> str:
    """Lee GEMINI_API_KEY del entorno o de un .env local."""
    clave = os.environ.get("GEMINI_API_KEY", "")
    if not clave:
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            for linea in env_path.read_text(encoding="utf-8").splitlines():
                if linea.startswith("GEMINI_API_KEY"):
                    _, _, clave = linea.partition("=")
                    clave = clave.strip().strip('"').strip("'")
                    break
    if not clave:
        sys.exit(
            "No se encontró GEMINI_API_KEY.\n"
            "Defínela como variable de entorno o en un fichero .env:\n"
            "  GEMINI_API_KEY=tu_clave_aqui"
        )
    return clave


# ---------------------------------------------------------------------------
# Lógica de Gemini
# ---------------------------------------------------------------------------

def subir_y_esperar(ruta: Path, verbose: bool = True) -> genai.types.File:
    """Sube el vídeo a la File API y espera hasta que esté listo."""
    if verbose:
        print(f"  Subiendo '{ruta.name}'...", end=" ", flush=True)

    fichero = genai.upload_file(path=str(ruta), mime_type="video/mp4")

    # Espera activa hasta estado ACTIVE (puede tardar según tamaño)
    while fichero.state.name == "PROCESSING":
        time.sleep(5)
        fichero = genai.get_file(fichero.name)

    if fichero.state.name != "ACTIVE":
        raise RuntimeError(
            f"El fichero quedó en estado inesperado: {fichero.state.name}"
        )

    if verbose:
        print("listo.")
    return fichero


def identificar_ejercicio(fichero_gemini, modelo: genai.GenerativeModel) -> str:
    """Envía el vídeo a Gemini y devuelve el nombre del ejercicio limpio."""
    respuesta = modelo.generate_content([fichero_gemini, PROMPT_ANALISIS])
    texto = respuesta.text.strip()
    return limpiar_nombre(texto)


def eliminar_fichero_remoto(fichero_gemini) -> None:
    """Borra el fichero de la File API para no consumir cuota de almacenamiento."""
    try:
        genai.delete_file(fichero_gemini.name)
    except Exception:
        pass  # No es crítico si falla la limpieza


# ---------------------------------------------------------------------------
# Proceso principal
# ---------------------------------------------------------------------------

def procesar_carpeta(carpeta: Path, nombre_modelo: str, dry_run: bool) -> None:
    videos = [
        f for f in sorted(carpeta.iterdir())
        if f.is_file() and f.suffix.lower() in EXTENSIONES_VIDEO
    ]

    if not videos:
        print(f"No se encontraron vídeos en '{carpeta}'.")
        return

    print(f"Vídeos encontrados: {len(videos)}\n")
    modelo = genai.GenerativeModel(model_name=nombre_modelo)

    exitosos, fallidos = 0, 0

    for i, ruta in enumerate(videos, start=1):
        print(f"[{i}/{len(videos)}] {ruta.name}")
        fichero_gemini = None
        try:
            fichero_gemini = subir_y_esperar(ruta)
            ejercicio = identificar_ejercicio(fichero_gemini, modelo)
            print(f"  Ejercicio detectado: {ejercicio}")

            destino = nombre_sin_colision(ruta.parent / f"{ejercicio}{ruta.suffix.lower()}")

            if dry_run:
                print(f"  [dry-run] Renombraría a: {destino.name}")
            else:
                ruta.rename(destino)
                print(f"  Renombrado a: {destino.name}")

            exitosos += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            fallidos += 1

        finally:
            if fichero_gemini:
                eliminar_fichero_remoto(fichero_gemini)

        print()

    print("=" * 50)
    print(f"Completado: {exitosos} OK, {fallidos} errores.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Renombra vídeos de ejercicios usando Gemini (IEC 60909)."
    )
    parser.add_argument(
        "--carpeta",
        required=True,
        type=Path,
        help="Carpeta que contiene los vídeos a analizar.",
    )
    parser.add_argument(
        "--modelo",
        default="gemini-1.5-flash",
        help="Modelo Gemini a usar (default: gemini-1.5-flash).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra los renombrados sin ejecutarlos.",
    )
    args = parser.parse_args()

    if not args.carpeta.is_dir():
        sys.exit(f"La carpeta '{args.carpeta}' no existe o no es un directorio.")

    genai.configure(api_key=cargar_api_key())
    procesar_carpeta(args.carpeta, args.modelo, args.dry_run)


if __name__ == "__main__":
    main()
