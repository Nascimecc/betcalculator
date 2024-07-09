from flask import Flask, render_template, request

app = Flask(__name__)

def calc_kelly(prob_evento, odd_aposta):
    try:
        prob_evento = float(prob_evento)
        odd_aposta = float(odd_aposta)
        
        kelly_fraction = (prob_evento / 100 - (1 - prob_evento / 100) / (odd_aposta - 1))
        proporcao_investimento_ideal = kelly_fraction * 100
        valor_a_ser_investido = round(((proporcao_investimento_ideal / 8) * 100) / 25) * 25
        
        return proporcao_investimento_ideal, valor_a_ser_investido
    except ValueError:
        return None, "Erro: Por favor, insira um número válido."
    except ZeroDivisionError:
        return None, "Erro: A odd não pode ser zero."

def calc_bilateral(odd_analisada, odd_contraria, odd_aposta):
    try:
        odd_analisada = float(odd_analisada)
        odd_contraria = float(odd_contraria)
        odd_aposta = float(odd_aposta)
        
        prob_analisada = (1 / odd_analisada) * 100
        prob_contraria = (1 / odd_contraria) * 100
        hold = ((odd_analisada * odd_contraria) / (odd_analisada + odd_contraria)) * 100
        odd_justa = max(1, 100 / (prob_analisada + prob_contraria))
        
        kelly_fraction = (prob_analisada / 100 - (1 - prob_analisada / 100) / (odd_aposta - 1))
        proporcao_investimento_ideal = kelly_fraction * 100
        valor_a_ser_investido = round(((proporcao_investimento_ideal / 8) * 100) / 25) * 25
        
        payout = (prob_analisada + prob_contraria) / 100
        
        return payout, odd_justa, proporcao_investimento_ideal, valor_a_ser_investido
    except ValueError:
        return None, "Erro: Por favor, insira um número válido."
    except ZeroDivisionError:
        return None, "Erro: A odd não pode ser zero."

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

@app.route('/bilateral', methods=['GET', 'POST'])
def bilateral():
    hold = None
    odd_justa = None
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
        
        hold, odd_justa, proporcao_investimento_ideal, valor_a_ser_investido = calc_bilateral(odd_analisada, odd_contraria, odd_aposta)
        if hold is None:
            error_message = odd_justa
            hold = None
            odd_justa = None
            proporcao_investimento_ideal = None
            valor_a_ser_investido = None

    mode = request.cookies.get('mode', 'light')
    
    return render_template('bilateral.html', 
                           payout=hold, 
                           odd_justa=odd_justa, 
                           proporcao=proporcao_investimento_ideal, 
                           valor=valor_a_ser_investido, 
                           error=error_message, 
                           odd_analisada=odd_analisada, 
                           odd_contraria=odd_contraria, 
                           odd_aposta=odd_aposta,
                           mode=mode)

@app.route('/toggle_mode', methods=['POST'])
def toggle_mode():
    mode = request.cookies.get('mode', 'light')
    new_mode = 'dark' if mode == 'light' else 'light'
    response = app.make_response()
    response.set_cookie('mode', new_mode)
    return response

if __name__ == '__main__':
    app.run(debug=True)
