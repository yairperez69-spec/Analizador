from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

class AnalizadorLexico:
    def __init__(self):
        # Palabras reservadas (en minúsculas para comparación)
        self.palabras_reservadas = {'if', 'for', 'while'}

        # Tokens definidos con expresiones regulares
        self.tokens = {
            'INCREMENT': r'\+\+',
            'LESSTHANOREQUAL': r'<=',
            'LPAREN': r'\(',
            'RPAREN': r'\)',
            'LBRACE': r'\{',
            'RBRACE': r'\}',
            'SEMICOLON': r';',
            'ASSIGN': r'=',
            'DOT': r'\.',
            'LESSTHAN': r'<',
            'GREATERTHAN': r'>',
            'PLUS': r'\+',
            'NUMBER': r'\d+',
            'IDENTIFIER': r'[a-zA-Z_][a-zA-Z0-9_]*'
        }

    def analizar(self, texto):
        if not texto.strip():
            return []

        # Crear regex maestro con todos los tokens
        token_regex = '|'.join(f'(?P<{nombre}>{patron})' for nombre, patron in self.tokens.items())

        resultados = []
        posicion = 1

        # Contadores para estadísticas
        contador_palabras_reservadas = 0
        contador_identificadores = 0

        # Buscar coincidencias
        for match in re.finditer(token_regex, texto):
            tipo = match.lastgroup
            valor = match.group()

            # Verificar si es palabra reservada (comparación case-insensitive)
            if valor.lower() in self.palabras_reservadas:
                resultados.append({
                    'token': valor,
                    'tipo': 'PALABRA_RESERVADA',
                    'color': 'success',
                    'posicion': posicion
                })
                contador_palabras_reservadas += 1
            elif tipo == 'IDENTIFIER':
                resultados.append({
                    'token': valor,
                    'tipo': 'IDENTIFIER',
                    'color': 'info',
                    'posicion': posicion
                })
                contador_identificadores += 1
            elif tipo == 'NUMBER':
                resultados.append({
                    'token': valor,
                    'tipo': 'NUMBER',
                    'color': 'primary',
                    'posicion': posicion
                })
            else:
                # Otros símbolos
                resultados.append({
                    'token': valor,
                    'tipo': tipo,
                    'color': 'warning',
                    'posicion': posicion
                })

            posicion += 1

        return resultados, contador_palabras_reservadas, contador_identificadores


# Instancia del analizador
analizador = AnalizadorLexico()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analizar', methods=['POST'])
def analizar_texto():
    data = request.get_json()
    texto = data.get('texto', '')
    
    resultados, palabras_reservadas, identificadores = analizador.analizar(texto)
    
    return jsonify({
        'success': True,
        'resultados': resultados,
        'total_tokens': len(resultados),
        'palabras_reservadas': palabras_reservadas,
        'identificadores': identificadores
    })


if __name__ == '__main__':
    app.run(debug=True)