from models import (db,Company, Plan, Payment,User,PaymentTypeEnum,PlanEnum,Profile,Role,
                    RoleEnum,UserRole,IndustryEnum,Industry,JobLevelEnum,JobResponsibility,JobTag,
                    ApplicationStatusEnum,EducationLevelEnum,IndustryCompany,Job,Tag,UserTag,Requirement,Application,Education,Experience,Shortlisting)
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
# from flask_jwt_extended import jwt_required
from flask_migrate import Migrate
from flask_cors import CORS
# from auth import auth_bp,jwt,allow
from datetime import datetime,timezone,timedelta

app=Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
# jwt.init_app(app)
api=Api(app)
migrate=Migrate(app,db)

# API endpoint
@app.route('/')
def index():
    return '<h1>Project Server</h1>'

###################################################################### USER RESOURCE ############################################################################################
class Users(Resource):
    
    def get(self):
        users=[]
        for user in User.query.all():
            response_body={
                "id":user.id,
                "email":user.email,
                "code":user.code,
                "profile":user.profile,
                "role":user.roles
            }
            users.append(response_body)
        
        return make_response(users,200)
    
    #TO BE REVISTED DONT DELETE
    # def post(self):
        data=request.get_json()
        email=data['email']
        password=data['password']
        role_name=data['role']
        
        errors=[]
        
        role=Role.query.filter_by(name=role_name).first()
        
        if not "@" in email or not email:
            errors.append('email is required')
        if len(password) <8 :
            errors.append('Password should be at least 8 characters')
        
        user=User.get_user_by_email(email=email)
        
        if user is not None:
            errors.append('A user with that email exists')
        
        if errors:
            return make_response({
                "errors":errors
            },400)
        
        new_user=User(email=email)
        new_user.set_password(password)
        new_user.save()
        
        user_role=UserRole(user_id=new_user.id,role_id=role)
        db.session.add(user_role)
        db.session.commit()
        
        return make_response({
            "message":"User successfully created",
        },201)

api.add_resource(Users,'/users')
        
class User_by_id(Resource):
    def get(self,id):
        user=User.query.filter_by(id=id).first()
        
        if not user:
            return make_response({
                "message":"No user found"
            },400)
        
        return make_response(user.to_dict(),200)
    
    def delete(self,id):
        user=User.query.filter_by(id=id).first()
        if not user:
            return make_response({
                "message":"No user found"
            },400)
        
        user.delete()
        
        return make_response({
            "message":"user deleted successfully"
        },200)
    
    def put(self,id):
        user=user.query.filter_by(id=id).first()
        if not user:
            return make_response({
            "message":"No user found"
            },400)
        
        data=request.get_json()
        
        for key,value in data.items():
            setattr(user,key,value)
        
        db.session.commit()
        
        return make_response({
            "id":user.id,
            "email":user.email,
            "code":user.code,
            "profile":user.profile,
            "role":user.roles
            
        },200)    
            
            
            
api.add_resource(User_by_id,'/users/<int:id>')

##################################################################COMPANY RESOURCE##############################################################################################
class Companies(Resource):
    #this route is used by the admin to get all the companies in the system
    def get(self):
        companies=[company.to_dict() for company in Company.query.all()]
        if not companies:
            return make_response({
                "message":"No companies found"
            },400)        
        return make_response(companies,200)
    
    #this route is used by the admin to delete all the companies in the system
    def delete(self):
        companies=[company.to_dict() for company in Company.query.all()]
        if not companies:
            return make_response({
                "message":"No companies found"
            },400)

        Company.query.delete()
        return make_response({
            "message":"Companies have been deleted"
        },200)
api.add_resource(Companies,'/companies')

class Companies_by_id(Resource):
    #this route is used by the admin to delete the company based on the id
    def delete(self,id):
        company=Company.query.filter_by(id=id).first()
        
        if not company:
            return make_response({
                "message":"No company is found"
            })
        
        db.session.delete(company)
        db.session.commit()
        
        return make_response({
            "message":"company is successfully deleted"
        })
    
    #This route is used by the employer when he/she is updating the company details
    def put(self,id):
        company=Company.query.filter_by(id=id).first()
        if not company:
            return make_response({
                "message":"No company is found"
            })
        data=request.get_json()
        
        for key,value in data.items():
            setattr(company,key,value)
        
        db.session.commit()
        
        return make_response(company.to_dict,200)
    
