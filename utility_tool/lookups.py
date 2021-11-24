from __future__ import unicode_literals
from selectable.base import ModelLookup
from selectable.registry import registry
from .models import Fruit

class FruitLookup(ModelLookup):
    model = Fruit
    search_fields = ('name__icontains', )

registry.register(FruitLookup)