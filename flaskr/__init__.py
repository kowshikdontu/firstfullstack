import os
from flask import Flask
from flaskr.db import init_db
def create_app(test_config=None):
    app=Flask(__name__,instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path,'flaskr.sqlite'),
    )
    if test_config is None:
        app.config.from_pyfile('config.py',silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'hello world'

    from . import db
    db.init_app(app)
    from . import home
    app.register_blueprint(home.bp)
    from . import auth
    app.register_blueprint(auth.bp)
    from . import analysis
    app.register_blueprint(analysis.bp FLASK_APP)



    return app
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
