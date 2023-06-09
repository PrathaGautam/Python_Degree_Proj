import uuid
from fastapi import FastAPI, Request, Form, Response,File, UploadFile
from typing import Tuple
from starlette.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
from jinja2 import Environment, FileSystemLoader
import pymysql
import re
from fastapi.templating import Jinja2Templates
import bcrypt
from auth_utils import create_access_token, decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI()


class ConnectionPool:
    def __init__(self, initial_size=5, **kwargs):
        self.kwargs = kwargs

    def get_connection(self):
        return pymysql.connect(**self.kwargs)

    def release_connection(self, conn):
        conn.close()


pool = ConnectionPool(
    host='localhost',
    user='pratha',
    password='12345',
    database='AdvertisementsDb',
    cursorclass=pymysql.cursors.DictCursor,
    connect_timeout=30
)


def query_db(query, params=None, commit=False, get_last_id=False):
    connection = pool.get_connection()
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        result = cursor.fetchall()
        if get_last_id:
            cursor.execute("SELECT LAST_INSERT_ID();")
            result = cursor.fetchall()[0]['LAST_INSERT_ID()']
    if commit:
        connection.commit()

    pool.release_connection(connection)
    return result


template_dir = os.path.join(os.path.dirname(__file__), 'templates')

env = Environment(loader=FileSystemLoader(template_dir))

templates = Jinja2Templates(directory="templates/")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    return RedirectResponse("/home")


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
        return templates.TemplateResponse("about_us_page.html", {"request": request, "username": None})


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


def get_username_and_id_by_email(email: str) -> Tuple[str, str]:
    user_params = (email,)
    result = query_db("SELECT FirstName, IdUser from users where Email = %s", user_params)
    username = result[0]['FirstName']
    user_id = result[0]['IdUser']
    return username, user_id


@app.get("/details")
async def details(request: Request):
    opened_by_owner = False
    print(request.query_params)
    ad_id = request.query_params["id"]
    user_params = (ad_id,)
    result = query_db("SELECT * from ads WHERE idad = %s", user_params)
    access_token = request.cookies.get("access_token")
    if not result:
        return templates.TemplateResponse("404.html",
                                          {"request": request}, status_code=404)
    user_id_from_ad = result[0]['userID']
    ad_email = None
    if user_id_from_ad:
        user_params = (user_id_from_ad,)
        ad_email = query_db("SELECT Email from users WHERE IDUser=%s", user_params)
        ad_email = ad_email[0]['Email']

    if access_token:
        email = get_email_from_token(access_token)
        username, user_id = get_username_and_id_by_email(email)
    else:
        email = None
        username = None
        user_id = None
    user_id_from_ad = result[0]['userID']

    if user_id == user_id_from_ad:
        opened_by_owner = True
    print(f"DETAILS {user_id=} {user_id_from_ad=}")

    return templates.TemplateResponse("detailsofAds.html",
                                      {"request": request, "username": username, "email": email, "ad_email": ad_email,
                                       "data": result[0], "opened_by_owner": opened_by_owner})

