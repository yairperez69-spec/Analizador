from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

class AnalizadorLexico:
    def __init__(self):
        # Palabras reservadas (en minúsculas para comparación)
        self.palabras_reservadas = {'if', 'for', 'while'}

        # Tokens definidos con expresiones regulares
        # IMPORTANTE: El orden importa - tokens más largos primero
        self.tokens = {
            'INCREMENT': r'\+\+',
            'DECREMENT': r'--',
            'LESSTHANOREQUAL': r'<=',
            'GREATERTHANOREQUAL': r'>=',
            'EQUALITY': r'==',
            'NOTEQUAL': r'!=',
            'LOGICALAND': r'&&',
            'LOGICALOR': r'\|\|',
            'ASSIGN': r'=',           # ← AQUÍ ESTÁ EL SÍMBOLO = que pediste
            'LPAREN': r'\(',
            'RPAREN': r'\)',
            'LBRACE': r'\{',
            'RBRACE': r'\}',
            'LBRACKET': r'\[',
            'RBRACKET': r'\]',
            'SEMICOLON': r';',
            'COMMA': r',',
            'DOT': r'\.',
            'LESSTHAN': r'<',
            'GREATERTHAN': r'>',
            'PLUS': r'\+',
            'MINUS': r'-',
            'MULTIPLY': r'\*',
            'DIVIDE': r'/',
            'MODULO': r'%',
            'NOT': r'!',
            'QUESTION': r'\?',
            'COLON': r':',
            'NUMBER': r'\d+(\.\d+)?',  # Soporte para decimales
            'IDENTIFIER': r'[a-zA-Z_][a-zA-Z0-9_]*'
        }

    def analizar(self, texto):
        if not texto.strip():
            return [], 0, 0, 0, 0

        # Crear regex maestro con todos los tokens
        token_regex = '|'.join(f'(?P<{nombre}>{patron})' for nombre, patron in self.tokens.items())

        resultados = []
        posicion = 1

        # Contadores para estadísticas
        contador_palabras_reservadas = 0
        contador_identificadores = 0
        contador_numeros = 0
        contador_simbolos = 0

        # Buscar coincidencias
        for match in re.finditer(token_regex, texto):
            tipo = match.lastgroup
            valor = match.group()

            # Crear estructura base del resultado
            resultado = {
                'token': valor,
                'posicion': posicion,
                'palabra_reservada': '',
                'simbolo': '',
                'parentesis_izq': '',
                'parentesis_der': ''
            }

            # Verificar si es palabra reservada (comparación case-insensitive)
            if tipo == 'IDENTIFIER' and valor.lower() in self.palabras_reservadas:
                resultado.update({
                    'tipo': 'PALABRA_RESERVADA',
                    'color': 'success',
                    'palabra_reservada': '✓',
                    'estado': 'Palabra Clave'
                })
                contador_palabras_reservadas += 1
            elif tipo == 'IDENTIFIER':
                resultado.update({
                    'tipo': 'IDENTIFICADOR',
                    'color': 'info',
                    'estado': 'Variable'
                })
                contador_identificadores += 1
            elif tipo == 'NUMBER':
                resultado.update({
                    'tipo': 'NUMERO',
                    'color': 'primary',
                    'estado': 'Valor Numérico'
                })
                contador_numeros += 1
            elif tipo == 'LPAREN':
                resultado.update({
                    'tipo': 'PARENTESIS_IZQ',
                    'color': 'warning',
                    'simbolo': '✓',
                    'parentesis_izq': '✓',
                    'estado': 'Delimitador'
                })
                contador_simbolos += 1
            elif tipo == 'RPAREN':
                resultado.update({
                    'tipo': 'PARENTESIS_DER',
                    'color': 'warning',
                    'simbolo': '✓',
                    'parentesis_der': '✓',
                    'estado': 'Delimitador'
                })
                contador_simbolos += 1
            else:
                # Otros símbolos
                tipo_traducido = self._traducir_tipo(tipo)
                resultado.update({
                    'tipo': tipo_traducido,
                    'color': 'warning',
                    'simbolo': '✓',
                    'estado': 'Símbolo'
                })
                contador_simbolos += 1

            resultados.append(resultado)
            posicion += 1

        return resultados, contador_palabras_reservadas, contador_identificadores, contador_numeros, contador_simbolos

    def _traducir_tipo(self, tipo):
        """Traduce los tipos de tokens al español"""
        traducciones = {
            'INCREMENT': 'INCREMENTO',
            'DECREMENT': 'DECREMENTO', 
            'ASSIGN': 'ASIGNACION',        # ← Aquí se traduce el símbolo =
            'EQUALITY': 'IGUALDAD',
            'NOTEQUAL': 'DIFERENTE',
            'LPAREN': 'PARENTESIS_IZQ',
            'RPAREN': 'PARENTESIS_DER',
            'LBRACE': 'LLAVE_IZQ',
            'RBRACE': 'LLAVE_DER',
            'LBRACKET': 'CORCHETE_IZQ',
            'RBRACKET': 'CORCHETE_DER',
            'SEMICOLON': 'PUNTO_COMA',
            'COMMA': 'COMA',
            'PLUS': 'SUMA',
            'MINUS': 'RESTA',
            'MULTIPLY': 'MULTIPLICACION',
            'DIVIDE': 'DIVISION',
            'MODULO': 'MODULO',
            'LESSTHAN': 'MENOR_QUE',
            'GREATERTHAN': 'MAYOR_QUE',
            'LESSTHANOREQUAL': 'MENOR_IGUAL',
            'GREATERTHANOREQUAL': 'MAYOR_IGUAL',
            'LOGICALAND': 'Y_LOGICO',
            'LOGICALOR': 'O_LOGICO',
            'NOT': 'NEGACION',
            'DOT': 'PUNTO',
            'QUESTION': 'INTERROGACION',
            'COLON': 'DOS_PUNTOS'
        }
        return traducciones.get(tipo, tipo)

    def _obtener_descripcion(self, tipo, valor):
        """Obtiene una descripción amigable para cada tipo de token"""
        descripciones = {
            'ASIGNACION': f'Operador de asignación ({valor})',  # ← Descripción para =
            'IGUALDAD': 'Operador de comparación',
            'INCREMENTO': 'Operador de incremento',
            'DECREMENTO': 'Operador de decremento',
            'SUMA': 'Operador aritmético',
            'RESTA': 'Operador aritmético',
            'MULTIPLICACION': 'Operador aritmético',
            'DIVISION': 'Operador aritmético',
            'MENOR_QUE': 'Operador de comparación',
            'MAYOR_QUE': 'Operador de comparación',
            'PARENTESIS_IZQ': 'Delimitador de expresión',
            'PARENTESIS_DER': 'Delimitador de expresión',
            'LLAVE_IZQ': 'Delimitador de bloque',
            'LLAVE_DER': 'Delimitador de bloque',
            'PUNTO_COMA': 'Terminador de sentencia'
        }
        return descripciones.get(tipo, f'Símbolo: {valor}')


