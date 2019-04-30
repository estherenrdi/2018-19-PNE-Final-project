# Main app
# port 8000
import http.server
import socketserver
import http.client
import json, requests
#  import json
PORT = 8000  # The PORT is always this one
socketserver.TCPServer.allow_reuse_address = True

class TestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        path = self.path

        if path == "/":  # The main page will be shown
            f = open('index.html', 'r')
            content = f.read()

        elif self.path.startswith("/listSpecies"):  # listSpecies is select and you send the info
            content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>LISTSPECIES</title>
</head>
<body style="background-color: lightgreen;">
<p>This is the list of the species:<br> </p>
<ul>
{}
</ul>
<a href="/"> Main page </a>
</body>
</html>"""
            # LIST OF ALL THE SPECIES AVAILABLE. This is the client for the list
            server = "http://rest.ensembl.org"
            ext = "/info/species?"

            r = requests.get(server + ext, headers={"Content-Type": "application/json"})

            if not r.ok:
                f = open('error.html', 'r')
                content = f.read()
            general = r.json()

            # Process the message to make a list for the html file
            list_species = """"""
            limit = path.split('=')[1]

            if limit == '':
                rang = int(len(general['species']))
            else:
                rang = int(limit)

            for num, index in enumerate(general['species'][:rang], start=1):
                names = index['name']
                list_species += "<li>{}) Common name  : {}</li>".format(num, names)

            #  Add the result to the html file
            content = content.format(list_species)
        elif self.path.startswith("/karyotype"):
            # Here I get the list of the species

            # I need to prove that the specie requested is in the list
            specie_req = (path.split('=')[1]).lower()

            content = """<!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <title>KARYOTYPE</title>
                        </head>
                        <body style="background-color: lightpink;">
                        <p>Here is show the karyotype of the specie you have selected</p>
                        {}<br>
                        <a href="/"> Main page </a>
                        </body>
                        </html>
                        """
            variable = 'info/assembly/' + specie_req + '?content-type=application/json'
            PORT = 80
            SERVER = 'rest.ensembl.org'
            conn = http.client.HTTPConnection(SERVER, PORT)
            conn.request("GET", variable)
            r1 = conn.getresponse()
            data = r1.read().decode('utf-8')
            general = json.loads(data)
            try:
                karyotype = general['karyotype']
                if karyotype == list():  # there are some specoes that haven't got karyotype info
                    content = content.format("Sorry, the karyotype of the specie you have selected is not in the database. \n Try again! ")
                else:
                    new_list = list()
                    for index in karyotype:
                        if index == 'MT':  # Necessary to delete the MT chromosome
                            continue
                        else:
                            new_list.append(index)
                    content = content.format(new_list)
            except KeyError:
                f = open('error.html', 'r')
                content = f.read()

        elif self.path.startswith("/chromosomeLength"):
            specie = str(path.split('=')[1].split('&')[0])
            chromo = str(path.split('=')[2])
            if specie == '' or chromo == '':  # The user must introduce the 2 values
                f = open('error.html', 'r')
                content = f.read()
            else:
                server = "http://rest.ensembl.org"
                ext = "/info/assembly/" + specie + "/" + chromo + "?"
                r = requests.get(server + ext, headers={"Content-Type": "application/json"})

                if r.ok:
                    decoded = r.json()
                    longitud = decoded['length']
                    content = """<!DOCTYPE html>
                                    <html lang="en">
                                    <head>
                                        <meta charset="UTF-8">
                                        <title>CHROMO/LEN</title>
                                    </head>
                                    <body style="background-color: lightyellow;">
                                    <p>You have selected the specie {} and the chromosome {}</p>
                                    <br>
                                    <p>The length of it is : {}</p>
                                    <a href="/"> Main page </a>
                                    </body>
                                    </html>
                                   """
                    content = content.format(specie,chromo, longitud)
                else:  # If something is wrong, the error page will be shown
                    f = open('error.html', 'r')
                    content = f.read()

        else:  # If something is wrong, the error page will be shown
            f = open('error.html', 'r')
            content = f.read()

        self.send_response(200)

        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(str.encode(content)))
        self.end_headers()

        # --- Sending the body of the response message
        self.wfile.write(str.encode(content))


# --- Now we have to write the main programe
with socketserver.TCPServer(("", PORT), TestHandler) as httpd:

    print("serving at port {}".format(PORT))

    try:

        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
