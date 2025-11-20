from pydantic import BaseModel

from tortoise import fields, Model


class Student(Model):
    id = fields.IntField(pk=True, description="主键")
    username = fields.CharField(max_length=128, null=True, description="用户名")
    score = fields.IntField(null=True, description="分数")

    class Meta:
        table = "student"
        table_description = "学生表"

    def __str__(self):
        return f"Student(id={self.id}, username={self.username}, score={self.score})"