# Instancia del analizador
analizador = AnalizadorLexico()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar', methods=['POST'])
def analizar_texto():
    try:
        data = request.get_json()
        texto = data.get('texto', '')
        
        if not texto.strip():
            return jsonify({
                'success': False,
                'error': 'No se proporcionó texto para analizar'
            })
        
        resultados, palabras_reservadas, identificadores, numeros, simbolos = analizador.analizar(texto)
        
        return jsonify({
            'success': True,
            'resultados': resultados,
            'total_tokens': len(resultados),
            'palabras_reservadas': palabras_reservadas,
            'identificadores': identificadores,
            'numeros': numeros,
            'simbolos': simbolos,
            'mensaje': f'Se analizaron {len(resultados)} tokens correctamente'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error al analizar: {str(e)}'
        })

@app.route('/test')
def test():
    """Endpoint de prueba para verificar que el servidor funciona"""
    return jsonify({
        'status': 'OK',
        'message': 'El analizador léxico está funcionando correctamente',
        'tokens_soportados': list(analizador.tokens.keys()),
        'palabras_reservadas': list(analizador.palabras_reservadas)
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Error interno del servidor'}), 500


if __name__ == '__main__':
    print("🚀 Iniciando el Analizador Léxico...")
    print("📍 Disponible en: http://localhost:5000")
    print("🧪 Endpoint de prueba: http://localhost:5000/test")
    print("📝 Tokens soportados:")
    
    analizador_test = AnalizadorLexico()
    for token in analizador_test.tokens.keys():
        print(f"   - {token}")
    
    print(f"🔤 Palabras reservadas: {', '.join(analizador_test.palabras_reservadas)}")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)


    