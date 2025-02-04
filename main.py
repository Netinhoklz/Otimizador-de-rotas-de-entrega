from flask import Flask, render_template, request, redirect, url_for
import googlemaps
from itertools import permutations







app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        addresses = request.form.getlist('address')
        preco_str = request.form.getlist('preco_gasolina')
        return redirect(url_for('show_addresses', addresses=addresses,
                                preco_gasolina = preco_str))
    return render_template('index.html')



@app.route('/show_addresses')
def show_addresses():
    addresses = request.args.getlist('addresses')
    print(addresses)
    preco_str = request.args.getlist('preco_gasolina')
    print(preco_str)
    preco = float(preco_str[0].replace(',','.'))
    # Chave api conetando
    gmaps = googlemaps.Client(key="COLOQUE_AQUI_SUA_CHAVE_API_DO_GOOGLE")

    # Passando por todos os nomes
    lista_locais = addresses
    locais = {local: {} for local in lista_locais}
    for i in range(len(lista_locais)):
        for index in range(len(lista_locais)):
            if i == index or lista_locais[i]==''or lista_locais[index]=='':
                continue

            directions_result = gmaps.directions(origin=lista_locais[i], destination=lista_locais[index],
                                                 mode="driving")
            tempo=directions_result[0]['legs'][0]['duration']['value']

            locais[lista_locais[i]][lista_locais[index]] = (directions_result[0]['legs'][0]['distance']['value'],tempo)


    print(locais)

    # Função para calcular o comprimento de uma rota
    def comprimento_rota(rota):
        comprimento = 0
        tempo_total = 0
        for i in range(len(rota) - 1):
            cidade_atual = rota[i]
            proxima_cidade = rota[i + 1]
            comprimento += locais[cidade_atual][proxima_cidade][0]
            tempo_total += locais[cidade_atual][proxima_cidade][1] + 180
        # Adicionando a distância de volta para a cidade de origem
        comprimento += locais[rota[-1]][rota[0]][0]
        tempo_total += locais[rota[-1]][rota[0]][1] + 180

        return comprimento, tempo_total

    # Gerando todas as permutações das locais
    primeiro_valor = lista_locais[0]

    # Remova o valor escolhido dos valores originais
    valores_restantes = [valor for valor in lista_locais if valor != primeiro_valor]

    # Gere todas as permutações dos valores restantes
    permutacoes_restantes = permutations(valores_restantes)

    # Adicione o valor escolhido como primeiro valor em cada permutação
    permutacoes_com_primeiro_valor = [(primeiro_valor,) + permutacao for permutacao in permutacoes_restantes]

    # Inicializando a menor rota e seu comprimento
    menor_rota = None
    menor_comprimento = float('inf')

    # Encontrando a menor rota
    for rota in permutacoes_com_primeiro_valor:
        # print(rota)
        comprimento = comprimento_rota(rota)[0]
        tempo_rota = comprimento_rota(rota)[1]
        if comprimento < menor_comprimento:
            menor_comprimento = comprimento
            menor_rota = rota
            tempo_menor_rota = tempo_rota
    menor_comprimento = menor_comprimento/1000
    tempo_menor_rota = f'{round(tempo_menor_rota/60)} min'
    # Exibindo a menor rota e seu comprimento
    print("Menor rota:", menor_rota)
    print("Comprimento:", menor_comprimento)
    return render_template('show_addresses.html', addresses=menor_rota,
                           preco_gasolina = preco,
                           tempo_rota = tempo_menor_rota,
                           distancia = round(menor_comprimento,2),
                           l_carro = round(menor_comprimento/10,2),
                           c_carro = round((menor_comprimento/10)*preco,2),
                           l_moto =round(menor_comprimento / 17.745, 2),
                           c_moto =round((menor_comprimento / 17.745) * preco, 2),
                           )

if __name__ == '__main__':
    app.run(debug=True)