@app.get("/signup")
def form_get(request: Request, first_name: str = "", last_name: str = "",
             email: str = "", password: str = "", repeat_password: str = ""):
    return templates.TemplateResponse("sign_up_page.html", {"request": request,
                                                            "firstname": first_name,
                                                            "lastname ": last_name,
                                                            "email": email,
                                                            "password": password,
                                                            "repeatpassword": repeat_password})

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
    password_error = ""
    repeat_password_error = ""
    print(request.__dict__)
    print("VALUES:" + "\n".join((first_name, last_name, password, repeat_password, email)))
    if len(first_name) < 1 or len(first_name) >= 50:
        firstname_error = "First Name must be between 1 and 50 characters."

    if len(last_name) < 1 or len(last_name) >= 50:
        lastname_error = "Last Name must be between 1 and 50 characters."

    regex = r"(.+)@(.+)\.(.+)"
    if not re.match(regex, email):
        email_error = "Not a valid email address."

    if len(password) < 3 or len(password) >= 50:
        password_error = "Password must be between 3 and 50 characters."

    if password != repeat_password:
        repeat_password_error = "Passwords do not match."

    if not any((email_error, password_error, firstname_error, lastname_error, repeat_password_error)):
        user_params = (email,)
        result = query_db(f"SELECT Email from users WHERE Email=%s", user_params)
        if result:
            email_error = "This email already exists, put a new email."
        else:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

            add_user = (f"INSERT INTO users "
                        f"(FirstName, LastName, Email, Password) "
                        f"VALUES (%s, %s, %s, %s)")
            user_data = (first_name, last_name, email, hashed)

            user_data = query_db(add_user, user_data, commit=True)
            print(f"This is the user data afetr sign up: {user_data}")
            print(type(user_data))

            access_token = create_access_token({"sub": email})
            response = RedirectResponse(url="/home", status_code=303)
            response.set_cookie(
                key="access_token",
                value=f"Bearer {access_token}",
                httponly=True,
                max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )

            return response
    return templates.TemplateResponse('sign_up_page.html', {'request': request,
                                                            "first_name": first_name,
                                                            "firstname_error": firstname_error,
                                                            "last_name": last_name,
                                                            "lastname_error": lastname_error,
                                                            "email": email,
                                                            "email_error": email_error,
                                                            "password_error": password_error,
                                                            "repeat_password_error": repeat_password_error})

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

    photo_uuid = str(uuid.uuid4())
    extension = photo.filename.split(".")[-1]
    filename = f"{photo_uuid}.{extension}"
    file_data = await photo.read()

    with open(f"uploads/{filename}", "wb") as f:
        f.write(file_data)

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

    ad_id = query_db(insert_query, insert_values, commit=True, get_last_id=True)

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

@app.get("/login")
async def templateHome(request: Request):
    template = env.get_template("login_page.html")
    html_content = template.render(data={})
    return HTMLResponse(content=html_content, status_code=200)


# post method for login page to verify in data base if email and password are same :
@app.post("/login")
def login(request: Request, password: str = Form(""), email: str = Form("")):
    user_params = (email,)
    result = query_db("SELECT IdUser,FirstName,LastName,Password from users WHERE Email=%s", user_params)
    if len(result) == 0:
        login_error = "Incorrect email or password."
        return templates.TemplateResponse("login_page.html", {"request": request, "login_error": login_error})
    else:
        id_user = result[0]["IdUser"]
        first_name = result[0]["FirstName"]
        last_name = result[0]["LastName"]
        hashed = result[0]["Password"]


    if bcrypt.hashpw(password.encode(), hashed.encode()) == hashed.encode():
        access_token = create_access_token({"sub": email})
        response = RedirectResponse(url="/home", status_code=303)
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        return response
    else:
        login_error = "Incorrect email or password!"
        return templates.TemplateResponse("login_page.html", {"request": request, "login_error": login_error})


@app.get("/logout")
async def logout(request: Request, response: Response):
    response = templates.TemplateResponse(
        "home_page.html", {"request": request, "username": None})
    response.delete_cookie(key="access_token")
    return response


@app.post("/delete_ad/{ad_id}")
def deleting_ad(ad_id: int, response: Response, request: Request):
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
            # getting filename of photo :
            photo_filename = result[0].get('photo')
            query_db("DELETE FROM ads where idad = %s", user_params, commit=True)

            # deleting the photo from uploads :
            if photo_filename:
                photo_path = os.path.join("uploads", photo_filename)
                if os.path.exists(photo_path):
                    os.remove(photo_path)

            response = RedirectResponse(url="/products", status_code=303)
        else:
            response = RedirectResponse(url="/forbidden.html", status_code=403)
    return response

