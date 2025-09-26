import re

class GramaticaCompleta:
    def __init__(self):
        # Tokens regex optimizados
        self.tokens_regex = {
            'COMMENT_MULTI': r'/\*.*?\*/', 'COMMENT_SINGLE': r'//.*', 'STRING': r'"([^"\\]|\\.)*"',
            'CHAR': r"'([^'\\]|\\.)'", 'LEFT_SHIFT_ASSIGN': r'<<=', 'RIGHT_SHIFT_ASSIGN': r'>>=',
            'LEFT_SHIFT': r'<<', 'RIGHT_SHIFT': r'>>', 'INCREMENT': r'\+\+', 'DECREMENT': r'--',
            'ARROW': r'->', 'LESSTHANOREQUAL': r'<=', 'GREATERTHANOREQUAL': r'>=', 'EQUALITY': r'==',
            'NOTEQUAL': r'!=', 'LOGICALAND': r'&&', 'LOGICALOR': r'\|\|', 'PLUS_ASSIGN': r'\+=',
            'MINUS_ASSIGN': r'-=', 'MULTIPLY_ASSIGN': r'\*=', 'DIVIDE_ASSIGN': r'/=', 'MODULO_ASSIGN': r'%=',
            'BITWISE_AND_ASSIGN': r'&=', 'BITWISE_OR_ASSIGN': r'\|=', 'BITWISE_XOR_ASSIGN': r'\^=',
            'ASSIGN': r'=', 'PLUS': r'\+', 'MINUS': r'-', 'MULTIPLY': r'\*', 'DIVIDE': r'/',
            'MODULO': r'%', 'LESSTHAN': r'<', 'GREATERTHAN': r'>', 'NOT': r'!', 'BITWISE_AND': r'&',
            'BITWISE_OR': r'\|', 'BITWISE_XOR': r'\^', 'BITWISE_NOT': r'~', 'LPAREN': r'\(',
            'RPAREN': r'\)', 'LBRACE': r'\{', 'RBRACE': r'\}', 'LBRACKET': r'\[', 'RBRACKET': r'\]',
            'SEMICOLON': r';', 'COMMA': r',', 'DOT': r'\.', 'QUESTION': r'\?', 'COLON': r':',
            'FLOAT': r'\d+\.\d*([eE][+-]?\d+)?[fF]?|\d+[eE][+-]?\d+[fF]?|\d+[fF]', 'NUMBER': r'\d+',
            'IDENTIFIER': r'[a-zA-Z_][a-zA-Z0-9_]*', 'WHITESPACE': r'\s+',
        }
        
        self.palabras_reservadas = {'if','else','switch','case','default','while','for','do','break',
            'continue','return','int','float','double','char','bool','void','true','false'}
        self.errores = []
        self.estructuras_reconocidas = []
        self.tokens_encontrados = []

    def tokenizar(self, texto):
        token_regex = '|'.join(f'(?P<{nombre}>{patron})' for nombre, patron in self.tokens_regex.items())
        tokens = []
        for match in re.finditer(token_regex, texto, re.DOTALL):
            tipo, valor = match.lastgroup, match.group()
            if tipo in ['WHITESPACE', 'COMMENT_SINGLE', 'COMMENT_MULTI']: continue
            if tipo == 'IDENTIFIER' and valor.lower() in self.palabras_reservadas:
                tokens.append({'tipo': valor.upper(), 'valor': valor, 'posicion': match.start()})
            else: tokens.append({'tipo': tipo, 'valor': valor, 'posicion': match.start()})
        return tokens

    def analizar_programa(self, tokens, inicio=0):
        pos = inicio
        while pos < len(tokens):
            if tokens[pos]['tipo'] in ['INT','FLOAT','DOUBLE','CHAR','BOOL','VOID']:
                exito, nuevo_pos, mensaje = self.analizar_declaracion(tokens, pos)
            else:
                exito, nuevo_pos, mensaje = self.analizar_sentencia(tokens, pos)
            
            if exito:
                self.estructuras_reconocidas.append(f"✅ {mensaje}")
                pos = nuevo_pos
            else:
                self.errores.append(f"❌ {mensaje}")
                pos += 1
        return True, pos, "Programa analizado"

    def analizar_declaracion(self, tokens, inicio=0):
        pos = inicio
        if pos >= len(tokens) or tokens[pos]['tipo'] not in ['INT','FLOAT','DOUBLE','CHAR','BOOL','VOID']:
            return False, pos, "Se esperaba tipo de dato"
        tipo = tokens[pos]['valor']
        pos += 1
        
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'IDENTIFIER':
            return False, pos, "Se esperaba identificador después del tipo"
        identificador = tokens[pos]['valor']
        pos += 1
        
        # Array opcional
        if pos < len(tokens) and tokens[pos]['tipo'] == 'LBRACKET':
            pos += 1
            if pos >= len(tokens) or tokens[pos]['tipo'] != 'NUMBER':
                return False, pos, "Se esperaba tamaño del array"
            pos += 1
            if pos >= len(tokens) or tokens[pos]['tipo'] != 'RBRACKET':
                return False, pos, "Se esperaba ']'"
            pos += 1
            
            if pos < len(tokens) and tokens[pos]['tipo'] == 'ASSIGN':
                pos += 1
                if pos >= len(tokens) or tokens[pos]['tipo'] != 'LBRACE':
                    return False, pos, "Se esperaba '{' para inicialización del array"
                pos += 1
                if pos < len(tokens) and tokens[pos]['tipo'] != 'RBRACE':
                    exito, pos, error = self.analizar_lista_valores(tokens, pos)
                    if not exito: return False, pos, f"Error en lista de valores: {error}"
                if pos >= len(tokens) or tokens[pos]['tipo'] != 'RBRACE':
                    return False, pos, "Se esperaba '}'"
                pos += 1
        elif pos < len(tokens) and tokens[pos]['tipo'] == 'ASSIGN':
            pos += 1
            exito, pos, error = self.analizar_expresion(tokens, pos)
            if not exito: return False, pos, f"Error en inicialización: {error}"
        
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'SEMICOLON':
            return False, pos, "Se esperaba ';'"
        return True, pos + 1, f"Declaración: {tipo} {identificador}"

    def analizar_sentencia(self, tokens, inicio=0):
        pos = inicio
        if pos >= len(tokens): return False, pos, "No hay tokens para analizar"
        
        if tokens[pos]['tipo'] == 'LBRACE': return self.analizar_bloque(tokens, pos)
        elif tokens[pos]['tipo'] == 'IF': return self.analizar_sentencia_if(tokens, pos)
        elif tokens[pos]['tipo'] == 'SWITCH': return self.analizar_sentencia_switch(tokens, pos)
        elif tokens[pos]['tipo'] == 'WHILE': return self.analizar_sentencia_while(tokens, pos)
        elif tokens[pos]['tipo'] == 'FOR': return self.analizar_sentencia_for(tokens, pos)
        elif tokens[pos]['tipo'] == 'DO': return self.analizar_sentencia_do_while(tokens, pos)
        elif tokens[pos]['tipo'] in ['BREAK','CONTINUE','RETURN']: return self.analizar_sentencia_salto(tokens, pos)
        else: return self.analizar_sentencia_expresion(tokens, pos)

    def analizar_bloque(self, tokens, inicio=0):
        pos = inicio
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'LBRACE':
            return False, pos, "Se esperaba '{'"
        pos += 1
        
        while pos < len(tokens) and tokens[pos]['tipo'] != 'RBRACE':
            if tokens[pos]['tipo'] in ['INT','FLOAT','DOUBLE','CHAR','BOOL','VOID']:
                exito, pos, error = self.analizar_declaracion(tokens, pos)
                if not exito: return False, pos, f"Error en declaración del bloque: {error}"
            else:
                exito, pos, error = self.analizar_sentencia(tokens, pos)
                if not exito: return False, pos, f"Error en sentencia del bloque: {error}"
        
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'RBRACE':
            return False, pos, "Se esperaba '}'"
        return True, pos + 1, "Bloque válido"

    def analizar_sentencia_expresion(self, tokens, inicio=0):
        pos = inicio
        if pos < len(tokens) and tokens[pos]['tipo'] != 'SEMICOLON':
            exito, pos, error = self.analizar_expresion(tokens, pos)
            if not exito: return False, pos, f"Error en expresión: {error}"
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'SEMICOLON':
            return False, pos, "Se esperaba ';'"
        return True, pos + 1, "Sentencia de expresión válida"

    def analizar_sentencia_if(self, tokens, inicio=0):
        pos = inicio
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'IF': return False, pos, "Se esperaba 'if'"
        pos += 1
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'LPAREN': return False, pos, "Se esperaba '(' después de 'if'"
        pos += 1
        exito, pos, error = self.analizar_expresion(tokens, pos)
        if not exito: return False, pos, f"Error en condición del if: {error}"
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'RPAREN': return False, pos, "Se esperaba ')' después de la condición"
        pos += 1
        exito, pos, error = self.analizar_sentencia(tokens, pos)
        if not exito: return False, pos, f"Error en cuerpo del if: {error}"
        
        if pos < len(tokens) and tokens[pos]['tipo'] == 'ELSE':
            pos += 1
            exito, pos, error = self.analizar_sentencia(tokens, pos)
            if not exito: return False, pos, f"Error en cuerpo del else: {error}"
        return True, pos, "Sentencia if válida"

    def analizar_sentencia_for(self, tokens, inicio=0):
        pos = inicio
        required_checks = [('FOR', "'for'"), ('LPAREN', "'(' después de 'for'")]
        for check_type, error_msg in required_checks:
            if pos >= len(tokens) or tokens[pos]['tipo'] != check_type:
                return False, pos, f"Se esperaba {error_msg}"
            pos += 1
        
        # Tres expresiones del for
        for i, desc in enumerate(['inicialización', 'condición', 'actualización']):
            if pos < len(tokens) and tokens[pos]['tipo'] != 'SEMICOLON' and (i < 2 or tokens[pos]['tipo'] != 'RPAREN'):
                exito, pos, error = self.analizar_expresion(tokens, pos)
                if not exito: return False, pos, f"Error en {desc} del for: {error}"
            
            if i < 2:  # Primeras dos necesitan ';'
                if pos >= len(tokens) or tokens[pos]['tipo'] != 'SEMICOLON':
                    return False, pos, f"Se esperaba ';' después de la {desc}"
                pos += 1
        
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'RPAREN':
            return False, pos, "Se esperaba ')' después de la actualización"
        pos += 1
        exito, pos, error = self.analizar_sentencia(tokens, pos)
        if not exito: return False, pos, f"Error en cuerpo del for: {error}"
        return True, pos, "Sentencia for válida"

    def analizar_sentencia_while(self, tokens, inicio=0):
        return self._analizar_bucle_simple(tokens, inicio, 'WHILE', 'while', "Sentencia while válida")

    def analizar_sentencia_do_while(self, tokens, inicio=0):
        pos = inicio
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'DO': return False, pos, "Se esperaba 'do'"
        pos += 1
        exito, pos, error = self.analizar_sentencia(tokens, pos)
        if not exito: return False, pos, f"Error en cuerpo del do: {error}"
        
        checks = [('WHILE', "'while' después del cuerpo do"), ('LPAREN', "'(' después de 'while'")]
        for check_type, error_msg in checks:
            if pos >= len(tokens) or tokens[pos]['tipo'] != check_type:
                return False, pos, f"Se esperaba {error_msg}"
            pos += 1
        
        exito, pos, error = self.analizar_expresion(tokens, pos)
        if not exito: return False, pos, f"Error en condición del while: {error}"
        
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'RPAREN':
            return False, pos, "Se esperaba ')' después de la condición"
        pos += 1
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'SEMICOLON':
            return False, pos, "Se esperaba ';' después del do-while"
        return True, pos + 1, "Sentencia do-while válida"

    def _analizar_bucle_simple(self, tokens, inicio, token_tipo, palabra, mensaje_exito):
        pos = inicio
        checks = [(token_tipo, f"'{palabra}'"), ('LPAREN', f"'(' después de '{palabra}'")]
        for check_type, error_msg in checks:
            if pos >= len(tokens) or tokens[pos]['tipo'] != check_type:
                return False, pos, f"Se esperaba {error_msg}"
            pos += 1
        
        exito, pos, error = self.analizar_expresion(tokens, pos)
        if not exito: return False, pos, f"Error en condición del {palabra}: {error}"
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'RPAREN':
            return False, pos, "Se esperaba ')' después de la condición"
        pos += 1
        exito, pos, error = self.analizar_sentencia(tokens, pos)
        if not exito: return False, pos, f"Error en cuerpo del {palabra}: {error}"
        return True, pos, mensaje_exito

    def analizar_sentencia_salto(self, tokens, inicio=0):
        pos = inicio
        if pos >= len(tokens) or tokens[pos]['tipo'] not in ['BREAK','CONTINUE','RETURN']:
            return False, pos, "Se esperaba break, continue o return"
        tipo_salto = tokens[pos]['valor']
        pos += 1
        
        if tipo_salto == 'return' and pos < len(tokens) and tokens[pos]['tipo'] != 'SEMICOLON':
            exito, pos, error = self.analizar_expresion(tokens, pos)
            if not exito: return False, pos, f"Error en expresión de return: {error}"
        
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'SEMICOLON':
            return False, pos, f"Se esperaba ';' después de {tipo_salto}"
        return True, pos + 1, f"Sentencia {tipo_salto} válida"

    def analizar_expresion(self, tokens, inicio=0):
        return self.analizar_expresion_asignacion(tokens, inicio)

    def analizar_expresion_asignacion(self, tokens, inicio=0):
        pos = inicio
        exito, pos, error = self.analizar_expresion_ternaria(tokens, pos)
        if not exito: return False, pos, error
        
        assign_ops = ['ASSIGN','PLUS_ASSIGN','MINUS_ASSIGN','MULTIPLY_ASSIGN','DIVIDE_ASSIGN',
                     'MODULO_ASSIGN','BITWISE_AND_ASSIGN','BITWISE_OR_ASSIGN','BITWISE_XOR_ASSIGN',
                     'LEFT_SHIFT_ASSIGN','RIGHT_SHIFT_ASSIGN']
        if pos < len(tokens) and tokens[pos]['tipo'] in assign_ops:
            pos += 1
            exito, pos, error = self.analizar_expresion_asignacion(tokens, pos)
            if not exito: return False, pos, f"Error después del operador de asignación: {error}"
        return True, pos, "Expresión de asignación válida"

    def analizar_expresion_ternaria(self, tokens, inicio=0):
        pos = inicio
        exito, pos, error = self.analizar_expresion_logica_or(tokens, pos)
        if not exito: return False, pos, error
        
        if pos < len(tokens) and tokens[pos]['tipo'] == 'QUESTION':
            pos += 1
            exito, pos, error = self.analizar_expresion(tokens, pos)
            if not exito: return False, pos, f"Error en parte verdadera del operador ternario: {error}"
            if pos >= len(tokens) or tokens[pos]['tipo'] != 'COLON':
                return False, pos, "Se esperaba ':' en operador ternario"
            pos += 1
            exito, pos, error = self.analizar_expresion_ternaria(tokens, pos)
            if not exito: return False, pos, f"Error en parte falsa del operador ternario: {error}"
        return True, pos, "Expresión condicional válida"

    def _analizar_expresion_binaria(self, tokens, inicio, metodo_inferior, operadores, nombre):
        pos = inicio
        exito, pos, error = metodo_inferior(tokens, pos)
        if not exito: return False, pos, error
        while pos < len(tokens) and tokens[pos]['tipo'] in operadores:
            pos += 1
            exito, pos, error = metodo_inferior(tokens, pos)
            if not exito: return False, pos, f"Error después del operador {nombre}: {error}"
        return True, pos, f"Expresión {nombre} válida"

    def analizar_expresion_logica_or(self, tokens, inicio=0):
        return self._analizar_expresion_binaria(tokens, inicio, self.analizar_expresion_logica_and, ['LOGICALOR'], 'lógica OR')

    def analizar_expresion_logica_and(self, tokens, inicio=0):
        return self._analizar_expresion_binaria(tokens, inicio, self.analizar_expresion_igualdad, ['LOGICALAND'], 'lógica AND')

    def analizar_expresion_igualdad(self, tokens, inicio=0):
        return self._analizar_expresion_binaria(tokens, inicio, self.analizar_expresion_relacional, ['EQUALITY','NOTEQUAL'], 'de igualdad')

    def analizar_expresion_relacional(self, tokens, inicio=0):
        return self._analizar_expresion_binaria(tokens, inicio, self.analizar_expresion_aditiva, 
                                              ['LESSTHAN','GREATERTHAN','LESSTHANOREQUAL','GREATERTHANOREQUAL'], 'relacional')

    def analizar_expresion_aditiva(self, tokens, inicio=0):
        return self._analizar_expresion_binaria(tokens, inicio, self.analizar_expresion_multiplicativa, ['PLUS','MINUS'], 'aditiva')

    def analizar_expresion_multiplicativa(self, tokens, inicio=0):
        return self._analizar_expresion_binaria(tokens, inicio, self.analizar_expresion_unaria, ['MULTIPLY','DIVIDE','MODULO'], 'multiplicativa')

    def analizar_expresion_unaria(self, tokens, inicio=0):
        pos = inicio
        if pos >= len(tokens): return False, pos, "Se esperaba expresión unaria"
        
        if tokens[pos]['tipo'] in ['INCREMENT','DECREMENT','PLUS','MINUS','NOT','BITWISE_NOT']:
            pos += 1
            return self.analizar_expresion_unaria(tokens, pos)
        return self.analizar_expresion_postfijo(tokens, pos)

    def analizar_expresion_postfijo(self, tokens, inicio=0):
        pos = inicio
        exito, pos, error = self.analizar_expresion_primaria(tokens, pos)
        if not exito: return False, pos, error
        
        while pos < len(tokens):
            if tokens[pos]['tipo'] == 'LBRACKET':
                pos += 1
                exito, pos, error = self.analizar_expresion(tokens, pos)
                if not exito: return False, pos, f"Error en índice del array: {error}"
                if pos >= len(tokens) or tokens[pos]['tipo'] != 'RBRACKET':
                    return False, pos, "Se esperaba ']'"
                pos += 1
            elif tokens[pos]['tipo'] == 'LPAREN':
                pos += 1
                if pos < len(tokens) and tokens[pos]['tipo'] != 'RPAREN':
                    exito, pos, error = self.analizar_lista_argumentos(tokens, pos)
                    if not exito: return False, pos, f"Error en argumentos: {error}"
                if pos >= len(tokens) or tokens[pos]['tipo'] != 'RPAREN':
                    return False, pos, "Se esperaba ')'"
                pos += 1
            elif tokens[pos]['tipo'] in ['DOT','ARROW']:
                pos += 1
                if pos >= len(tokens) or tokens[pos]['tipo'] != 'IDENTIFIER':
                    return False, pos, f"Se esperaba identificador después de '{tokens[pos-1]['valor']}'"
                pos += 1
            elif tokens[pos]['tipo'] in ['INCREMENT','DECREMENT']:
                pos += 1
            else: break
        return True, pos, "Expresión postfijo válida"

    def analizar_expresion_primaria(self, tokens, inicio=0):
        pos = inicio
        if pos >= len(tokens): return False, pos, "Se esperaba expresión primaria"
        
        if tokens[pos]['tipo'] == 'IDENTIFIER':
            return True, pos + 1, f"Identificador: {tokens[pos]['valor']}"
        elif tokens[pos]['tipo'] in ['NUMBER','FLOAT','CHAR','TRUE','FALSE','STRING']:
            return True, pos + 1, f"Literal: {tokens[pos]['valor']}"
        elif tokens[pos]['tipo'] == 'LPAREN':
            pos += 1
            exito, pos, error = self.analizar_expresion(tokens, pos)
            if not exito: return False, pos, f"Error en expresión entre paréntesis: {error}"
            if pos >= len(tokens) or tokens[pos]['tipo'] != 'RPAREN':
                return False, pos, "Se esperaba ')'"
            return True, pos + 1, "Expresión entre paréntesis válida"
        return False, pos, f"Token inesperado en expresión primaria: '{tokens[pos]['valor']}'"

    def analizar_lista_argumentos(self, tokens, inicio=0):
        return self._analizar_lista_expresiones(tokens, inicio, "argumento")

    def analizar_lista_valores(self, tokens, inicio=0):
        return self._analizar_lista_expresiones(tokens, inicio, "valor")

    def _analizar_lista_expresiones(self, tokens, inicio, tipo_elemento):
        pos = inicio
        exito, pos, error = self.analizar_expresion(tokens, pos)
        if not exito: return False, pos, f"Error en {tipo_elemento}: {error}"
        
        while pos < len(tokens) and tokens[pos]['tipo'] == 'COMMA':
            pos += 1
            exito, pos, error = self.analizar_expresion(tokens, pos)
            if not exito: return False, pos, f"Error en {tipo_elemento} después de ',': {error}"
        return True, pos, f"Lista de {tipo_elemento}s válida"

    def analizar_sentencia_switch(self, tokens, inicio=0):
        pos = inicio
        checks = [('SWITCH',"'switch'"),('LPAREN',"'(' después de 'switch'")]
        for check_type, error_msg in checks:
            if pos >= len(tokens) or tokens[pos]['tipo'] != check_type:
                return False, pos, f"Se esperaba {error_msg}"
            pos += 1
        
        exito, pos, error = self.analizar_expresion(tokens, pos)
        if not exito: return False, pos, f"Error en expresión del switch: {error}"
        
        final_checks = [('RPAREN',"')' después de la expresión"),('LBRACE',"'{' después de switch")]
        for check_type, error_msg in final_checks:
            if pos >= len(tokens) or tokens[pos]['tipo'] != check_type:
                return False, pos, f"Se esperaba {error_msg}"
            pos += 1
        
        while pos < len(tokens) and tokens[pos]['tipo'] != 'RBRACE':
            if tokens[pos]['tipo'] == 'CASE':
                exito, pos, error = self._analizar_caso_o_default(tokens, pos, True)
            elif tokens[pos]['tipo'] == 'DEFAULT':
                exito, pos, error = self._analizar_caso_o_default(tokens, pos, False)
            else: return False, pos, f"Se esperaba 'case' o 'default', se encontró '{tokens[pos]['valor']}'"
            if not exito: return False, pos, error
        
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'RBRACE':
            return False, pos, "Se esperaba '}' para cerrar switch"
        return True, pos + 1, "Sentencia switch válida"

    def _analizar_caso_o_default(self, tokens, inicio, es_case):
        pos = inicio
        palabra = 'case' if es_case else 'default'
        pos += 1
        
        if es_case:
            if pos >= len(tokens) or tokens[pos]['tipo'] not in ['NUMBER','FLOAT','CHAR','TRUE','FALSE']:
                return False, pos, f"Se esperaba constante después de '{palabra}'"
            pos += 1
        
        if pos >= len(tokens) or tokens[pos]['tipo'] != 'COLON':
            return False, pos, f"Se esperaba ':' después de {palabra}"
        pos += 1
        
        while pos < len(tokens) and tokens[pos]['tipo'] not in ['CASE','DEFAULT','RBRACE']:
            exito, pos, error = self.analizar_sentencia(tokens, pos)
            if not exito: return False, pos, f"Error en sentencia del {palabra}: {error}"
        return True, pos, f"{palabra.capitalize()} válido"


