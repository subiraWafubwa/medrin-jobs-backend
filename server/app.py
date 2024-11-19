from config import app, init_extensions
from routes.AuthRoutes import auth_bp
from routes.UserRoutes import get_data_bp
from routes.JobRoutes import job_bp
from routes.AdminRoutes import admin_bp
from routes.ApplicationRoutes import application_bp
from routes.OrganisationRoutes import organisation_bp
from routes.JobseekerRoutes import jobseeker_bp
from routes.mpesa import mpesa_bp
from routes.plansRoute import plans_bp
from routes.paymentsRoute import payments_bp
from routes.subscriptionRoutes import subscription_bp

# Initialize extensions with the app
init_extensions(app)
app.register_blueprint(auth_bp)
app.register_blueprint(get_data_bp)
app.register_blueprint(job_bp)
app.register_blueprint(organisation_bp)
app.register_blueprint(application_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(jobseeker_bp)
app.register_blueprint(mpesa_bp)
app.register_blueprint(plans_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(subscription_bp)





# API endpoint
@app.route('/')
def index():
    return '<h1>Medrin Jobs Server</h1>'

# Running the app
if __name__ == '__main__':
    app.run(port=5555, debug=True)
