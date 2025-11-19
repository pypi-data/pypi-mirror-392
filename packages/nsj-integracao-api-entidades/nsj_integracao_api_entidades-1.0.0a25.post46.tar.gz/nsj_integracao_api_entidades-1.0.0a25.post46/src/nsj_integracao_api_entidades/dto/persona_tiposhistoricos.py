
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
class TiposhistoricoDTO(DTOBase):
    # Atributos da entidade
    id: str = DTOField(
      pk=True,
      entity_field='tipohistorico',
      resume=True,
      not_null=True,)
    tenant: int = DTOField(
      partition_data=tenant_is_partition_data,
      resume=True,
      not_null=True,)
    descricao: str = DTOField()
    grupo: int = DTOField(
      not_null=True,)
    subgrupo: int = DTOField()
    codigo: str = DTOField(
      not_null=True,)
    lastupdate: datetime.datetime = DTOField(        
        filters=[
          DTOFieldFilter("data_de", FilterOperator.GREATER_OR_EQUAL_THAN),
          DTOFieldFilter("data_ate", FilterOperator.LESS_OR_EQUAL_THAN),
        ]
    )

