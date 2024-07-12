from flask import Flask, render_template, request, make_response

app = Flask(__name__)

# Função calc_kelly
def calc_kelly(prob_evento, odd_aposta):
    try:
        prob_evento = float(prob_evento)
        odd_aposta = float(odd_aposta)
        
        kelly_fraction = (prob_evento / 100 - (1 - prob_evento / 100) / (odd_aposta - 1))
        proporcao_investimento_ideal = kelly_fraction * 100
        
        valor_a_ser_investido = round((proporcao_investimento_ideal / 10) * 100 / 25) * 25
        
        return proporcao_investimento_ideal, valor_a_ser_investido
    except ValueError:
        return None, "Erro: Por favor, insira um número válido."
    except ZeroDivisionError:
        return None, "Erro: A odd não pode ser zero."

# Função calc_bilateral
def calc_bilateral(odd_analisada, odd_contraria, odd_aposta):
    try:
        odd_analisada = float(odd_analisada)
        odd_contraria = float(odd_contraria)
        odd_aposta = float(odd_aposta)
        
        prob_analisada = 1 / odd_analisada
        prob_contraria = 1 / odd_contraria
        payout = 1 / (prob_analisada + prob_contraria)
        
        kelly_fraction = (prob_analisada - (1 - prob_analisada) / (odd_aposta - 1))
        proporcao_investimento_ideal = kelly_fraction * 100
        
        valor_a_ser_investido = round((proporcao_investimento_ideal / 10) * 100 / 25) * 25
        
        return payout * 100, proporcao_investimento_ideal, valor_a_ser_investido
    except ValueError:
        return None, "Erro: Por favor, insira um número válido."
    except ZeroDivisionError:
        return None, "Erro: A odd não pode ser zero."

# Função calc_cashout
def calc_cashout(odd_entrada, valor_entrada, odd_contraria):
    try:
        odd_entrada = float(odd_entrada)
        valor_entrada = float(valor_entrada)
        odd_contraria = float(odd_contraria)

        # Freebet na aposta original
        freebet_original = valor_entrada / (odd_contraria - 1)
        lucro_freebet_original = (valor_entrada * odd_entrada) - valor_entrada - freebet_original

        # Win-Win
        valor_investido_win_win = (valor_entrada * odd_entrada) / odd_contraria
        lucro_win_win = (valor_entrada * odd_entrada - valor_entrada) - valor_investido_win_win

        # Freebet na aposta contrária
        freebet_contraria = (valor_entrada * odd_entrada) - valor_entrada
        lucro_freebet_contraria = (freebet_contraria * odd_contraria) - valor_entrada - freebet_contraria

        return round(freebet_original, 2), round(lucro_freebet_original, 2), round(valor_investido_win_win, 2), round(lucro_win_win, 2), round(freebet_contraria, 2), round(lucro_freebet_contraria, 2), None
    except ValueError:
        return None, None, None, None, None, None, "Erro: Por favor, insira um número válido."
    except ZeroDivisionError:
        return None, None, None, None, None, None, "Erro: A odd não pode ser zero."

# Rota para a calculadora unilateral
@app.route('/', methods=['GET', 'POST'])
def index():
    proporcao_investimento_ideal = None
    valor_a_ser_investido = None
    error_message = None
    odd_decimal = None
    odd_aposta = None
    
    if request.method == 'POST':
        odd_decimal = request.form['odd_decimal']
        odd_aposta = request.form['odd_aposta']
        
        prob_evento = (1 / float(odd_decimal)) * 100
        
        proporcao_investimento_ideal, valor_a_ser_investido = calc_kelly(prob_evento, odd_aposta)
        if proporcao_investimento_ideal is None:
            error_message = valor_a_ser_investido
            proporcao_investimento_ideal = None
            valor_a_ser_investido = None

    mode = request.cookies.get('mode', 'light')
    
    return render_template('index.html', 
                           proporcao=proporcao_investimento_ideal, 
                           valor=valor_a_ser_investido, 
                           error=error_message, 
                           odd_decimal=odd_decimal, 
                           odd_aposta=odd_aposta,
                           mode=mode)

# Rota para a calculadora bilateral
@app.route('/bilateral', methods=['GET', 'POST'])
def bilateral():
    payout = None
    proporcao_investimento_ideal = None
    valor_a_ser_investido = None
    error_message = None
    odd_analisada = None
    odd_contraria = None
    odd_aposta = None
    
    if request.method == 'POST':
        odd_analisada = request.form['odd_analisada']
        odd_contraria = request.form['odd_contraria']
        odd_aposta = request.form['odd_aposta']
        
        payout, proporcao_investimento_ideal, valor_a_ser_investido = calc_bilateral(odd_analisada, odd_contraria, odd_aposta)
        if payout is None:
            error_message = proporcao_investimento_ideal
            payout = None
            proporcao_investimento_ideal = None
            valor_a_ser_investido = None

    mode = request.cookies.get('mode', 'light')
    
    return render_template('bilateral.html', 
                           payout=payout, 
                           proporcao=proporcao_investimento_ideal, 
                           valor=valor_a_ser_investido, 
                           error=error_message, 
                           odd_analisada=odd_analisada, 
                           odd_contraria=odd_contraria, 
                           odd_aposta=odd_aposta,
                           mode=mode)

# Rota para a calculadora de cashout
@app.route('/cashout', methods=['GET', 'POST'])
def cashout():
    freebet_original = ''
    lucro_freebet_original = ''
    win_win = ''
    lucro_win_win = ''
    freebet_contraria = ''
    lucro_freebet_contraria = ''
    error_message = None
    aposta_entrada = ''
    aposta_adversaria = ''
    odd_entrada = ''
    valor_adversaria = ''
    odd_contraria = ''
    
    if request.method == 'POST':
        aposta_entrada = request.form['aposta_entrada']
        aposta_adversaria = request.form['aposta_adversaria']
        odd_entrada = request.form['odd_entrada']
        valor_adversaria = request.form['valor_adversaria']
        odd_contraria = request.form['odd_contraria']
        
        freebet_original, lucro_freebet_original, win_win, lucro_win_win, freebet_contraria, lucro_freebet_contraria, error_message = calc_cashout(odd_entrada, valor_adversaria, odd_contraria)

    mode = request.cookies.get('mode', 'light')
    
    return render_template('cashout.html', 
                           freebet_original=freebet_original, 
                           lucro_freebet_original=lucro_freebet_original,
                           win_win=win_win, 
                           lucro_win_win=lucro_win_win,
                           freebet_contraria=freebet_contraria, 
                           lucro_freebet_contraria=lucro_freebet_contraria,
                           error=error_message, 
                           aposta_entrada=aposta_entrada, 
                           aposta_adversaria=aposta_adversaria, 
                           odd_entrada=odd_entrada, 
                           valor_adversaria=valor_adversaria, 
                           odd_contraria=odd_contraria,
                           mode=mode)

@app.route('/toggle_mode', methods=['POST'])
def toggle_mode():
    mode = request.cookies.get('mode', 'light')
    new_mode = 'dark' if mode == 'light' else 'light'
    response = make_response()
    response.set_cookie('mode', new_mode)
    return response

if __name__ == '__main__':
    app.run(debug=True)
