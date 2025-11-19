
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
class DfFreteDTO(DTOBase):
    # Atributos da entidade
    id: uuid.UUID = DTOField(
      pk=True,
      entity_field='df_frete',
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
    id_docfis: uuid.UUID = DTOField(
      not_null=True,
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    ibgeocorrenciafatorgeradoricms: str = DTOField()
    id_transportadora: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    modalidade: int = DTOField(
      not_null=True,)
    valorservico: float = DTOField()
    valorbcretencaoicms: float = DTOField()
    parcelaicmsretido: float = DTOField()
    valoricmsretido: float = DTOField()
    cfopservicotransporte: str = DTOField()
    placaveiculo: str = DTOField()
    ufveiculo: str = DTOField()
    rntcveiculo: str = DTOField()
    vagao: str = DTOField()
    balsa: str = DTOField()
    lastupdate: datetime.datetime = DTOField(        
        filters=[
          DTOFieldFilter("data_de", FilterOperator.GREATER_OR_EQUAL_THAN),
          DTOFieldFilter("data_ate", FilterOperator.LESS_OR_EQUAL_THAN),
        ]
    )
    id_veiculo: uuid.UUID = DTOField(
      strip=True,
      min=36,
      max=36,
      validator=DTOFieldValidators().validate_uuid,)
    tiporateio: int = DTOField()

