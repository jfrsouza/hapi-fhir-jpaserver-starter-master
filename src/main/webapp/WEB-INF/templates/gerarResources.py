import pandas as pd
from fhir.resources import patient, humanname, contactpoint, address

def format_birth_date(birth_date):
    # Formatar a data de nascimento para "ano mês dia"
    parts = birth_date.split('/')
    formatted_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
    return formatted_date


# Função para criar um recurso FHIR Patient a partir de uma linha do CSV
def create_patient_resource(row):
    # Criar um recurso Patient
    patient_resource = patient.Patient()

    # Definir o nome do paciente
    patient_name = humanname.HumanName()
    patient_name.text = row['Nome']
    patient_resource.name = [patient_name]

    # Definir o gênero do paciente
    patient_resource.gender = row['Gênero']

    # Definir a data de nascimento do paciente
    patient_birthdate = format_birth_date(row['Data de Nascimento'])
    patient_resource.birthDate = patient_birthdate

    # Definir o telefone do paciente
    patient_phone = contactpoint.ContactPoint()
    patient_phone.system = 'phone'
    patient_phone.value = row['Telefone']
    patient_resource.telecom = [patient_phone]

    # Definir o país de nascimento do paciente
    patient_address = address.Address()
    patient_address.country = row['País de Nascimento']
    patient_resource.address = [patient_address]

    # Adicionar observação, se presente
    if 'Observação' in row:
        patient_resource.text = row['Observação']

    return patient_resource

# Carregar o arquivo CSV usando o pandas
csv_file_path = 'data/patients.csv'
df = pd.read_csv(csv_file_path, delimiter=',')  # Altere o delimitador conforme necessário

# Iterar sobre as linhas do DataFrame e criar recursos FHIR Patient
fhir_patient_resources = []
for index, row in df.iterrows():
    patient_resource = create_patient_resource(row)
    fhir_patient_resources.append(patient_resource)

# Agora, 'fhir_patient_resources' contém uma lista de recursos FHIR Patient
# Você pode fazer o que quiser com essa lista, como salvar em um arquivo FHIR Bundle, enviar para um servidor FHIR, etc.
