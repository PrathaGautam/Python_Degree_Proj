#testuser@gmail.com, pw = test
import uuid

from fastapi import FastAPI, Request, Form, Response, Depends, File, UploadFile
from jinja2 import Template
from typing import Annotated
import mysql.connector
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
from jinja2 import Environment, FileSystemLoader
import pymysql
import re
from fastapi.templating import Jinja2Templates
import mysql.connector
from mysql.connector import errorcode
import bcrypt
from auth_utils import create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES


# from sqlread2 import cursor

app = FastAPI()

try:
    connection = pymysql.connect(
        host='localhost',
        user='pratha',
        password='12345',
        database='AdvertisementsDb',
        cursorclass=pymysql.cursors.DictCursor

    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your username or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)




def query_db(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result


# Set the directory containing the templates
template_dir = os.path.join(os.path.dirname(__file__), 'templates')

# Create the template environment
env = Environment(loader=FileSystemLoader(template_dir))

templates = Jinja2Templates(directory="templates/")

# Load the templates
# top_menu_template = env.get_template('top_menu.html')
# content_template = env.get_template('content.html')
app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def read_root():
    return {"Hello": "World"}  # dictionary, this will be automatically converted to json


# to run this,type command uvicorn main:app --reload


@app.get("/products")  # getting ad table and printing data on website
async def read_ad(request: Request):
    result = query_db("SELECT * from ads")
    access_token = request.cookies.get("access_token")
    username = None
    if access_token is not None:
        email = get_email_from_token(access_token)
        username, user_id = get_username_and_id_by_email(email)
    return templates.TemplateResponse("displayingads.html",
                                      {"request": request, "username": username, "data": result})





@app.get("/home")
async def x(request: Request):
    access_token = request.cookies.get("access_token")
    if access_token:
        email = get_email_from_token(access_token)
        user_params = (email,)
        result = query_db("SELECT FirstName from users where email = %s", user_params)
        username = result[0]['FirstName']
    else:
        username = None

    if access_token is not None:
        return templates.TemplateResponse("home_page.html", {"request": request, "username": username})
    else:
        return templates.TemplateResponse("home_page.html", {"request": request, "username": None})



@app.get("/aboutus")
async def templateHome(request: Request):
    access_token = request.cookies.get("access_token")
    if access_token:
        email = get_email_from_token(access_token)
        username, user_id = get_username_and_id_by_email(email)
    else:
        username = None

    if access_token is not None:
        return templates.TemplateResponse("about_us_page.html",
                                          {"request": request, "username": username})
    else:
        return templates.TemplateResponse("about_us_page.html", {"request": request, "username" : None})


@app.get("/contactus")
async def templateHome(request: Request):
    access_token = request.cookies.get("access_token")
    if access_token:
        email = get_email_from_token(access_token)
        username, user_id = get_username_and_id_by_email(email)
    else:
        username = None

    if access_token is not None:
        return templates.TemplateResponse("contact_us.html",
                                          {"request": request, "username": username})
    else:
        return templates.TemplateResponse("contact_us.html", {"request": request, "username": None})

def get_email_from_token(access_token: str) -> str:
    access_token = access_token.split()[-1]
    token_and_email = decode_access_token(access_token)
    return token_and_email['sub']

def get_username_and_id_by_email(email:str) -> str:
    # email = get_email_from_token(access_token)
    user_params = (email,)
    result = query_db("SELECT FirstName, IdUser from users where email = %s", user_params)
    username = result[0]['FirstName']
    user_id = result[0]['IdUser']
    return username, user_id


@app.get("/details")
async def details(request: Request):

    # to check if ad is of owner :
    opened_by_owner = False
    print(request.query_params)
    # template = env.get_template("detailsOfAds.html")
    ad_id = request.query_params["id"]
    user_params = (ad_id,)
    result = query_db("SELECT * from ads where idad = %s", user_params)
    access_token = request.cookies.get("access_token")

    if access_token:
        email = get_email_from_token(access_token)
        username, user_id = get_username_and_id_by_email(email)
    else:
        email = None
        username = None
        user_id = None
    if not result:
        return templates.TemplateResponse("404.html",
                                          {"request": request, "username": username}, status_code=404)
    print(result)
    user_id_from_ad = result[0]['userID']

    if user_id == user_id_from_ad:
        opened_by_owner = True
    print(f"DETAILS {user_id=} {user_id_from_ad=}")

    return templates.TemplateResponse("detailsofAds.html",
                                      {"request": request, "username": username,"email":email, "data": result[0], "opened_by_owner":opened_by_owner})
    # html_content = template.render(data=result[0])
    # return HTMLResponse(content=html_content, status_code=200)









@app.get("/signup")
def form_get(request: Request, first_name: str = "", last_name: str = "", email: str ="", password: str="", repeat_password: str=""):
    # my_dict={"firstname": "First Name:", "lastname":"Last Name:", "email":"Email", "password":"Password", "repeatpassword":"Repeat Password"}

    return templates.TemplateResponse("sign_up_page.html", {"request": request, "firstname": first_name, "lastname ": last_name, "email" : email,"password" : password,"repeatpassword":repeat_password})



@app.post("/signup")
def form_post(request: Request,
              first_name: str = Form(""),
              last_name: str = Form(""),
              password: str = Form(""),
              repeat_password: str = Form(""),
              email: str = Form("")):
    firstname_error = ""
    lastname_error = ""
    email_error = ""
    password_error=""
    repeat_password_error=""
    print(request.__dict__)
    print("VALUES:"+"\n".join((first_name, last_name, password, repeat_password, email)))
    if len(first_name)<1 or len(first_name)>=50:
        firstname_error="First Name must be between 1 and 50 characters."

    if len(last_name)<1 or len(last_name)>=50:
        lastname_error = "Last Name must be between 1 and 50 characters."

    regex = r"(.+)@(.+)\.(.+)"
    if not re.match(regex, email):
        email_error="Not a valid email address."

    if len(password)<3 or len(password)>=50:
        password_error = "Password must be between 3 and 50 characters."

    if password != repeat_password:
        repeat_password_error="Passwords do not match."

        # to check if email is unique and add users to mysql if unique :

    if not any((email_error, password_error, firstname_error, lastname_error, repeat_password_error)):
        user_params = (email,)
        result = query_db(f"SELECT Email from users WHERE Email=%s",user_params)
        if result:
            email_error = "This email already exists, put a new email."
        else:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

            add_user = (f"INSERT INTO users "
                        f"(FirstName, LastName, Email, Password) "
                        f"VALUES (%s, %s, %s, %s)")
            user_data = (first_name, last_name, email, hashed)

            user_data = query_db(add_user, user_data)
            print(f"This is the user data afetr sign up: {user_data}")
            print(type(user_data))
            connection.commit()

            # Return a success message to the user
            # access_token = create_access_token({"sub": email})
            access_token = create_access_token({"sub": email})
            response = RedirectResponse(url="/home", status_code=303)
            # response = Response()
            response.set_cookie(
                key="access_token",
                value=f"Bearer {access_token}",
                httponly=True,
                max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )

            return response



    # request = fastapi.Request(scope=request.scope)
    return templates.TemplateResponse('sign_up_page.html', {'request': request,"first_name":first_name,"firstname_error":firstname_error, "last_name":last_name,"lastname_error":lastname_error,
                                                            "email": email, "email_error": email_error,
                                                            "password": password, "password_error": password_error,
                                                            "repeat_password": repeat_password, "repeat_password_error": repeat_password_error})




@app.post("/uploadads")
async def upload_ad(
    request: Request,
    title: str = Form(...),
    photo: UploadFile = File(...),
    price: float = Form(...),
    negotiation: bool = Form(False),
    condition: str = Form(...),
    description: str = Form(...),
    phone: str = Form(...)

):
    access_token = request.cookies.get("access_token")
    if access_token is not None:
        email = get_email_from_token(access_token)
        username, user_id = get_username_and_id_by_email(email)
    else:
        return RedirectResponse(url=f"/forbidden.html", status_code=403)


    # Get the user ID of the logged-in user
    # user_id = get_user_id_from_email(email)
    # Generate a UUID for the photo
    photo_uuid = str(uuid.uuid4())

    # Get the file extension of the uploaded file
    extension = photo.filename.split(".")[-1]

    # Construct the filename with the UUID and file extension
    filename = f"{photo_uuid}.{extension}"


    # Save the uploaded file
    file_data = await photo.read()

    with open(f"uploads/{filename}", "wb") as f:
        f.write(file_data)

    # Insert the ad into the database
    insert_query = (
        "INSERT INTO ads "
        "(title, photo, price, negotiation, `Condition`, description, phone_number, userId) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    )
    insert_values = (
        title,
        filename,
        price,
        negotiation,
        condition,
        description,
        phone,
        user_id,
    )

    result = query_db(insert_query, insert_values)
    print(result)
    connection.commit()
    ad_id = query_db("SELECT LAST_INSERT_ID();")[0]['LAST_INSERT_ID()']
    print("ad_id:")
    print(ad_id)

    response = RedirectResponse(url=f"/details?id={ad_id}", status_code=303)
    return response


@app.get("/uploadads")
async def templateHome(request: Request):
    access_token = request.cookies.get("access_token")
    if access_token is not None:
        email = get_email_from_token(access_token)
        username, user_id = get_username_and_id_by_email(email)
        return templates.TemplateResponse("uploadads.html",
                                      {"request": request, "username": username})
    else:
        return templates.TemplateResponse("detailsOfAds.html",
                                          {"request": request, "username": None})

# get method to get the page which shows email and password box and login button
@app.get("/login")
async def templateHome(request: Request):
    template = env.get_template("login_page.html")
    html_content = template.render(data={})
    return HTMLResponse(content=html_content, status_code=200)

# post method for login page to verify in data base if email and password are same :
@app.post("/login")
def login(request: Request,password: str = Form(""),email: str = Form("")):
    user_params=(email,)
    result=query_db("SELECT IdUser,FirstName,LastName,Password from users WHERE Email=%s",user_params)
    ########################################################
    if len(result)==0:
        login_error = "Incorrect email or password."
        return templates.TemplateResponse("login_page.html", {"request": request, "login_error": login_error})
    else:

        id_user = result[0]["IdUser"]
        first_name = result[0]["FirstName"]
        last_name = result[0]["LastName"]
        hashed = result[0]["Password"]

    ##############################################

    # use photo@gmail.com and password : photo

    if bcrypt.hashpw(password.encode(), hashed.encode()) == hashed.encode():
        access_token = create_access_token({"sub": email})
        response = RedirectResponse(url="/home", status_code=303)
        #response = Response()
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES*60
        )
        return response
    else:
        return "WRONG PASSWORD"


@app.get("/logout")
async def logout(request: Request, response: Response):
    response = templates.TemplateResponse(
        "home_page.html", {"request": request, "username": None})
    response.delete_cookie(key="access_token")
    return response

@app.post("/delete_ad/{ad_id}")
def deleting_ad(ad_id:int, response: Response, request: Request):
    user_params = (ad_id,)
    result = query_db("SELECT * from ads where idad = %s", user_params)
    access_token = request.cookies.get("access_token")



    if access_token:
        email = get_email_from_token(access_token)
        username, user_id = get_username_and_id_by_email(email)
        if not result:
            return templates.TemplateResponse("404.html",
                                              {"request": request, "username": username}, status_code=404)

        user_id_from_ad = result[0].get('userID')
        if user_id == user_id_from_ad:
            query_db("DELETE FROM ads where idad = %s", user_params)
            connection.commit()
            response = RedirectResponse(url="/products", status_code=303)
        else:
            response = RedirectResponse(url="/forbidden.html", status_code=403)
    return response





