
import datetime
import uuid

from nsj_rest_lib.decorator.dto import DTO
from nsj_rest_lib.descriptor.dto_field import DTOField, DTOFieldFilter
from nsj_rest_lib.descriptor.filter_operator import FilterOperator
from nsj_rest_lib.descriptor.dto_field_validators import DTOFieldValidators
from nsj_rest_lib.dto.dto_base import DTOBase



# Configuracoes execucao
from nsj_integracao_api_entidades.config import (tenant_is_partition_data)

@DTO()
class NegociacoesfornecedoreDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='negociacaofornecedor',
      resume=True,
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tenant: int = DTOField(
      partition_data=tenant_is_partition_data,
      resume=True,
      not_null=True,)
    fornecedor: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    negociacao: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    valorfrete: float = DTOField()
    valoroutrasdespesas: float = DTOField()
    ordem: int = DTOField(
      not_null=True,)
    fretemarcado: bool = DTOField()
    outrasdespesasmarcado: bool = DTOField()
    lastupdate: datetime.datetime = DTOField(
      filters=[
        DTOFieldFilter("data_de", FilterOperator.GREATER_OR_EQUAL_THAN),
        DTOFieldFilter("data_ate", FilterOperator.LESS_OR_EQUAL_THAN),
      ]
    )
    cotacaofornecedor: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    prazoentrega: int = DTOField()
    pis: float = DTOField()
    cofins: float = DTOField()
    icms: float = DTOField()
    icmsst: float = DTOField()
    ipi: float = DTOField()
    tributosmarcado: bool = DTOField()

