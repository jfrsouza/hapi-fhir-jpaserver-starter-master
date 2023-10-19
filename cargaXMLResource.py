import csv
import requests
from datetime import datetime
from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.address import Address
from fhir.resources.bundle import Bundle, BundleEntry

# URL do servidor FHIR
fhir_server_url = "http://localhost:8080/fhir"

def importar_pacientes_do_csv(arquivo_csv):
    with open(arquivo_csv, 'r') as arquivo:
        leitor_csv = csv.DictReader(arquivo)

        for linha in leitor_csv:
            # Criar um recurso Patient
            paciente = Patient()

            # Adicionar nome
            nome = HumanName()
            nome.text = linha['Nome']
            paciente.name = [nome]

            # Adicionar identificador (CPF)
            identificador = Identifier()
            identificador.system = 'http://example.org/cpf'
            identificador.value = linha['CPF']
            paciente.identifier = [identificador]

            # Adicionar gênero
            paciente.gender = linha['Gênero']

            # Adicionar data de nascimento
            data_nascimento = datetime.strptime(linha['Data de Nascimento'], '%d/%m/%Y').date()
            paciente.birthDate = data_nascimento.strftime('%Y-%m-%d')

            # Adicionar telefone
            telefone = ContactPoint()
            telefone.system = 'phone'
            telefone.value = linha['Telefone']
            paciente.telecom = [telefone]

            # Adicionar país de nascimento
            endereco = Address()
            endereco.type = 'physical'
            endereco.use = 'home'
            endereco.city = 'Cidade'
            endereco.state = "Estado"
            endereco.country = linha['País de Nascimento']
            paciente.address = [endereco]

            # Adicionar observação
            #paciente.text = {'status': 'generated', 'div': linha['Observação']}

            # Criar um BundleEntry para o recurso Patient
            entry = BundleEntry()
            entry.resource = paciente
            entry.request = {'method': 'POST', 'url': 'Patient'}

            #print(entry)

            # Criar um Bundle e adicionar o BundleEntry
            bundle = Bundle(entry=[entry])

            # Converter o Bundle para XML
            bundle_xml = bundle.as_json()

            #print(bundle_xml)

            # Enviar o Bundle para o servidor FHIR
            url_paciente = f'{fhir_server_url}/'
            headers = {'Content-Type': 'application/xml'}
            response = requests.post(url_paciente, json=bundle_xml, headers=headers)

            if response.status_code == 201:
                print(f'Paciente {linha["Nome"]} importado com sucesso.')
            else:
                print(f'Erro ao importar paciente {linha["Nome"]}. Código de status: {response.status_code}')

# Nome do arquivo CSV
arquivo_csv = 'patients.csv'

# Chamar a função de importação
importar_pacientes_do_csv(arquivo_csv)