# Edit ad :
@app.get("/editablepage/{ad_id}")
def edit_ad(ad_id: int, request: Request):
    user_params = (ad_id,)
    result = query_db("SELECT * from ads where idad = %s", user_params)
    access_token = request.cookies.get("access_token")

    if access_token is not None:
        email = get_email_from_token(access_token)
        username, user_id = get_username_and_id_by_email(email)
        user_params = (ad_id,)
        user_id_from_ad = result[0].get('userID')
        if user_id == user_id_from_ad:
            return templates.TemplateResponse("editablepage.html",
                                              {"request": request, "username": username, "data": result[0]})
        if not result:
            return templates.TemplateResponse("404.html",
                                              {"request": request, "username": username}, status_code=404)
    else:
        return RedirectResponse(url=f"/forbidden.html", status_code=403)


@app.post("/editablepage/{ad_id}")
def editing_ad(
        ad_id: int,
        request: Request,
        title: str = Form(...),
        photo: UploadFile = File(None),
        price: float = Form(...),
        negotiation: bool = Form(False),
        condition: str = Form(...),
        description: str = Form(...),
):
    user_params = (ad_id,)
    result = query_db("SELECT * from ads WHERE idad = %s", user_params)
    print(result)
    access_token = request.cookies.get("access_token")
    if access_token:
        email = get_email_from_token(access_token)
        username, user_id = get_username_and_id_by_email(email)
        if not result:
            return templates.TemplateResponse(
                "404.html", {"request": request, "username": username}, status_code=404
            )
        user_id_from_ad = result[0].get("userID")
        if user_id == user_id_from_ad:
            # Update the ad only if a field has been updated
            title = title.strip()
            price = round(price, 2)
            condition = condition.strip()
            description = description.strip()
            photo_name = result[0]["photo"]
            photo_data = photo.file.read()
            if (
                    title != result[0]["title"]
                    or price != result[0]["price"]
                    or negotiation != result[0]["negotiation"]
                    or condition != result[0]["condition"]
                    or description != result[0]["description"]
                    # or phone != result[0]["phone"]
                    or photo_data
            ):
                # Save the new photo if provided
                if photo_data:
                    photo_path = os.path.join("uploads", photo_name)

                    with open(photo_path, "wb") as f:
                        f.write(photo_data)
                    photo.file.close()
                # Update the ad
                query_db(
                    "UPDATE ads SET title = %s, photo = %s, price = %s, negotiation = %s, `condition` = %s, description = %s WHERE idad = %s",
                    (
                        title,
                        photo_name,
                        price,
                        negotiation,
                        condition,
                        description,
                        ad_id,
                    ), commit=True
                )
            response = RedirectResponse(url=f"/details?id={ad_id}", status_code=303)
        else:
            response = RedirectResponse(url="/forbidden.html", status_code=403)
    else:
        response = RedirectResponse(url="/login", status_code=303)
    return response


@app.get("/myads")  # getting only ads of the same logged in user
async def read_ad(request: Request):
    access_token = request.cookies.get("access_token")
    username = None
    username = None
    if access_token is not None:
        email = get_email_from_token(access_token)
        username, user_id = get_username_and_id_by_email(email)
        result = query_db("SELECT * FROM ads WHERE userID=%s", (user_id,))
    else:
        result = []
    return templates.TemplateResponse("displayingads.html",
                                      {"request": request, "username": username, "data": result})


@app.get("/searchads")
def match_keywords(keywords: str, request: Request):
    query = f"SELECT * FROM ads WHERE title LIKE '%{keywords}%' OR description LIKE '%{keywords}%'"
    results = query_db(query)
    print(f"Results : {results}")

    access_token = request.cookies.get("access_token")
    username = None
    if access_token is not None:
        email = get_email_from_token(access_token)
        username, user_id = get_username_and_id_by_email(email)

    # filtering results :
    matched_ads = [ad for ad in results if
                   keywords.lower() in ad["title"].lower() or keywords.lower() in ad["description"].lower()]
    print(f"Matched ads : {matched_ads}")

    return templates.TemplateResponse("displayingads.html",
                                      {"request": request, "username": username, "data": matched_ads})
