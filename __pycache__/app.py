from analizador_sintactico import analizar_sintactico   # 👈 al inicio del archivo

# ---- endpoint léxico ----
@app.route('/analizar_lexico', methods=['POST'])
def analizar_lexico():
    ...

# ---- endpoint sintáctico ----
@app.route('/analizar_sintactico', methods=['POST'])
def analizar_sintactico_endpoint():
    try:
        data = request.get_json()
        texto = data.get('texto', '')

        if not texto.strip():
            return jsonify({
                'success': False,
                'error': 'No se proporcionó texto para analizar'
            })

        resultado = analizar_sintactico(texto)

        return jsonify({
            'success': True,
            'resultado': str(resultado) if resultado else "✅ Análisis sintáctico completado"
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error en el análisis sintáctico: {str(e)}'
        })
