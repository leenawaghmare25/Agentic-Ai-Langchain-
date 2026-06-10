from marshmallow import Schema, fields

class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    priority = fields.Str(required=True)
    completed = fields.Bool(dump_only=True)