def analizarsintactico(texto):
    analizador = GramaticaCompleta()
    analizador.errores = []
    analizador.estructuras_reconocidas = []
    analizador.tokens_encontrados = []
    
    try:
        if not texto or not texto.strip():
            return {'success': False, 'mensaje': 'No se proporcionó código para analizar',
                   'errores': ['Texto vacío o solo espacios'], 'resultados_sintacticos': [],
                   'tokens_lexicos': [], 'total_estructuras': 0, 'total_errores': 1}
        
        tokens = analizador.tokenizar(texto.strip())
        analizador.tokens_encontrados = [t['valor'] for t in tokens]
        
        if not tokens:
            return {'success': False, 'mensaje': 'No se encontraron tokens válidos en el código',
                   'errores': ['No se encontraron tokens válidos'], 'resultados_sintacticos': [],
                   'tokens_lexicos': [], 'total_estructuras': 0, 'total_errores': 1}
        
        exito, final_pos, mensaje = analizador.analizar_programa(tokens, 0)
        
        if final_pos < len(tokens):
            tokens_restantes = [tokens[i]['valor'] for i in range(final_pos, min(final_pos + 5, len(tokens)))]
            analizador.errores.append(f"Tokens no procesados: {', '.join(tokens_restantes)}")
        
        total_errores = len(analizador.errores)
        total_estructuras = len(analizador.estructuras_reconocidas)
        
        if total_errores == 0 and total_estructuras > 0:
            mensaje_final = f"✅ Análisis sintáctico exitoso: {total_estructuras} estructura(s) válida(s)"
            success = True
        else:
            mensaje_final = f"❌ Análisis con errores: {total_errores} error(es), {total_estructuras} estructura(s) válida(s)"
            success = False
        
        return {'success': success, 'mensaje': mensaje_final, 'errores': analizador.errores,
               'resultados_sintacticos': analizador.estructuras_reconocidas,
               'tokens_lexicos': analizador.tokens_encontrados, 'total_estructuras': total_estructuras,
               'total_errores': total_errores}
        
    except Exception as e:
        return {'success': False, 'mensaje': f'Error interno en el análisis sintáctico: {str(e)}',
               'errores': [f"Error interno: {str(e)}"], 'resultados_sintacticos': [],
               'tokens_lexicos': [], 'total_estructuras': 0, 'total_errores': 1}

def analizar_sintactico(texto):
    return analizarsintactico(texto)