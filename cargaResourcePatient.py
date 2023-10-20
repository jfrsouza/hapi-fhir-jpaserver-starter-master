import csv
#import profile
import requests
from fhir.resources.patient import Patient
from fhir.resources.identifier import Identifier
from fhir.resources.condition import Condition
from fhir.resources.humanname import HumanName
from datetime import datetime
from lxml import etree
import json

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

def converter_para_formato_correto(data_str):
    try:
        # Tenta converter a data para o formato 'YYYY-MM-DD'
        data_formatada = datetime.strptime(data_str, '%Y-%m-%d').strftime('%Y-%m-%d')
        return data_formatada
    except ValueError:
        # Se a conversão falhar, tenta formatar a data de outras maneiras
        for formato in ['%m/%d/%Y', '%d/%m/%Y']:
            try:
                data_formatada = datetime.strptime(data_str, formato).strftime('%Y-%m-%d')
                return data_formatada
            except ValueError:
                continue
        # Se todas as tentativas falharem, retorna None
        return None

def obj_para_dict(obj, _seen=None):
    # Converte um objeto para um dicionário, lidando com referências circulares
    if _seen is None:
        _seen = set()

    if id(obj) in _seen:
        return 'CIRCULAR_REFERENCE'

    _seen.add(id(obj))

    if hasattr(obj, '__dict__'):
        return {key: obj_para_dict(value, _seen) for key, value in obj.__dict__.items()}
    else:
        return obj

def criar_xml_recurso(recurso):
    recurso_dict = obj_para_dict(recurso)
    root = etree.Element(recurso.resource_type)
    for key, value in recurso_dict.items():
        if value == 'CIRCULAR_REFERENCE':
            continue
        element = etree.SubElement(root, key)
        
        if key == 'name':
            for sub_key, sub_value in value[0].__dict__.items():
                sub_element = etree.SubElement(element, sub_key)
                sub_element.text = str(sub_value) if sub_value is not None else ""
        elif key == 'meta':
            for sub_key, sub_value in value.items():
                sub_element = etree.SubElement(element, sub_key)
                sub_element.text = str(sub_value) if sub_value is not None else ""
        elif key == 'identifie':
            for sub_key, sub_value in value.items():
                sub_element = etree.SubElement(element, sub_key)
                sub_element.text = str(sub_value) if sub_value is not None else ""
        elif isinstance(value, list):
            for sub_value in value:
                sub_element = etree.SubElement(element, key[:-1])
                sub_element.text = str(sub_value) if sub_value is not None else ""
        else:
            element.text = str(value) if value is not None else ""
    
    return etree.tostring(root, pretty_print=True, encoding='unicode')

def carregar_dados_fhir(url_fhir_server, caminho_arquivo_csv):
    ids_pacientes = []

    with open(caminho_arquivo_csv, 'r') as arquivo_csv:
        leitor_csv = csv.DictReader(arquivo_csv)
        for linha in leitor_csv:

            nome_humano = HumanName()
            nome_humano.text = linha['Nome']
            nome_humano.given = [linha['Nome']]
            nome_humano.family = linha['Nome']
            nome_humano.use = "official"

            identifier = Identifier()
            identifier.value = linha['CPF']
            identifier.use = "official"


            paciente = Patient()
            
            # Adicionar informações ao campo meta
            #paciente.meta = {
            #    'versionId': linha['VersionId'] if 'VersionId' in linha else None,
             #   'lastUpdated': linha['LastUpdated'] if 'LastUpdated' in linha else None,
              #  'profile': 'https://simplifier.net/redenacionaldedadosemsaude/brindividuo',
               # 'tag': [{'system': linha['TagSystem'], 'code': linha['TagCode']}] if 'TagSystem' in linha and 'TagCode' in linha else None,
            #}
            paciente.active = True
            paciente.name = [nome_humano] #[{'text': linha['Nome']}]
            paciente.identifier = [identifier] #[{'value': linha['CPF']}]
            paciente.gender = linha['Gênero']

            # Tenta converter ou formatar a data para o formato correto
            data_nascimento = converter_para_formato_correto(linha['Data de Nascimento'])
            if data_nascimento:
                paciente.birthDate = data_nascimento
            else:
                print(f'Aviso: Data de Nascimento não reconhecida para o paciente {linha["Nome"]}. Ignorando este paciente.')
                continue

            # Enviar o recurso Patient para o servidor FHIR
            #print(paciente) 
            paciente_xml = criar_xml_recurso(paciente)
            #print(paciente_xml)
            resposta_paciente = requests.post(f'{url_fhir_server}/Patient', data=paciente_xml, headers={'Content-Type': 'application/xml'})
            #print(resposta_paciente.text)
            if resposta_paciente.status_code == 201:
                resposta_paciente_xml = resposta_paciente.content
                id_paciente = etree.fromstring(resposta_paciente_xml).find('.//id')
                #print(etree.fromstring(resposta_paciente_xml).find('..//id'))
                
                if id_paciente is not None and id_paciente.text:
                    ids_pacientes.append(id_paciente.text)

                    condicao = Condition()
                    condicao.subject = {'reference': f'Patient/{id_paciente.text}'}
                    condicao.text = {'status': 'generated', 'div': linha['Observação']}

                    # Enviar o recurso Condition para o servidor FHIR
                    condicao_xml = criar_xml_recurso(condicao)
                    requests.post(
                        f'{url_fhir_server}/Condition',
                        data=condicao_xml,
                        headers={'Content-Type': 'application/xml'},
                    )
                else:
                    print(f'Aviso: ID do paciente não encontrado na resposta. Ignorando este paciente.')
                
    return ids_pacientes

url_fhir_server = 'http://localhost:8080/fhir'
caminho_arquivo_csv = 'patients.csv'

ids_pacientes_criados = carregar_dados_fhir(url_fhir_server, caminho_arquivo_csv)

print(f'IDs dos pacientes criados: {ids_pacientes_criados}')
