import csv
import requests
from fhir.resources.patient import Patient
from fhir.resources.identifier import Identifier
from fhir.resources.humanname import HumanName
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.extension import Extension
from fhir.resources.coding import Coding
from fhir.resources.observation import Observation
#from fhir.resources.date

def format_birth_date(birth_date):
    # Formatar a data de nascimento para "ano mês dia"
    parts = birth_date.split('/')
    formatted_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
    return formatted_date


# Função para converter dados CSV em recursos FHIR
def convert_csv_to_fhir(csv_file):
    fhir_resources = []
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Criar um recurso Patient para cada linha no CSV
            patient = Patient()

            # Configurar atributos do paciente a partir das colunas CSV
            patient.identifier = [Identifier(value=row['CPF'])]
            patient.name = [HumanName(text=row['Nome'])]
            patient.birthDate = format_birth_date(row['Data de Nascimento'])
            patient.gender = row['Gênero']
            patient.telecom = [ContactPoint(system="phone", value=row['Telefone'])]

            # Adicionar extensão para detalhes adicionais
            #patient_extension = Extension()
            #patient_extension.url = "http://example.com/fhir/extensions#additionalDetails"
            #patient_extension.extension = [
            #    {"url": "countryOfBirth", "valueString": row['País de Nascimento']}#,
                #{"url": "observationNote", "valueString": row['Observação']}
            #]
            #patient.extension = [patient_extension]

            # Adicionar perfil ao paciente
            patient.meta = {"profile": ["https://simplifier.net/RedeNacionaldeDadosemSaude/BRIndividuo/~json"]}

            # Criar um recurso Observation para cada paciente
            #observation = Observation()
            #observation.meta = {"profile": ["https://simplifier.net/RedeNacionaldeDadosemSaude/BRIndividuo/~json"]}
            #observation.status = "final"
            #observation.code = Coding(system="http://loinc.org", code="8302-2", display="Pregnancy status")
            #observation.subject = {"reference": f"Patient/{patient.identifier[0].value}"}
            #observation.valueString = row['Observação']
            #observation.effectiveDateTime = FHIRDate(row['Data de Nascimento'])  # Usando a data de nascimento como a data da observação

            #fhir_resources.extend([patient, observation])

    return fhir_resources

# Função para enviar recursos FHIR para o servidor
def upload_to_fhir_server(fhir_resources, server_url):
    for resource in fhir_resources:
        response = requests.post(f"{server_url}/{resource.resource_type}", json=resource.as_json())
        if response.status_code == 201:
            print(f"{resource.resource_type} with ID {resource.identifier[0].value} uploaded successfully.")
        else:
            print(f"Failed to upload {resource.resource_type} with ID {resource.identifier[0].value}. Status code: {response.status_code}")

if __name__ == "__main__":
    # Substituir pelo caminho do seu arquivo CSV
    csv_file_path = 'data/patients.csv'

    # Substituir pela URL do seu servidor FHIR
    fhir_server_url = 'http://localhost:8080/fhir/Patient'

    # Converter CSV em recursos FHIR
    fhir_resources = convert_csv_to_fhir(csv_file_path)

    # Enviar recursos FHIR para o servidor
    upload_to_fhir_server(fhir_resources, fhir_server_url)
