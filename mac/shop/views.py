from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum
MERCHANT_KEY = 'kbzk1DSbJiV_O3p5'
# Create your views here.
# products=Product.objects.all()
# print(products)
def index(request):
    products=Product.objects.all()
    # n=len(products)
    # nSlides = (n//4) + ceil((n/4)-(n//4))
    # params={'np_of_slides':nSlides,'product':products,'range':range(1,nSlides)}
    # allProds=[[products,range(1,nSlides),nSlides],[products,range(1,nSlides),nSlides]]  
    
    allProds=[]
    catProds=Product.objects.values('category','id')
    print(catProds)
    cats={item['category'] for item in catProds}
    for cat in cats:
        n=len(products)
        prod=Product.objects.filter(category=cat)
        nSlides = (n//4) + ceil((n/4)-(n//4))
        allProds.append([prod, range(1,nSlides),nSlides])        

    params={'allProds':allProds}
    return render(request,'shop/index.html',params)

def about(request):
    return render(request,'shop/about.html')

def contact(request):
    if request.method=="POST":
        hell=True
        name = request.POST.get('name','')#ye humne html form se liyA
        email = request.POST.get('email','')
        phone = request.POST.get('phone','')
        desc = request.POST.get('desc','')
        contact=Contact(name=name,email=email,phone=phone,desc=desc)
        #ye humne humare model ko arguments diye
        contact.save()
        return render(request,'shop/contact.html',{'hell': hell})

        #and isse save kiya 
        # print(name,email,phone,desc)

    return render(request,'shop/contact.html')

def tracker(request):
    if request.method=="POST":
        orderId= request.POST.get('orderId','')
        email = request.POST.get('email','')
        # return HttpResponse(f"{orderId} and {email}")
        try:
            order=Orders.objects.filter(order_id=orderId,email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success","updates":updates, "itemsJson":order[0].items_json} ,default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitemfound"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')
    return render(request,'shop/tracker.html')
def searchMatch(query,item):
    if (query).lower() in (item.product_name).lower() or (query).lower() in (item.desc).lower() or (query).lower() in (item.category).lower():
        return True
    else:
        return False

def search(request):
    query=request.GET.get('search')
    allProds=[]
    catProds=Product.objects.values('category','id')
    cats={item['category'] for item in catProds}
    for cat in cats:
        prodtemp=Product.objects.filter(category=cat)
        prod=[item for item in prodtemp if searchMatch(query,item)]
        n=len(prod)
        if n!=0:
            nSlides = (n//4) + ceil((n/4)-(n//4))
            allProds.append([prod, range(1,nSlides),nSlides])  
              

    params={'allProds':allProds,"msg":""}
    if len(allProds)==0 or len(query)<3:
        params={"msg":"No item found"}

    return render(request,'shop/search.html',params)


def productView(request, myid):
    #Fetch the product using the id
    product=Product.objects.filter(id=myid)
    # print(product)
    
    return render(request,'shop/prodview.html',{'product': product[0]})

def checkout(request):
        if request.method=="POST":
            itemsJson=request.POST.get('itemsJson','')
            name = request.POST.get('name','')#ye humne html form se liyA
            email = request.POST.get('email','')
            amount = request.POST.get('amount','')

            address = request.POST.get('address1','') + " " + request.POST.get('address2','')
            city = request.POST.get('city','')
            state = request.POST.get('state','')
            zip_code = request.POST.get('zip_code','')
            phone = request.POST.get('phone','')

            order=Orders(items_json=itemsJson,name=name,email=email,address=address,city=city,state=state,zip_code=zip_code,phone=phone,amount=amount)
        #ye humne humare model ko arguments diye
            order.save()
            thank=True
            update=OrderUpdate(order_id=order.order_id,update_desc="Your Order has been placed")
            id=order.order_id
            update.save()
            # return render(request,'shop/checkout.html',{"thank":thank,'id':id})
            # request paytm to accept and transfer the amount to your account after payment
            param_dict={
                    'MID': 'WorldP64425807474247',#yaha humari merchant id hpgi
                    'ORDER_ID': str(order.order_id),#yaha humari order id hogi
                    'TXN_AMOUNT': str(amount),
                    'CUST_ID': 'email',#customer ki id , hum order wale ki email
                    'INDUSTRY_TYPE_ID': 'Retail',
                    'WEBSITE': 'WEBSTAGING',#ye testing ke liye hoti hai 
                    'CHANNEL_ID': 'WEB',
                    'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/'
                    # 'CHECKSUMHASH':checksum.generate_checksum(param_dict.Me)
                    #callback url woh hai jaha paytm humein post bhejega ki payment hogaya ha
                    }
            param_dict['CHECKSUMHASH']=checksum.generate_checksum(param_dict,MERCHANT_KEY)
                    
            return render(request,"shop/paytm.html",{"param_dict":param_dict})
        #and isse save kiya 
        # print(name,email,phone,desc)
        return render(request,'shop/checkout.html')
    

def wishlist(request):
    return HttpResponse('We are at Wishlist')

def compare(request):
    return HttpResponse('We are at Compare')

# def get_data(request):
#     a=Product()
#     return HttpResponse(a)
# def display():
#     pass
#csrf token se kya hota hia ki dusra koi humare website pe kuch post bhej nhi sakta 
#ab agar paytm kobhejna hai req toh humein woh csrf nikalna padega , toh ek time ke liye hum csrf token nikalenge, dekhte hai kaise 
@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})
