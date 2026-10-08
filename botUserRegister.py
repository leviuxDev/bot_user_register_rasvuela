from bs4 import BeautifulSoup
import requests
import sys
import json

#preparar datos para el formulario nuevo cliente
def payloadCliente():
    nombre = sys.argv[1]
    apellido = sys.argv[2]
    direccion = "Barquisimeto"
    ciudad = "29916"
    correo = 'rasvuela@gmail.com'
    telf ='4220329591'
    cedula = sys.argv[3]


def iniciarSession():
    #se crea la session para mantener las cookies entre peticiones
    session = requests.Session()

    # Encabezado para simular navegación real
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language':'es-ES,es;q=0.9,en;q=0.8',
    }

    session.headers.update(headers)

    url_Base = 'https://export.multitrack.trackingpremium.us'
    loginUrl =f"{url_Base}/login"

    #obtener cookies para logearse
    loginGet = session.get(loginUrl)


def extrerTokenCsrf():
    #extraer token CSRF 
    soupLogin = BeautifulSoup(loginGet.text, 'html.parser')
    csrfInput = soupLogin.find('input',{'name':'_csrf_token'}) or soupLogin.find('input',{'name':'csrf_token'})
    csrfToken = csrfInput['value'] if csrfInput else None

    #payload 
    payload = {
        '_username': 'yohan.abarcas@gmail.com',
        '_password': 'RESvuela2026',  
        'login_date': ''
    }

    if csrfToken :
        payload['_csrf_token'] = csrfToken


def registrarCliente():
    login_post_headers ={
        'Origin' : url_Base,
        'Referer' : loginUrl
    }

    check_login = f"{url_Base}/login_check"
    envirPost = session.post(check_login,data=payload, headers=login_post_headers)

    index_headers = {'Referer':check_login}
    vista_Principal = f"{url_Base}/receipt/index"

    index = session.get(vista_Principal, headers=index_headers)


    # Si la URL final es /receipt/index, ¡la sesión se mantuvo con éxito!
    if "receipt/index" in index.url:
        vista_nuevo_cliente_url = f"{url_Base}/customer/new"
        cliente_headers = {'Referer':vista_Principal}
        res_nuevo_cliete = session.get(vista_nuevo_cliente_url,headers=cliente_headers)

        #extraer token de cliente si lo tiene
        soupCliente = BeautifulSoup(res_nuevo_cliete.text, 'html.parser')
        csrf_input_cliente = soupCliente.find('input', {'name':'customer_type[_token]'})
        csrf_token_cliente = csrf_input_cliente['value'] if csrf_input_cliente else None

        

        payload_cliente = {
            'customer_type[type]' : '1',
            'customer_type[name]':nombre.strip().capitalize(),
            'customer_type[lastname]':apellido.strip(),
            'customer_type[address]' : direccion.strip(),
            'customer_type[cityid]' : ciudad,
            'customer_type[cityname]': 'Barquisimeto (Lara, Venezuela)',
            'customer_type[email]' : correo.strip(),
            'customer_type[mobile]' : telf.strip(),
            'customer_type[docid]' : cedula.strip()
        }
        if csrf_token_cliente:
            payload_cliente['customer_type[_token]'] = csrf_token_cliente

        
        #enviar datos por post 
        endPoint_crear_cliente = f"{url_Base}/customer/create"
        nuevo_cliente_post_headers = {
            'Origin': url_Base,
            'Referer': vista_nuevo_cliente_url
        }
        respuesta_guardar_cliente = session.post(endPoint_crear_cliente,data=payload_cliente, headers=nuevo_cliente_post_headers)
        if respuesta_guardar_cliente.status_code in [200,302]:
            respuesta ={
                'status' : 'success',
                'mensaje' : f"el usuario {nombre} {apellido} fue registrado con exito en la plataforma secundaria"
            }

            
        else:
            respuesta = {
                'status' : 'error',
                'mensaje': f"error de registro {nombre} {apellido} status: {respuesta_guardar_cliente.status_code}"
            }
            

        
        logout_headers ={'Referer' : endPoint_crear_cliente}
        session.get(f"{url_Base}/logout?globalagencyid=2747",headers =logout_headers)
        session.close()
        
    else:
        respuesta = {
            'status': 'error',
            'mensaje': "❌ La sesión sigue redirigiendo al login. Revisa la contraseña o el token."
        }
    print(json.dumps(respuesta))

