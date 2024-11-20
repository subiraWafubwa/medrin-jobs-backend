from flask import Blueprint,request,make_response
from flask_restful import Api,Resource
from models import db,Subscription

subscription_bp=Blueprint('subscription_bp',__name__,url_prefix='/subscription_route')
api=Api(subscription_bp)

class Subscriptions(Resource):
    def get(self):
        subscriptions=[subscription.to_dict() for subscription in Subscription.query.all()]
        
        if not subscriptions:
            return make_response({
                "error":"No subscription is found"
            },404)
        
        return make_response(subscriptions,200)

api.add_resource(Subscriptions,'/subscriptions')

        