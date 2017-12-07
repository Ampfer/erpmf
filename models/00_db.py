# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(myconf.get('db.uri'), 
             pool_size = myconf.get('db.pool_size'),
             migrate_enabled = myconf.get('db.migrate'),
             check_reserved = ['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=myconf.get('host.names'))
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
#mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
mail.settings.server = 'smtp.gmail.com:587'
#mail.settings.sender = myconf.get('smtp.sender')
mail.settings.sender = 'mfengenharia.amparo@gmail.com'
#mail.settings.login = myconf.get('smtp.login')
mail.settings.login =  'mfengenharia.amparo@gmail.com:@mf123456'
#mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.tls = True
#mail.settings.ssl = myconf.get('smtp.ssl') or False
#mail.settings.ssl = True

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

def moeda(valor):
    from locale import setlocale, currency, LC_ALL
    try:
        setlocale(LC_ALL, 'pt_BR.UTF-8')
    except:
        setlocale(LC_ALL, 'portuguese')
    return '%s' % currency(valor, grouping=True, symbol=False)

data = IS_NULL_OR(IS_DATE(format=T("%d/%m/%Y")))
def make_data(field):
    if field != None:
        return field.strftime("%d/%m/%Y")

Relatorio = db.define_table('relatorio',
                            Field('datarel','date',label ='Data'),
                            Field('codigo','string',label='Código',length=7),
                            Field('descricao','string',label='Descrição'),
                            Field('unidade','string',label='Unidade',length=4),
                            Field('etapa','string',label='Etapa',length=30),
                            Field('quantidade','decimal(7,2)',label='Quantidade'),
                            Field('valor','decimal(7,2)',label='Valor'),
                            #Field('total','decimal(7,2)',label='Total'),
                            Field('total', compute=lambda r: (r['valor'] * r['quantidade']).quantize(Decimal('1.00'), rounding=ROUND_HALF_UP)),
                            Field('porcentagem','decimal(7,2)',label='%'),
                            Field('acumulado','decimal(7,2)',label='Acumulado')
                            )
Relatorio.quantidade.requires = IS_DECIMAL_IN_RANGE(dot=',')
Relatorio.valor.requires = IS_DECIMAL_IN_RANGE(dot=',')
Relatorio.porcentagem.requires = IS_DECIMAL_IN_RANGE(dot=',')
Relatorio.acumulado.requires = IS_DECIMAL_IN_RANGE(dot=',')
Relatorio.total.requires = IS_DECIMAL_IN_RANGE(dot=',')
Relatorio.datarel.requires = data
Relatorio.datarel.represent = lambda value, row: value.strftime("%d/%m/%Y")

Emails = db.define_table('email',
    Field('email','string',label='Email:',length=100),
    Field('assunto','string',label='Assunto:',length=100),
    Field('mensagem','text',label='Mensagem:'),
    Field('anexo','string',label='Anexo:',length=20)
    )
Emails.email.requires=IS_NOT_EMPTY()
Emails.assunto.requires=IS_NOT_EMPTY()
Emails.mensagem.requires=IS_NOT_EMPTY()

class IS_CPF_OR_CNPJ(object):
 
    def __init__(self, format=False, error_message=T('Número incorreto!')):
        self.error_message = error_message
        self.format = format
 
    def __call__(self, value):
        try:
            cl = str(''.join(c for c in value if c.isdigit()))
 
            if len(cl) == 11:
                cpf = cl
                cnpj = None
            elif len(cl) == 14:
                cpf = None
                cnpj = cl
            else:
                return value, self.error_message
 
            if cpf:
                def calcdv(numb):
                    result = int()
                    seq = reversed(
                        ((range(9, -1, -1)*2)[:len(numb)])
                    )
                    for digit, base in zip(numb, seq):
                        result += int(digit)*int(base)
                    dv = result % 11
                    return (dv-10) and dv or 0
 
                numb, xdv = cpf[:-2], cpf[-2:]
 
                dv1 = calcdv(numb)
                dv2 = calcdv(numb + str(dv1))
                if '%d%d' % (dv1, dv2) == xdv:
                    return self.doformat(cpf) if self.format else cpf, None
                else:
                    return cpf, T('CPF inválido')
 
            elif cnpj:
 
                intmap = map(int, cnpj)
                validate = intmap[:12]
 
                prod = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
                while len(validate) < 14:
                    r = sum([x*y for (x, y) in zip(validate, prod)]) % 11
                    f = 11 - r if r > 1 else 0
                    validate.append(f)
                    prod.insert(0, 6)
 
                if validate == intmap:
                    return self.doformat(cnpj) if self.format else cnpj, None
 
                else:
                    return cnpj, T('CNPJ inválido')
 
        except:
            return value, self.error_message
 
    def doformat(self, value):
            if len(value) == 11:
                result = value[0:3] + '.' + value[3:6] + '.' + value[6:9] + \
                    '-' + value[9:11]
            elif len(value) == 14:
                result = value[0:2] + '.' + value[2:5] + '.' + value[5:8] + \
                    '/' + value[8:12] + '-' + value[12:14]
            else:
                result = value
            return result

