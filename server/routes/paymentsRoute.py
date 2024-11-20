from flask import Blueprint,request,make_response
from flask_restful import Api,Resource
from models import db,Payment

payments_bp=Blueprint('payments_bp',__name__,url_prefix='/payments_route')
api=Api(payments_bp)

class Payments(Resource):
    def get(self):
        payments=[payment.to_dict() for payment in Payment.query.all()]
        
        if not payments:
            return make_response(
                {
                    "error":"Sorry no payments found"
                },404
            )
        
        return make_response(payments,200)
    
api.add_resource(Payments,'/payments')

class Payments_by_id(Resource):
    def put(self,id):
        payment=Payment.query.filter_by(id=id).first()
        data=request.get_json()
        
        if not payment:
            return make_response(
                {
                    "error":"Sorry no payment found"
                },404
            )
        
        for key,value in data.items():
            if hasattr(payment, key):
                setattr(payment,key,value)
        
        db.session.commit()
        
        return make_response(payment.to_dict(),200)

api.add_resource(Payments_by_id,'/payments/<uuid:id>')

        