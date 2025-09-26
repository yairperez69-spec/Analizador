from flask import Flask, render_template, request, jsonify
import re
from analizadorsintactico import analizarsintactico   # 👈 Importamos el parser

app = Flask(__name__)

# =======================
#   ANALIZADOR LÉXICO
# =======================
class AnalizadorLexico:
    def __init__(self):
        # Palabras reservadas
        self.palabras_reservadas = {'if', 'else', 'for', 'while', 'int', 'float', 'return', 'void'}

        # Tokens con expresiones regulares
        self.tokens = {
            'INCREMENT': r'\+\+',
            'DECREMENT': r'--',
            'LESSTHANOREQUAL': r'<=',
            'GREATERTHANOREQUAL': r'>=',
            'EQUALITY': r'==',
            'NOTEQUAL': r'!=',
            'LOGICALAND': r'&&',
            'LOGICALOR': r'\|\|',
            'ASSIGN': r'=',
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
            'NUMBER': r'\d+(\.\d+)?',
            'IDENTIFIER': r'[a-zA-Z_][a-zA-Z0-9_]*'
        }

    def analizar(self, texto):
        if not texto.strip():
            return [], 0, 0, 0, 0

        token_regex = '|'.join(f'(?P<{nombre}>{patron})' for nombre, patron in self.tokens.items())
        resultados = []
        posicion = 1
        contador_palabras_reservadas = 0
        contador_identificadores = 0
        contador_numeros = 0
        contador_simbolos = 0

        for match in re.finditer(token_regex, texto):
            tipo = match.lastgroup
            valor = match.group()

            resultado = {
                'token': valor,
                'posicion': posicion,
                'palabra_reservada': '',
                'simbolo': '',
                'parentesis_izq': '',
                'parentesis_der': ''
            }

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
        traducciones = {
            'INCREMENT': 'INCREMENTO',
            'DECREMENT': 'DECREMENTO', 
            'ASSIGN': 'ASIGNACION',
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


# Instancia del analizador léxico
analizador_lexico = AnalizadorLexico()

# =======================
#   RUTAS FLASK
# =======================
@app.route('/')
def index():
    return render_template('index.html')

# --- Endpoint Análisis Léxico ---
@app.route('/analizar_lexico', methods=['POST'])
def analizar_lexico():
    try:
        data = request.get_json()
        texto = data.get('texto', '')
        
        if not texto.strip():
            return jsonify({
                'success': False,
                'error': 'No se proporcionó texto para analizar'
            })
        
        resultados, palabras_reservadas, identificadores, numeros, simbolos = analizador_lexico.analizar(texto)
        
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

# --- Endpoint Análisis Sintáctico ---
@app.route('/analizar_sintactico', methods=['POST'])
def analizar_sintactico_endpoint():
    try:
        data = request.get_json()
        texto = data.get('texto', '')

        if not texto.strip():
            return jsonify({
                'success': False,
                'error': 'No se proporcionó texto para analizar',
                'errores': ['Texto vacío'],
                'resultados_sintacticos': [],
                'tokens_lexicos': [],
                'total_estructuras': 0,
                'total_errores': 1
            })

        # Llamar al analizador sintáctico
        resultado = analizarsintactico(texto)
        
        # El resultado ya viene en el formato correcto
        return jsonify(resultado)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error en el análisis sintáctico: {str(e)}',
            'errores': [f'Error interno: {str(e)}'],
            'resultados_sintacticos': [],
            'tokens_lexicos': [],
            'total_estructuras': 0,
            'total_errores': 1
        })

# --- Endpoint Test ---
@app.route('/test')
def test():
    return jsonify({
        'status': 'OK',
        'message': 'Analizador léxico y sintáctico funcionando',
        'tokens_soportados': list(analizador_lexico.tokens.keys()),
        'palabras_reservadas': list(analizador_lexico.palabras_reservadas),
        'estructuras_sintacticas': [
            'Declaraciones de variables: int x = 5;',
            'Asignaciones: x = 10;',
            'Estructuras FOR: for(i=0; i<10; i++) { }',
            'Expresiones aritméticas: x + y * 2',
            'Expresiones de comparación: x > 5'
        ]
    })

# --- Endpoint para ejemplos ---
@app.route('/ejemplos')
def ejemplos():
    return jsonify({
        'ejemplos': [
            {
                'nombre': 'Declaración simple',
                'codigo': 'int x = 5;',
                'descripcion': 'Declaración de variable entera con inicialización'
            },
            {
                'nombre': 'Estructura FOR completa',
                'codigo': 'for(i=0; i<10; i++) {\n    int y = i * 2;\n}',
                'descripcion': 'Bucle for con inicialización, condición, incremento y bloque'
            },
            {
                'nombre': 'Múltiples declaraciones',
                'codigo': 'int x = 5;\nfloat y = 3.14;\nint z = x + 2;',
                'descripcion': 'Varias declaraciones de variables'
            },
            {
                'nombre': 'Asignación simple',
                'codigo': 'x = 10;',
                'descripcion': 'Asignación de valor a variable existente'
            },
            {
                'nombre': 'Error sintáctico',
                'codigo': 'int = 5;',
                'descripcion': 'Declaración incompleta (falta identificador)'
            }
        ]
    })

# =======================
#   MAIN
# =======================
if __name__ == '__main__':
    print("🚀 Iniciando Analizador Léxico y Sintáctico...")
    print("📍 Disponible en: http://localhost:5000")
    print("🧪 Endpoint de prueba: GET -> http://localhost:5000/test")
    print("🧪 Endpoint léxico: POST -> http://localhost:5000/analizar_lexico")
    print("🧪 Endpoint sintáctico: POST -> http://localhost:5000/analizar_sintactico")
    print("📚 Ejemplos disponibles: GET -> http://localhost:5000/ejemplos")
    print("=" * 60)
    print("📋 Estructuras sintácticas soportadas:")
    print("   • Declaraciones: int x = 5;")
    print("   • Asignaciones: x = 10;")
    print("   • Bucles FOR: for(i=0; i<10; i++) { ... }")
    print("   • Expresiones aritméticas y lógicas")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)