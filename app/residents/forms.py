from django import forms
from core.services.validators import validate_cpf, validate_cnpj, validate_email, validate_phone, validate_url, validate_date, validate_upload_files_docs
from core.services.hydra_cpf_service import consult_cpf

from domains.residents.models import CondominiumUnit, RealEstateAgency, Vehicle, Visitor, Resident
from domains.parameters.models import ResidentType

class CondominiumUnitFormAdmin(forms.ModelForm):
    
    class Meta:
        model = CondominiumUnit
        fields = '__all__'
        widgets = {
            'tower': forms.TextInput(attrs={'class': 'mask-tower'}),
            'unit_number': forms.TextInput(attrs={'class': 'mask-unit-number'}),
            'identification': forms.TextInput(attrs={'class': 'mask-identification'}),
            'area_total': forms.NumberInput(attrs={'class': 'mask-area-total'}),
            'sale_price': forms.NumberInput(attrs={'class': 'mask-sale-price'}),
            'rent_price': forms.NumberInput(attrs={'class': 'mask-rent-price'}),
        }
        
        labels = {
            'condominium': 'Condomínio',
            'tower': 'Torre',
            'unit_number': 'Número da Unidade',
            'floor': 'Andar',
            'identification': 'Identificação',
            'unit_type': 'Tipo de Unidade',
            'bedrooms': 'Quartos',
            'bathrooms': 'Banheiros',
            'suites': 'Suítes',
            'garage_spaces': 'Vagas de Garagem',
            'area_total': 'Área Total',
            'status': 'Status',
            'for_sale': 'À Venda',
            'for_rent': 'Para Alugar',
            'sale_price': 'Preço de Venda',
            'rent_price': 'Preço de Aluguel',
            'notes': 'Observações',
        }
        
        help_texts = {
            'condominium': 'Selecione o condomínio ao qual a unidade pertence',
            'tower': 'Digite o bloco ou torre da unidade',
            'unit_number': 'Digite o número da unidade',
            'floor': 'Digite o andar da unidade',
            'identification': 'Digite a identificação da unidade (ex: número do apartamento, letra, etc.)',
            'unit_type': 'Selecione o tipo de unidade',
            'bedrooms': 'Digite o número de quartos',
            'bathrooms': 'Digite o número de banheiros',
            'suites': 'Digite o número de suítes',
            'garage_spaces': 'Digite a quantidade de vagas de garagem',
            'area_total': 'Digite a área total da unidade',
            'status': 'Selecione o status da unidade',
            'for_sale': 'Indique se a unidade está à venda',
            'for_rent': 'Indique se a unidade está para alugar',
            'sale_price': 'Digite o preço de venda da unidade (se aplicável)',
            'rent_price': 'Digite o preço de aluguel da unidade (se aplicável)',
            'notes': 'Digite as observações da unidade',
        }
        
        error_messages = {
            'condominium': {
                'required': 'O condomínio é obrigatório.',
                'invalid_choice': 'Selecione um condomínio válido.',
            },
            'tower': {
                'required': 'O bloco ou torre é obrigatório.',
            },
            'unit_number': {
                'required': 'O número da unidade é obrigatório.',
            },
            'floor': {
                'required': 'O andar é obrigatório.',
            },
            'identification': {
                'required': 'A identificação é obrigatória.',
            },
            'unit_type': {
                'required': 'O tipo de unidade é obrigatório.',
                'invalid_choice': 'Selecione um tipo de unidade válido.',
            },
            'bedrooms': {
                'invalid': 'Digite um número válido de quartos.',
            },
            'bathrooms': {
                'invalid': 'Digite um número válido de banheiros.',
            },
            'suites': {
                'invalid': 'Digite um número válido de suítes.',
            },
            'garage_spaces': {
                'required': 'O número de vagas de garagem é obrigatório.',
                'invalid_choice': 'Selecione um número válido de vagas de garagem.',
            },
             'area_total': {
                'invalid': 'Digite uma área total válida.',
            },
            'status': {
                'required': 'O status é obrigatório.',
                'invalid_choice': 'Selecione um status valido.',
            },
            'for_sale': {
                'required': 'O status é obrigatório.',
                'invalid_choice': 'Selecione um status valido.',
            },
            'for_rent': {
                'required': 'O status é obrigatório.',
                'invalid_choice': 'Selecione um status valido.',
            },
            'sale_price': {
                'invalid': 'Digite um preço de venda válido.',
            },
            'rent_price': {
                'invalid': 'Digite um preço de aluguel válido.',
            },
            'notes': {
                'required': 'As observações da unidade é obrigatória.',
            },
            'created_at': {
                'required': 'A data de criação da unidade é obrigatória.',
            },
            'updated_at': {
                'required': 'A data de atualização da unidade é obrigatória.',
            },
        }
        
        exclude = [
            'created_at',
            'updated_at',
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['identification'].widget.attrs['class'] = 'mask-identification'
        self.fields['area_total'].widget.attrs['class'] = 'mask-area-total'
        self.fields['sale_price'].widget.attrs['class'] = 'mask-sale-price'
        self.fields['rent_price'].widget.attrs['class'] = 'mask-rent-price'
    

class ResidentFormAdmin(forms.ModelForm):
    
    class Meta:
        model = Resident
        fields = '__all__'
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'mask-email'}),
            'phone': forms.TextInput(attrs={'class': 'mask-phone'}),
            'cpf': forms.TextInput(attrs={'class': 'mask-cpf'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'unit': 'Condominio/Unidade',
            'type_of_resident': 'Tipo de Residente',
            'name': 'Nome Completo',
            'email': 'E-mail',
            'phone': 'Número de Telefone',
            'cpf': 'CPF',
            'rg': 'RG',
            'sex': 'Sexo',
            'date_of_birth': 'Data de Nascimento',
            'profission': 'Profissão',
            'photo': 'Foto',
            'is_primary': 'Principal',
            'is_resident': 'Residente',
            'is_active': 'Ativo',
            'created_at': 'Criado em',
            'updated_at': 'Atualizado em',
            'certificate_presentation_date': 'Data de Apresentação da Certidão',
            'certificate_validity': 'Validade da Certidão',
            'observations_certificate': 'Observações da Certidão',
            'certificate_file': 'Arquivo da Certidão',
        }
        
        help_texts = {
            'unit': 'Selecione a unidade à qual o(a) morador(a) pertence',
            'type_of_resident': 'Selecione o tipo de morador(a)',
            'name': 'Digite o nome completo do(a) morador(a)',
            'email': 'Digite o e-mail do(a) morador(a)',
            'phoner': 'Digite o número de telefone do(a) morador(a)',
            'cpf': 'Digite o CPF do(a) morador(a)',
            'rg': 'Digite o RG do(a) morador(a)',
            'sex': 'Selecione o sexo do(a) morador(a)',
            'date_of_birth': 'Digite a data de nascimento do(a) morador(a)',
            'profission': 'Digite a profissão do(a) morador(a)',
            'is_primary': 'Indique se o(a) morador(a) é o principal da unidade',
            'is_resident': 'Indique se o(a) morador(a) é um morador da unidade',
            'is_active': 'Indique se o(a) morador(a) está ativo',
            'photo': 'Selecione uma foto do(a) morador(a)',
            'created_at': 'Data de criação do(a) morador(a)',
            'updated_at': 'Data de atualização do(a) morador(a)',
            'certificate_presentation_date': 'Digite a data de apresentação da certidão',
            'certificate_validity': 'Digite a data de validade da certidão',
            'observations_certificate': 'Digite as observações da certidão',
            'certificate_file': 'Selecione o arquivo da certidão',
        }
        
        error_messages = {
            'unit': {
                'required': 'A unidade é obrigatória.',
                'invalid_choice': 'Selecione uma unidade válida.',
            },
            'type_of_resident': {
                'required': 'O tipo de morador(a) é obrigatório.',
                'invalid_choice': 'Selecione um tipo de morador(a) válido.',
            },
            'name': {
                'required': 'O nome completo é obrigatório.',
            },
            'email': {
                'required': 'O e-mail é obrigatório.',
                'invalid': 'Digite um e-mail válido.',
            },
            'phone': {
                'required': 'O número de telefone é obrigatório.',
                'invalid': 'Digite um número de telefone válido.',
            },
            'cpf': {
                'required': 'O CPF é obrigatório.',
                'invalid': 'Digite um CPF valido.',
            },
            'rg': {
                'required': 'O RG é obrigatório.',
                'invalid': 'Digite um RG valido.',
            },
            'sex': {
                'required': 'O sexo é obrigatório.',
                'invalid_choice': 'Selecione um sexo valido.',
            },
            'date_of_birth': {
                'required': 'A data de nascimento é obrigatória.',
                'invalid': 'Digite uma data de nascimento valida.',
            },
            'profission': {
                'required': 'A profissão é obrigatória.',
            },
            'is_primary': {
                'required': 'O principal é obrigatório.',
            },
            'is_resident': {
                'required': 'O residente é obrigatório.',
            },
            'is_active': {
                'required': 'O ativo é obrigatório.',
            },
            'photo': {
                'required': 'A foto é obrigatória.',
            },
            'created_at': {
                'required': 'A data de criação é obrigatória.',
            },
            'updated_at': {
                'required': 'A data de atualização é obrigatória.',
            },
        }
        
        exclude = [
            'created_at',
            'updated_at',
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'type_of_resident' in self.fields:
            self.fields['type_of_resident'].queryset = ResidentType.objects.filter(is_active=True).order_by('description')
        self.fields['email'].widget.attrs['class'] = 'mask-email'
        self.fields['phone'].widget.attrs['class'] = 'mask-phone'
        self.fields['cpf'].widget.attrs['class'] = 'mask-cpf'
        self.fields['date_of_birth'].widget.attrs['class'] = 'mask-date-of-birth'
        if 'certificate_file' in self.fields:
            self.fields['certificate_file'].validators.append(validate_upload_files_docs)

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf:
            if not validate_cpf(cpf):
                raise forms.ValidationError('O CPF informado é inválido.')
            
            # Consultar Receita Federal via HydraCPF se o CPF mudou ou se a situação está vazia
            cpf_digits = "".join(filter(str.isdigit, cpf))
            import logging
            logger = logging.getLogger(__name__)
            
            logger.info(f"Validating CPF for {self.instance}: digits={cpf_digits}")
            
            if not self.instance.pk or self.instance.cpf != cpf or not self.instance.situation:
                logger.info(f"Triggering API consultation for CPF {cpf_digits}")
                result = consult_cpf(cpf_digits)
                logger.info(f"API result for {cpf_digits}: {result}")
                
                if result is not None:
                    if 'error' not in result:
                        self.instance.situation = result.get('situation')
                        self.instance.regular = result.get('regular')
                        self.instance.death = result.get('death')
                        logger.info(f"Updating instance: situation={self.instance.situation}, regular={self.instance.regular}, death={self.instance.death}")
                    else:
                        self.instance.situation = "Erro na Consulta"
                        logger.info("API returned error, setting situation to 'Erro na Consulta'")
                else:
                    logger.info("API result is None")
        return cpf



    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not validate_email(email):
            raise forms.ValidationError('O e-mail informado é inválido.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not validate_phone(phone):
            raise forms.ValidationError('O telefone informado é inválido.')
        return phone

    def clean_rg(self):
        rg = self.cleaned_data.get('rg')
        if not rg:
            raise forms.ValidationError('O RG é obrigatório.')
        return rg

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            if not (1930 <= dob.year <= 2050):
                raise forms.ValidationError('A data de nascimento deve estar entre os anos 1930 e 2050.')
        return dob

    def clean_certificate_presentation_date(self):
        date_val = self.cleaned_data.get('certificate_presentation_date')
        if date_val and not validate_date(date_val):
            raise forms.ValidationError('Data de apresentação inválida.')
        return date_val

    def clean_certificate_validity(self):
        date_val = self.cleaned_data.get('certificate_validity')
        if date_val and not validate_date(date_val):
            raise forms.ValidationError('Data de validade inválida.')
        return date_val


class VehicleFormAdmin(forms.ModelForm):
    
    class Meta:
        model = Vehicle
        fields = '__all__'
        widgets = {
            'condo_unit': forms.Select(attrs={'class': 'mask-condo-unit'}),
            'license_plate': forms.TextInput(attrs={'class': 'mask-license-plate'}),
            'year': forms.NumberInput(attrs={'class': 'mask-year'}),
            'garage_space': forms.TextInput(attrs={'class': 'mask-garage-space'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'condo_unit': 'Condominio/Unidade',
            'vehicle_type': 'Tipo de Veículo',
            'license_plate': 'Placa do Veículo',
            'brand': 'Marca do Veículo',
            'model': 'Modelo do Veículo',
            'color': 'Cor do Veículo',
            'year': 'Ano do Veículo',
            'garage_space': 'Vaga de Garagem',
            'photo': 'Foto',
            'is_active': 'Ativo',
            'created_at': 'Criado em',
            'updated_at': 'Atualizado em',
        }
        
        help_texts = {
            'condo_unit': 'Selecione a unidade',
            'vehicle_type': 'Selecione o tipo de veículo',
            'license_plate': 'Digite a placa do veículo',
            'brand': 'Digite a marca do veículo',
            'model': 'Digite o modelo do veículo',
            'color': 'Digite a cor do veículo',
            'year': 'Digite o ano do veículo',
            'garage_space': 'Selecione a vaga de garagem associada ao veículo',
            'is_active': 'Indique se o veículo está ativo',
            'created_at': 'Data de criação do veículo',
            'updated_at': 'Data de atualização do veículo',
        }
        
        error_messages = {
            'condo_unit': {
                'required': 'A unidade é obrigatória.',
                'invalid_choice': 'Selecione uma unidade válida.',
            },
            'vehicle_type': {
                'required': 'O tipo de veículo é obrigatório.',
                'invalid_choice': 'Selecione um tipo de veículo válido.',
            },
            'license_plate': {
                'required': 'A placa do veículo é obrigatória.',
            },
            'brand': {
                'required': 'A marca do veículo é obrigatória.',
            },
            'model': {
                'required': 'O modelo do veículo é obrigatório.',
            },
            'color': {
                'required': 'A cor do veículo é obrigatória.',
            },
            'year': {
                'required': 'O ano do veículo é obrigatório.',
                'invalid': 'Digite um ano válido para o veículo.',
            },
            'garage_space': {
                'required': 'A vaga de garagem é obrigatória.',
                'invalid_choice': 'Selecione uma vaga de garagem válida.',
            },
            'is_active': {
                'required': 'O status de ativo é obrigatório.',
            },
            'created_at': {
                'required': 'A data de criação é obrigatória.',
            },
             'updated_at': {
                'required': 'A data de atualização é obrigatória.',
            },
        }
        
        exclude = [
            'created_at',
            'updated_at',
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['condo_unit'].widget.attrs['class'] = 'mask-condo-unit'
        self.fields['license_plate'].widget.attrs['class'] = 'mask-license-plate'
        self.fields['year'].widget.attrs['class'] = 'mask-year'


class VisitorFormAdmin(forms.ModelForm):
    
    class Meta:
        model = Visitor
        fields = '__all__'
        widgets = {
            'condo_unit': forms.Select(attrs={'class': 'mask-condo-unit'}),
            'cpf': forms.TextInput(attrs={'class': 'mask-cpf'}),
            'phone': forms.TextInput(attrs={'class': 'mask-phone'}),
        }
        
        labels = {
            'condo_unit': 'Condominio/Unidade',
            'name': 'Nome',
            'cpf': 'CPF',
            'rg': 'RG',
            'phone': 'Telefone',
            'purpose': 'Proposto da visita',
            'is_active': 'Ativo',
            'created_at': 'Criado em',
            'updated_at': 'Atualizado em',
            'certificate_presentation_date': 'Data de Apresentação da Certidão',
            'certificate_validity': 'Validade da Certidão',
            'observations_certificate': 'Observações da Certidão',
            'certificate_file': 'Arquivo da Certidão',
            'types_visitor_restriction': 'Tipos de Restrição',
            'restrictionVisitor_presentation_date': 'Data de apresentação',
            'restrictionVisitor_validity_date': 'Data de validade',
            'restrictionVisitor_observations': 'Observações',
            'restrictionVisitor_file': 'Arquivo',
        }
        
        help_texts = {
            'condo_unit': 'Selecione a unidade que o visitante irá visitar',
            'name': 'Digite o nome do visitante',
            'cpf': 'Digite o CPF do visitante',
            'rg': 'Digite o RG do visitante',
            'phone': 'Digite o telefone do visitante',
            'purpose': 'Digite o propósito da visita',
            'is_active': 'Indique se o visitante está ativo',
            'created_at': 'Data de criação do visitante',
            'updated_at': 'Data de atualização do visitante',
            'certificate_presentation_date': 'Digite a data de apresentação da certidão',
            'certificate_validity': 'Digite a data de validade da certidão',
            'observations_certificate': 'Digite as observações da certidão',
            'certificate_file': 'Selecione o arquivo da certidão',
            'types_visitor_restriction': 'Selecione o tipo de restrição',
            'restrictionVisitor_presentation_date': 'Digite a data de apresentação',
            'restrictionVisitor_validity_date': 'Digite a data de validade',
            'restrictionVisitor_observations': 'Digite as observações da restrição',
            'restrictionVisitor_file': 'Selecione o arquivo da restrição',
        }
        
        error_messages = {
            'condo_unit': {
                'required': 'A unidade é obrigatória.',
                'invalid_choice': 'Selecione uma unidade válida.',
            },
            'name': {
                'required': 'O nome é obrigatório.',
            },
            'cpf': {
                'required': 'O CPF é obrigatório.',
            },
            'rg': {
                'required': 'O RG é obrigatório.',
            },
            'phone': {
                'required': 'O telefone é obrigatório.',
            },
            'purpose': {
                'required': 'O propósito da visita é obrigatório.',
            },
            'is_active': {
                'required': 'O status de ativo é obrigatório.',
            },
            'created_at': {
                'required': 'A data de criação é obrigatória.',
            },
             'updated_at': {
                'required': 'A data de atualização é obrigatória.',
            }
        }
        
        exclude = [
            'created_at',
            'updated_at',
        ]
         
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['condo_unit'].widget.attrs['class'] = 'mask-condo-unit'
        self.fields['cpf'].widget.attrs['class'] = 'mask-cpf'
        self.fields['phone'].widget.attrs['class'] = 'mask-phone'
        if 'certificate_file' in self.fields:
            self.fields['certificate_file'].validators.append(validate_upload_files_docs)
        if 'restrictionVisitor_file' in self.fields:
            self.fields['restrictionVisitor_file'].validators.append(validate_upload_files_docs)

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if not cpf:
            raise forms.ValidationError('O CPF é obrigatório.')
        if not validate_cpf(cpf):
            raise forms.ValidationError('O CPF informado é inválido.')
        
        # Consultar Receita Federal via HydraCPF se o CPF mudou ou se a situação está vazia
        cpf_digits = "".join(filter(str.isdigit, cpf))
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Validating CPF for {self.instance}: digits={cpf_digits}")
        
        if not self.instance.pk or (hasattr(self.instance, 'cpf') and self.instance.cpf != cpf) or not self.instance.situation:
            logger.info(f"Triggering API consultation for CPF {cpf_digits}")
            result = consult_cpf(cpf_digits)
            logger.info(f"API result for {cpf_digits}: {result}")
            
            if result is not None:
                if 'error' not in result:
                    self.instance.situation = result.get('situation')
                    self.instance.regular = result.get('regular')
                    self.instance.death = result.get('death')
                    logger.info(f"Updating instance: situation={self.instance.situation}, regular={self.instance.regular}, death={self.instance.death}")
                else:
                    self.instance.situation = "Erro na Consulta"
                    logger.info("API returned error, setting situation to 'Erro na Consulta'")
            else:
                logger.info("API result is None")
        return cpf


    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError('O telefone é obrigatório.')
        if not validate_phone(phone):
            raise forms.ValidationError('O telefone informado é inválido.')
        return phone

    def clean_rg(self):
        rg = self.cleaned_data.get('rg')
        if not rg:
            raise forms.ValidationError('O RG é obrigatório.')
        return rg

    def clean_restrictionVisitor_presentation_date(self):
        date_val = self.cleaned_data.get('restrictionVisitor_presentation_date')
        if date_val and not validate_date(date_val):
            raise forms.ValidationError('Data de apresentação inválida.')
        return date_val

    def clean_restrictionVisitor_validity_date(self):
        validity_date = self.cleaned_data.get('restrictionVisitor_validity_date')
        presentation_date = self.cleaned_data.get('restrictionVisitor_presentation_date')
        
        if validity_date:
            if not validate_date(validity_date):
                raise forms.ValidationError('Data de validade inválida.')
            
            if presentation_date and validity_date < presentation_date:
                raise forms.ValidationError('A data de validade não pode ser anterior à data de apresentação.')
        
        return validity_date

    def clean_certificate_presentation_date(self):
        date_val = self.cleaned_data.get('certificate_presentation_date')
        if date_val and not validate_date(date_val):
            raise forms.ValidationError('Data de apresentação inválida.')
        return date_val

    def clean_certificate_validity(self):
        date_val = self.cleaned_data.get('certificate_validity')
        if date_val and not validate_date(date_val):
            raise forms.ValidationError('Data de validade inválida.')
        return date_val




class RealEstateAgencyFormAdmin(forms.ModelForm):
    
    class Meta:
        model = RealEstateAgency
        fields = '__all__'
        widgets = {
            'condo_unit': forms.Select(attrs={'class': 'mask-condo-unit'}),
            'cnpj': forms.TextInput(attrs={'class': 'mask-cnpj'}),
            'phone': forms.TextInput(attrs={'class': 'mask-phone'}),
            'email': forms.EmailInput(attrs={'class': 'mask-email'}),            
            'website': forms.URLInput(attrs={'class': 'mask-website'}),
            'trade_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'condo_unit': 'Condominio/Unidade',
            'name': 'Nome da Imobiliária',
            'trade_name': 'Nome Fantasia',
            'cnpj': 'CNPJ',
            'phone': 'Telefone',
            'email': 'E-mail',
            'website': 'Site',
            'address': 'Endereço',
            'contact_person': 'Pessoa de Contato',
            'is_active': 'Ativo',
            'created_at': 'Criado em',
            'updated_at': 'Atualizado em',
        }
        
        help_texts = {
            'condo_unit': 'Selecione a unidade associada à imobiliária',
            'name': 'Digite o nome da imobiliária',
            'trade_name': 'Digite o nome fantasia da imobiliária (opcional)',
            'cnpj': 'Digite o CNPJ da imobiliária',
            'phone': 'Digite o telefone da imobiliária',
            'email': 'Digite o e-mail da imobiliária',
            'website': 'Digite o site da imobiliária',
            'address': 'Digite o endereço da imobiliária',
            'contact_person': 'Digite o nome da pessoa de contato na imobiliária',
            'is_active': 'Indique se a imobiliária está ativa',
            'created_at': 'Data de criação da imobiliária',
            'updated_at': 'Data de atualização da imobiliária',
        }
        
        error_messages = {
            'condo_unit': {
                'required': 'A unidade é obrigatória.',
                'invalid_choice': 'Selecione uma unidade válida.',
            },
            'name': {
                'required': 'O nome da imobiliária é obrigatório.',
            },
            'cnpj': {
                'required': 'O CNPJ é obrigatório.',
                'invalid': 'Digite um CNPJ válido.',
            },
            'phone': {
                'required': 'O telefone é obrigatório.',
                'invalid': 'Digite um telefone válido.',
            },
            'email': {
                'required': 'O e-mail é obrigatório.',
                'invalid': 'Digite um e-mail válido.',
            },
            'website': {
                'required': 'O site é obrigatório.',
                'invalid': 'Digite um site válido.',
            },
            'address': {
                'required': 'O endereço é obrigatório.',
            },
            'contact_person': {
                'required': 'A pessoa de contato é obrigatória.',
            },
             'is_active': {
                'required': 'O status de ativo é obrigatório.',
            },
             'created_at': {
                'required': 'A data de criação é obrigatória.',
            },
             'updated_at': {
                'required': 'A data de atualização é obrigatória.',
            },
        }
        
        exclude = [
            'created_at',
            'updated_at',
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['condo_unit'].widget.attrs['class'] = 'mask-condo-unit'
        self.fields['cnpj'].widget.attrs['class'] = 'mask-cnpj'
        self.fields['phone'].widget.attrs['class'] = 'mask-phone'
        self.fields['email'].widget.attrs['class'] = 'mask-email'
        self.fields['website'].widget.attrs['class'] = 'mask-website'

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if not cnpj:
            raise forms.ValidationError('O CNPJ é obrigatório.')
        if not validate_cnpj(cnpj):
            raise forms.ValidationError('O CNPJ informado é inválido.')
        return cnpj

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('O e-mail é obrigatório.')
        if not validate_email(email):
            raise forms.ValidationError('O e-mail informado é inválido.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError('O telefone é obrigatório.')
        if not validate_phone(phone):
            raise forms.ValidationError('O telefone informado é inválido.')
        return phone

    def clean_website(self):
        website = self.cleaned_data.get('website')
        if website and not validate_url(website):
            raise forms.ValidationError('O site informado é inválido.')
        return website
