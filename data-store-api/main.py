from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import uvicorn  # type: ignore
from typing import Dict
from config import base_config, dispatch_cors

# Routes
from routes.metadata import metadata
from routes.registry import credentials
from routes.registry import items
from routes.register import register
from routes.admin import admin
from routes.check_access import checks


# Setup app
app = FastAPI()


# Get CORS middleware established

# Get the desired origins
origin_info = dispatch_cors(stage=base_config.stage,
                            base_domain=base_config.domain_base)

# If it is an origin list
if isinstance(origin_info, list):
    app.add_middleware(CORSMiddleware,
                       allow_credentials=True,
                       allow_origins=origin_info,
                       allow_methods=["*"],
                       allow_headers=["*"])
# Otherwise it is an origin regex
else:
    app.add_middleware(CORSMiddleware,
                       allow_credentials=True,
                       allow_origin_regex=origin_info,
                       allow_methods=["*"],
                       allow_headers=["*"])

app.include_router(checks.router, prefix="/check-access",
                   tags=["Access check"])
app.include_router(metadata.router, prefix="/metadata", tags=["Metadata"])
app.include_router(register.router, prefix="/register",
                   tags=["Register dataset"])
app.include_router(items.router, prefix="/registry/items",
                   tags=["Registry Items"])

# TODO bring back locks - though will be in registry
# app.include_router(lock.router, prefix="/registry/locks",
#                    tags=["Dataset Lock Actions"])

app.include_router(credentials.router,
                   prefix="/registry/credentials", tags=["Registry credentials"])
app.include_router(admin.router, prefix="/admin", tags=["Administration"])


@app.get("/", operation_id="root")
async def root() -> Dict[str, str]:
    """
    Function Description
    --------------------

    Demonstration unauthenticated endpoint.



    Returns
    -------
    Json
        Basic message response



    See Also (optional)
    --------

    Examples (optional)
    --------

    """
    return {"message": "Health check successful."}


# Add lambda function
handler = Mangum(app)

if __name__ == "__main__":
    uvicorn.run(app, port=8000)