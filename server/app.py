from config import app, init_extensions
from routes.AuthRoutes import auth_bp
from routes.UserRoutes import get_data_bp
from routes.JobRoutes import job_bp
from routes.ApplicationRoutes import application_bp

# Initialize extensions with the app
init_extensions(app)
app.register_blueprint(auth_bp)
app.register_blueprint(get_data_bp)
app.register_blueprint(job_bp)
app.register_blueprint(application_bp)

# API endpoint
@app.route('/')
def index():
    return '<h1>Medrin Jobs Server</h1>'

# Running the app
if __name__ == '__main__':
    app.run(port=5555, debug=True)
