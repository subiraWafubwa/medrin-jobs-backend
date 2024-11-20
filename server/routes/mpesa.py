import base64
import requests
from datetime import datetime
from flask import Blueprint,request,make_response
from flask_restful import Api,Resource
from dotenv import load_dotenv
from models import db,User,Plans,Subscription,Payment,Organisation
from uuid import UUID
import os


load_dotenv()

mpesa_bp=Blueprint('mpesa_bp',__name__,url_prefix='/mpesa')
api=Api(mpesa_bp)


consumer_key=os.getenv('Consumer_key')
consumer_secret_key=os.getenv('Consumer_secret')

#token
def authorization(url):
    #Base64 encode consumer_key and consumer_secret_key
    plain_text=f'{consumer_key}:{consumer_secret_key}'
    bytes_obj=bytes(plain_text,'utf-8')
    bs4=base64.b64encode(bytes_obj)
    bs4str=bs4.decode()
    headers={
        'Authorization':'Basic ' + bs4str
    }
    res=requests.get(url,headers=headers)
    return res.json().get('access_token')

def generate_timestamp():
    time = datetime.now().strftime('%Y%m%d%H%M%S')
    return time

def create_password(shortcode,passkey,timestamp):
    plain_text = shortcode+passkey+timestamp
    bytes_obj = bytes(plain_text, 'utf-8')
    bs4 = base64.b64encode(bytes_obj)
    bs4 = bs4.decode()
    return bs4


def format_phone_number(number):
    number_str=str(number)
    if number_str.startswith('07'):
        return '254' + number_str[1:]
    
    elif number_str.startswith('254'):
        return number_str
    else:
        return None

class Payments(Resource):
    def post(self):
        data=request.get_json()
        number=data['number']
        amount=data['amount']
        
        #I have include what we are paying for and who is paying details in the request
        plan_id = data.get('plan_id')  
        user_id = data.get('user_id')
        
        
        
        try:
            user_id_u = UUID(user_id)
            plan_id_u = UUID(plan_id)
        except (ValueError, TypeError):
            return make_response({"error": "Invalid user_id or plan_id format"}, 400)
            
        
        
        #query the organization based from the user_id
        organization=Organisation.query.filter_by(user_id=user_id_u).first()
        
        #here I validate the plan and user 
        user = User.query.filter_by(id=user_id_u).first()
        plan = Plans.query.filter_by(id=plan_id_u).first()
        
        if not user:
            return make_response({
                "error": "User not found"}, 404)
        
        if not organization:
            return make_response({
                "error":"Organization is not found"
            },404)
        
        
        if not plan:
            return make_response({
                "error": "Plan not found"}, 404)
        
        
        if not amount or not str(amount).isdigit() or int(amount) <=0:
            return make_response(
                {
                    "error":"Please enter a valid amount and the value should be greater than zero"
                },400
            )
        
        formatted_phone_number=format_phone_number(number)
        time=generate_timestamp()
        password=create_password("174379","bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919",time)
        
        payload = {
            "BusinessShortCode": 174379,
            "Password": password,
            "Timestamp": time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": 254790453418,
            "PartyB": 174379,
            "PhoneNumber": formatted_phone_number,
            "CallBackURL": "https://major-aardvark-secondly.ngrok-free.app/mpesa/payment_result",
            "AccountReference": "Medrin",
            "TransactionDesc": f'Payment for {plan.name}'
         } 
        
        token = authorization('https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials')
        headers = {'Authorization': 'Bearer '+token}
        res = requests.post('https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest', headers=headers, json=payload)
        response_data=res.json()
        
        new_payment=Payment(
            amount=amount,
            phone_number=formatted_phone_number,
            transaction_reference=response_data.get('CheckoutRequestID'),
            plan_id=plan_id_u,
            organisation_id=organization.id
        )
        
        db.session.add(new_payment)
        db.session.commit()
        return make_response(
            {"message": "Payment initiated", "data": response_data}, res.status_code)

class Payment_result(Resource):
    def post(self):
        print("Callback received:", request.json)
        callback_data = request.json
        checkout_request_id = callback_data['Body']['stkCallback']['CheckoutRequestID']
        result_code = callback_data['Body']['stkCallback']['ResultCode']
        
        payment = Payment.query.filter_by(transaction_reference=checkout_request_id).first()
        
        if not payment:
            return make_response({
                "error":"Payment Not Found"
            },404)
        
        if result_code == 0:  # here when  the result code is successful ,the payment_status becomes succesfull
            payment.payment_status = "success"
            db.session.commit()
            
            #creating a new subscription
            new_subscription = Subscription(organization_id=payment.organization_id, plan_id=payment.plan_id)
            db.session.add(new_subscription)
            db.session.commit()
            
            return make_response({
                "message": "Payment successful and subscription created"}, 200)
        
        else:
            payment.payment_status = "failed"
            db.session.commit()
            
            return make_response({"message": "Payment failed"}, 400)
        
# class Payment_status(Resource):
#     def get(self, checkout_request_id):
#         payment = Payment.query.filter_by(transaction_reference=checkout_request_id).first()
#         if payment:
#             if payment.payment_status == "success":
#                 return {"message": "Payment successful",}, 200
#             elif payment.payment_status == "failed":
#                 return {"message": "Payment failed"}, 400
#             else:
#                 return {"message": "Payment pending"}, 202
#         return {"error": "Payment not found"}, 404
        
        
api.add_resource(Payments,'/make_payment')   
api.add_resource(Payment_result,'/payment_result')
# api.add_resource(Payment_status, '/payment_status/<string:checkout_request_id>')        