api.add_resource(Companies_by_id,'/companies/<int:id>')

########################################################################### JOBS RESOURCE ######################################################################################
class Jobs(Resource):
    
    # This route is used by both the admin and the job_seeker to view all the available jobs 
    def get(self):
        jobs=[job.to_dict for job in Job.query.all()]
        
        if not jobs:
            return make_response({
                "message":"No jobs found"
            },400)
        
        return make_response(jobs,200)
    
    #This route is used by the employer to post a job
    def post(self):
        data=request.get_json()
        title=data['title']
        description=data['description']
        level=data['level']
        job_type=data['job_type']
        salary=data['salary']
        company_id=data['company_id']
        
        company=Company.query.filter_by(id=company_id).first()
        
        if not company:
            return make_response({
                "error":"Company with that company id is not found"
            },400)
        if not title or not isinstance(title, str):
            return make_response({
            "error": "Job title is required and should be a string"
        }, 400)
    
        if not description or not isinstance(description, str):
            return make_response({
            "error": "Job description is required and should be a string"
        }, 400)

        if not level or level not in ['entry_level', 'mid_level', 'senior_level']:
            return make_response({
            "error": "Job level is required and should be one of: entry_level, mid_level, senior_level"
        }, 400)

        if not job_type or job_type not in ['freelance', 'fulltime', 'parttime', 'internship']:
            return make_response({
            "error": "Job type is required and should be one of: freelance, fulltime, parttime, internship"
        }, 400)

        if not salary or not isinstance(salary, (int, float)):
            return make_response({
            "error": "Job salary is required and should be a number"
        }, 400)

        job = Job(
        title=title,
        description=description,
        level=level,
        job_type=job_type,
        salary=salary,
        company_id=company_id
        )
        
        db.session.add(job)
        db.session.commit()
        
        # Add multiple responsibilities
        for responsibility in data.get('responsibilities', []):
            job_responsibility = JobResponsibility(description=responsibility, job_id=job.id)
            db.session.add(job_responsibility)

        # Add multiple requirements
        for requirement in data.get('requirements', []):
            job_requirement = Requirement(description=requirement, job_id=job.id)
            db.session.add(job_requirement)
        
        db.session.commit()
        
        return make_response(job.to_dict(),201)
    
    #This route is used by the admin to delete all the jobs in the platform
    def delete(self):
        jobs=Job.query.all()
        
        if not jobs:
            return make_response({
                "error":"No jobs found"
            },400)
        
        Job.query.delete()
        
        return make_response({
            "error":"Jobs have been deleted successfully"
        },200)

api.add_resource(Jobs,'/jobs')

class Jobs_by_id(Resource):
    #this route is used by the employer to get all the jobs related to the employer's company
    def get(self,id):
        jobs=[job.to_dict() for job in Job.query.filter_by(company_id=id).all()]
        
        if not jobs:
            return make_response({
                "error":"No jobs have been found"
            },400)
            
        return make_response(jobs,200)
    
    #this route is used by the employer or admin to delete a particular job
    def delete(self,id):
        job=Job.query.filter_by(id=id).first()
        if not job:
            return make_response({
                "error":"No job is found"
            },400)
        db.session.delete(job)
        db.session.commit()
        
        return make_response({
            "message":"Job deleted successfuly"
        })
    #this route is used by the employer to edit a particular job
    def put(self,id):
        job=Job.query.filter_by(id=id).first()
        
        if not job:
            return make_response({
                "error":"No job is found"
            },400)
        
        data=request.get_json()
        for key,value in data:
            setattr(job,key,value)         
        job.update_at=datetime.now(timezone(timedelta(hours=3)))
        db.session.commit()
        
        return make_response(job.to_dict(),200)

api.add_resource(Jobs_by_id,'/jobs/<int:id>')

class Jobs_by_company_id(Resource):
    #this route is used by the employer to see all the jobs that belong to their company
    #NOTE HERE WE ARE USING COMPANY ID
    def get(self,id):
        jobs=[job.to_dict() for job in Job.query.filter_by(company_id=id)]
        
        if not jobs:
            return make_response(
                {
                    "error":"No jobs found"
                },400
            )
        
        return make_response(jobs,200)
    
api.add_resource(Jobs_by_company_id,'/jobs/company/<int:id>')        

############################################################################### APPLICATION RESOURCE #################################################################################################
    
    
    
# Running the app
if __name__ == '__main__':
    app.run(port=5555, debug=True)
