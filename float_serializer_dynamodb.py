from boto3.dynamodb import types
class FloatSerializer(types.TypeSerializer):
	# This one here raised Type error on floats.
	# By removing this error, we can work with floats in the first place.
	#
	# Original code uses six.integer_types here.
	# I work with 3.6 on this project, so I can omit six altogether.
    def _is_number(self, value):
        if isinstance(value, (int, decimal.Decimal, float)):
            return True
        return False

	# Add float-specific serialization code
    def _serialize_n(self, value):
        if isinstance(value, float):
            with decimal.localcontext(types.DYNAMODB_CONTEXT) as context:
                context.traps[decimal.Inexact] = 0
                context.traps[decimal.Rounded] = 0
                number = str(context.create_decimal_from_float(value))
                return number

        number = super(FloatSerializer, self)._serialize_n(value)
        return number
	
	# By the way, you can not write dictionaries with int/float/whatever keys as is,
	# boto3 does not convert them to strings automatically.
	#
	# And DynamoDB does not support numerical keys anyway,
	# so this crude workaround seems reasonable.
    def _serialize_m(self, value):
        return {str(k): self.serialize(v) for k, v in value.items()}

import boto3
from unittest.mock import patch

session = boto3.session()

# TypeSerializers are created on resource creation, so we need to patch it here.
with patch("boto3.dynamodb.types.TypeSerializer", new=FloatSerializer):
    db = session.resource("dynamodb")
