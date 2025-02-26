from nexios import MakeConfig

nexios_config = MakeConfig({
    "port" : 8000,
    "cors":{
        "allow_origins" : ["*"]
    },
    "debug" : True 
})