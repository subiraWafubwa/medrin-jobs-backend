from flask import Blueprint,request,make_response
from flask_restful import Api,Resource
from models import db,Plans
import uuid
from uuid import UUID

plans_bp=Blueprint('plans_bp',__name__,url_prefix='/plans_route')
api=Api(plans_bp)

class Plan(Resource):
    def get(self):
        plans=[plan.to_dict() for plan in Plans.query.all()]
        
        if not plans:
            return make_response({
                "error":"No plans found"
            },404)
        
        return make_response(plans,200)
    
    def post(self):
        data=request.get_json()
        name=data['name']
        cost=float(data['cost']) if isinstance(data['cost'], (int, float, str)) and str(data['cost']).isdigit() else None
        description=data['description']
        job_limit=data.get('job_limit',None)
        duration_days=data.get('duration_days',None)
        
        
        if cost is None or cost < 0:
            return make_response({"error": "Invalid cost value. Must be a positive number."}, 400)
        
        new_plan = Plans(
            name=name,
            cost=cost,
            description=description,
            job_limit=job_limit,
            duration_days=duration_days
        )
        db.session.add(new_plan)
        db.session.commit()
        
        return make_response(
            new_plan.to_dict(),201)
api.add_resource(Plan,'/plans')

class Plan_by_id(Resource):
    def get(self,id):
        plan=Plans.query.filter_by(id=id).first()
        
        if not plan:
            return make_response(
                {
                    "error":"The plan of the specified id is not found"
                },400
            )
        
        return make_response(plan.to_dict(),200)
    
    def put(self,id):
        if isinstance(id,str):
            plan_id=UUID(id)
        else:
            plan_id = id
            
        data=request.get_json()
        print(data)
        
        if 'id' in data:
            del data['id']
    
        plan=Plans.query.filter_by(id=plan_id).first()
        if not plan:
            return make_response(
                {
                    "error":"The plan of the specified id is not found"
                },400
            )
        
        for key,value in data.items():
            setattr(plan,key,value)
        
        db.session.commit()
        
        return make_response(plan.to_dict(),200)
    
    def delete(self,id):
        plan=Plans.query.filter_by(id=id).first()
        if not plan:
            return make_response(
                {
                    "error":"The plan of the specified id is not found"
                },404
            )
        
        db.session.delete(plan)
        db.session.commit()
        
        return make_response({
            "message":"Plan successfully deleted"
        },200)

api.add_resource(Plan_by_id,'/plans/<uuid:id>')