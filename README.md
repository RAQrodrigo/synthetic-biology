# synthetic-biology
En proyecto consta de varios archivos .py en src. Paso a dar una breve descripción de cada uno:

## main.py:
    El archivo, por ahora principal, donde toma datos de pubmed con la entrada que le pidas y guarda en una base de datos el id de la publicación junto a su abstract. Por ahora solo tomo los primeros 20 resultados, pero es facilmente cambiable. Para correrlo necesitamos primero configurar el archivo ".env" en el directorio raíz. El mismo te pide una APIKEY de groq y un mail cualquiera, donde el APIKEY es utilizado para hacer consultas a la IA y el mail porque pubmed te pide un mail para poder hacer consultas.

    Lo correriamos solo para actualizar nuestra base de datos, lo dejo como ejemplo una corrida:
        - Primero creamos nuestro entorno virtual:
                            python -m venv venv

        - Lo activamos:
                            .\venv\Scripts\activate         (windows)
                            source venv/bin/activate        (Mac/Linux)

        - Ahora instalamos los requerimientos:
                            pip install -r requirements.txt

        - Por último tenemos que crear un .env para poner los datos que nos pide Groq para el analisis (una APIKEY) y un mail para Pubmed (cualquiera), tiene que tener lo siguiente:
                            EMAIL=tu_correo@ejemplo.com
                            GROQ_API_KEY=tu_api_key_aqui

        - Ahora corremos el programa junto con una Query de la siguiente forma:
                            venv\Scripts\python.exe src/main.py --query "synthetic biology"

## iaProcess.py:
    Aqui encontramos el programa para que la IA haga analisis sobre los datos guardados en nuestra base de datos, primero hace una analisis individual de los abstracts y luego hace un analisis global. Por ahora solo guardamos el analisis global. Si queremos cambiar el tipo de analisis que hace, simplemente cambiamos los prompts. Ahora dejo el comando para correrlo:
                            python .\src\iaProcess.py

## csvtolist.py: 
    El main nos deja, además, un csv con los datos extraidos pero son dificiles de leer así que dejé esto para que lo conviertan en un html y sea más facil de digerir. Lo ejecutamos así:
                            python .\src\csvtolist.py

##  database.py:
        Aquí deje la creación de la base de datos. no hay nada que ejecutar pero se puede ver como es.

## printdb.py: 
        Por último esto lo ejecutas en caso de que quieras testear si se actualizó la base de datos, solamente printea los primeros 10 resultados. Ejecutamos así:
                            python .\src\printdb.py
