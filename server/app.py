from config import app, db, init_extensions
import models

# Initialize extensions with the app
init_extensions(app)

# API endpoint
@app.route('/')
def index():
    return '<h1>Project Server</h1>'

# Running the app
if __name__ == '__main__':
    app.run(port=5555, debug=True)
