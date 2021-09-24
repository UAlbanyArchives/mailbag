from jsonmodels import models, fields, errors, validators

class Email(models.Base):
    """EmailModel - model class for email formats"""
    Message_ID = fields.StringField(required=True)
    Email_Folder = fields.StringField()
    Original_Filename = fields.StringField()
    Date = fields.StringField()
    From = fields.StringField()
    To = fields.StringField()
    Cc = fields.StringField()
    Bcc = fields.StringField()
    Subject = fields.StringField()
    Content_Type = fields.StringField()    