from fastapi import FastAPI, Request
from jinja2 import Template
import mysql.connector
from starlette.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from jinja2 import Environment, FileSystemLoader
import pymysql

app = FastAPI()

connection = pymysql.connect(
    host='localhost',
    user='pratha',
    password='12345',
    database='AdvertisementsDb',
    cursorclass=pymysql.cursors.DictCursor
)

def query_db(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result


# Set the directory containing the templates
template_dir = os.path.join(os.path.dirname(__file__), 'templates')

# Create the template environment
env = Environment(loader=FileSystemLoader(template_dir))

# Load the templates
#top_menu_template = env.get_template('top_menu.html')
#content_template = env.get_template('content.html')
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def read_root():
    return {"Hello":"World"} #dictionary, this will be automatically converted to json
#to run this,type command uvicorn main:app --reload



@app.get("/products") #getting ad table and printing data on website
async def read_ad(request: Request):
    result = query_db("SELECT * from ad")
    print(result)
    template = env.get_template("displayingads.html")
    html_content = template.render(data=result)
    return HTMLResponse(content=html_content, status_code=200)

    #return {"data": myresult}

@app.get("/home")
async def x(request: Request):
    template = env.get_template("home_page.html")
    html_content = template.render(data={})
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/aboutus")
async def templateHome(request: Request):
    template = env.get_template("about_us_page.html")
    html_content = template.render(data={})
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/details")
async def details(request: Request):
    print(request.query_params)
    template = env.get_template("detailsOfAds.html")
    ad_id = request.query_params["id"]
    result = query_db("SELECT * from ad where idad = {}".format(ad_id))
    html_content = template.render(data=result[0])
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/contactus")
async def templateHome(request: Request):
    template = env.get_template("contact_us.html")
    html_content = template.render(data={})
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/login")
async def templateHome(request: Request):
    template = env.get_template("login_page.html")
    html_content = template.render(data={})
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/signup")
async def templateHome(request: Request):
    template = env.get_template("sign_up_page.html")
    html_content = template.render(data={})
    return HTMLResponse(content=html_content, status_code=200)





