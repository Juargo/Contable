"""Modelos de base de datos usando Tortoise ORM"""

from tortoise import fields, models

class Bank(models.Model):
    """Modelo para la tabla de bancos"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True)
    description = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        """Metadatos del modelo"""
        table = "banks"

    def __str__(self):
        return self.name

class Category(models.Model):
    """Modelo para la tabla de categorías"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    parent = fields.ForeignKeyField('models.Category', related_name='subcategories', null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        """Metadatos del modelo"""
        table = "categories"

    def __str__(self):
        return self.name

class CategoryKeyword(models.Model):
    """Modelo para las palabras clave de categorías"""
    id = fields.IntField(pk=True)
    category = fields.ForeignKeyField('models.Category', related_name='keywords')
    keyword = fields.CharField(max_length=100)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        """Metadatos del modelo"""
        table = "category_keywords"
        unique_together = (("category_id", "keyword"),)

    def __str__(self):
        return self.keyword

class Transaction(models.Model):
    """Modelo para la tabla de transacciones"""
    id = fields.IntField(pk=True)
    transaction_date = fields.DateField()
    description = fields.TextField()
    amount = fields.DecimalField(max_digits=10, decimal_places=0)
    category = fields.CharField(max_length=100, default="Sin clasificar")
    bank = fields.ForeignKeyField('models.Bank', related_name='transactions', null=True)
    # La columna currency aún no existe en la base de datos
    # currency = fields.CharField(max_length=3, default="CLP")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        """Metadatos del modelo"""
        table = "transactions"

    def __str__(self):
        return f"{self.transaction_date} - {self.description} - {self.amount}"

class IncomeTransaction(models.Model):
    """Modelo para las transacciones de ingresos"""
    id = fields.IntField(pk=True)
    transaction_date = fields.DateField(description="Fecha de la transacción")
    description = fields.CharField(max_length=255, description="Descripción de la transacción")
    amount = fields.DecimalField(max_digits=15, decimal_places=2, description="Monto de la transacción (valor positivo)")
    category = fields.CharField(max_length=100, default="Sin clasificar", description="Categoría de la transacción")
    bank_id = fields.IntField(null=True, description="ID del banco")
    created_at = fields.DatetimeField(auto_now_add=True, description="Fecha de creación")
    updated_at = fields.DatetimeField(auto_now=True, description="Fecha de actualización")

    class Meta:
        table = "transacciones_ingresos"
