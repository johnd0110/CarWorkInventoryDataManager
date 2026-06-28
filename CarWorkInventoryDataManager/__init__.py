#TODO: Implement way to display purchase history
#TODO: Implement refunded/returned items, refunds have been partially implemented already

def create_and_initialize_app():
    """
    Initializes a Flask application with a car work inventory database.
    :return: The newly initialized Flask application
    """
    from flask import Flask
    new_app = Flask(__name__, template_folder='web/templates')

    from .config import default_config
    new_app.config.from_object(default_config)

    from blueprints import web_car, web_home
    new_app.register_blueprint(web_car)
    new_app.register_blueprint(web_home)

    from db import setupDbInfrastructureForApp
    setupDbInfrastructureForApp(new_app)

    from templateFilters import groupSqlResultsByColumns
    new_app.jinja_env.filters['groupSqlResultsByColumns'] = groupSqlResultsByColumns

    from customCLI import initializeCWITestData, initializeCWIDbSchema
    new_app.cli.add_command(initializeCWITestData)
    new_app.cli.add_command(initializeCWIDbSchema)

    # Make some html enums and text mappings available to all templates
    def htmlEnumProcessor():
        from datastructures import InputTypes, VisibilityOptions
        return dict(InputTypes=InputTypes, VisibilityOptions=VisibilityOptions)
    new_app.context_processor(htmlEnumProcessor)

    def textMappingProcessor():
        from mappings import getTextMapping
        return dict(textMap=getTextMapping())
    new_app.context_processor(textMappingProcessor)

    return new_app
