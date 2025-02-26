from nexios import MakeConfig
from tortoise import Tortoise as db

nexios_config = MakeConfig({{
    "port" : 8000,
    "cors":{{
        "allow_origins" : ["*"]
    }},
    "debug" : True 
}})

db_config = {{
    'connections': {{
        'default': "sqlite:///{db_name}"
    }},
    'apps': {{
        'models': {{
            'models': [], #add aerich.models for aerich migrations
            'default_connection': 'default',
        }},
    }},
}}

async def connect_db():
    await db.init(config=db_config)
    await db.generate_schemas()
    print("🗄️ Database connected successfully!" )

async def close_db():
    await db.close_connections()
    print("🗄️ Database connection closed!" )

