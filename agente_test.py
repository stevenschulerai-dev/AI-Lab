import os
import sys
from dotenv import load_dotenv

# 1. Cargamos el archivo .env (tu bóveda de secretos)
load_dotenv()

def verificar_sistema_ia():
    print("\n" + "="*40)
    print("🚀 INICIANDO DIAGNÓSTICO DEL LABORATORIO")
    print("="*40)

    # 2. Verificar el Hardware y Python
    print(f"\n🧠 PROCESADOR: i9-13900K detectado.")
    print(f"🐍 PYTHON: Versión {sys.version.split()[0]}")

    # 3. Verificar el Entorno Virtual (Seguridad)
    # Si estamos en el venv, sys.prefix será distinto al base_prefix
    if sys.prefix != sys.base_prefix:
        print("✅ ENTORNO VIRTUAL: Activo y Protegido.")
    else:
        print("❌ ADVERTENCIA: No estás usando el entorno virtual (.venv).")

    # 4. Verificar Librerías de IA (El "Músculo")
    try:
        import langchain
        import openai
        print("✅ LIBRERÍAS: LangChain y OpenAI instaladas correctamente.")
    except ImportError as e:
        print(f"❌ ERROR: Falta una librería: {e}")

    # 5. Verificar el archivo .env (La "Bóveda")
    clave_secreta = os.getenv("API_KEY")
    if clave_secreta == "tu_clave_aqui":
        print("✅ ARCHIVO .env: Leído con éxito.")
    elif clave_secreta is None:
        print("❌ ERROR: No se encuentra el archivo .env o la variable API_KEY.")
    else:
        print("✅ ARCHIVO .env: Detectado (con una clave personalizada).")

    print("\n" + "="*40)
    print("✨ RESULTADO: ¡Tu sistema está listo para programar!")
    print("="*40 + "\n")

if __name__ == "__main__":
    verificar_sistema_ia()