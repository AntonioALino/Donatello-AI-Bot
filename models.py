from tortoise import fields, models
from tortoise.contrib.postgres.fields import ArrayField

class Vaga(models.Model):
    id = fields.IntField(pk=True)
    titulo = fields.TextField()
    empresa = fields.TextField()
    link = fields.CharField(max_length=512, unique=True)
    tags = ArrayField(element_type="text")
    origem = fields.TextField()

    class Meta:
        table = "vagas" 

    def __str__(self):
        return self.titulo