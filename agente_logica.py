def agente_soporte(mensaje_usuario):
    print(f"\n🤖 Agente analizando: '{mensaje_usuario}'")
    
    # 1. Fase de Pensamiento (Lógica de "detrás de escena")
    mensaje = mensaje_usuario.lower()
    
    # 2. Fase de Decisión (El flujo de trabajo)
    if "pago" in mensaje or "factura" in mensaje:
        destino = "Departamento de FINANZAS"
        prioridad = "ALTA"
    elif "error" in mensaje or "no funciona" in mensaje:
        destino = "Departamento de IT (Soporte Técnico)"
        prioridad = "CRÍTICA"
    elif "hola" in mensaje or "gracias" in mensaje:
        destino = "Atención al Cliente"
        prioridad = "BAJA"
    else:
        destino = "Mesa de Ayuda General"
        prioridad = "MEDIA"
    
    # 3. Resultado del Proceso
    return f"📍 Acción: Enviar a [{destino}] | ⚡ Prioridad: {prioridad}"

# --- SIMULACIÓN DEL FLUJO ---
pedidos = [
    "Hola, quería dar las gracias por el servicio",
    "¡Ayuda! Mi base de datos da un error 500 y no funciona nada",
    "No entiendo el cobro de mi última factura"
]

for p in pedidos:
    resultado = agente_soporte(p)
    print(resultado)