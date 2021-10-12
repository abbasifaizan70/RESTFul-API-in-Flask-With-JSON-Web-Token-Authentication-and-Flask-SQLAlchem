from flask import Flask, Blueprint, request
from flask_restplus import Api, Resource, fields
from marshmallow import Schema, fields as ma_fields, post_load
from werkzeug import Authorization
from functools import wraps

app = Flask(__name__)
# blueprint = Blueprint('api', __name__, url_prefix='/api')
# api = Api(blueprint, doc='/documentation') # doc = False (in the case of you dont want to show documentation to user)

# app.register_blueprint(blueprint)

# app.config['SWAGGER_UI_JSONEDITOR']=True

authorizations ={
    'apikey' : {
        'type':'apiKey',
        'in' : 'header',
        'name' : 'X-API-KEY'
    }
}

api=Api(app, authorizations=authorizations)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

        if not token:
            return {'message':'Token is missing.'},401

        if token != 'mytoken':
            return {'message':'Token you entered is wrrong'},401


        print ('Token : {}'.format(token))
        return f(*args, **kwargs)
    
    return decorated


class TheLanguage(object):
    def __init__(self, language, framework):
        self.language= language
        self.framework=framework

    def __repr__(self):
        return '{} is the Language. {} is the Framwework'.format(self.language, self.framework)

class LanguageSchema(Schema):
    language = ma_fields.String()
    framework = ma_fields.String()

    @post_load
    def create_language(self, data,**kwargs):
        return TheLanguage(**data)

a_language = api.model('Language',{'language': fields.String('Enter language Here'), 'framework': fields.String('Enter Framework Here.')} )

languages=[]
# python={'language': 'Python', 'id' : 1}
python= TheLanguage(language='Python', framework='Flask')
languages.append(python)

@api.route('/language')
class Language(Resource):

    # @api.marshal_with(a_language, envelope='The Data')
    @api.doc(security = 'apikey')
    @token_required
    def get(self):
        schema =LanguageSchema(many=True)

        return schema.dump(languages)

    @api.expect(a_language)
    def post(self):
        schema =LanguageSchema()

        new_language = schema.load(api.payload)
        print(new_language)
        # new_languages['id'] = len(languages)+1
        languages.append(new_language)
        print(languages)
        # languages.append(api.payload)
        return {'Result':'Language Added Successfully'},201

if __name__=='__main__':
    app.run(debug=True)