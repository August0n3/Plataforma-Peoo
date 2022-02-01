import requests

class Suap():
    def __init__(self):
        self.__endpoint = "https://suap.ifrn.edu.br/api/v2/"

    def autentica(self, username, password):
        ret = None

        url = self.__endpoint + "autenticacao/token/?format=json"

        headers = {'Content-type': 'application/json'}

        payload = '{"username": "%s", "password": "%s"}' % (username, password)

        result = requests.post(url, data=payload, headers=headers)
        
        if result.status_code == 200:
            
            data = result.json()
            
            if 'token' in data:
                user_data = self.__getMeusDados(data['token'])
                if user_data is not None:
                    ret = user_data

        return ret


    def __getMeusDados(self, token):
        ret = None

        url = self.__endpoint + "minhas-informacoes/meus-dados/"

        headers = {'Content-type': 'application/json',
                    'Authorization': 'JWT %s' % token}

        payload = '{"token": "%s"}' % token

        result = requests.get(url, data=payload, headers=headers)
        
        if result.status_code == 200:
            
            data = result.json()
            
            if data is not None:
                ret = data

        return ret