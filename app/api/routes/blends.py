# vintrick-backend/app/api/routes/blends.py


from fastapi import APIRouter, HTTPException, Body
from typing import List
import os
import logging
from dotenv import load_dotenv
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
from app.schemas.blend import BlendBase, BlendCreate, BlendOut, BlendUpdate

router = APIRouter()

# Setup logging
logger = logging.getLogger("vintrick.blends")
logging.basicConfig(level=logging.INFO)

# Load SharePoint credentials/config from .env
load_dotenv()
site_url = os.getenv("SHAREPOINT_SITE")
list_name = os.getenv("SHAREPOINT_LIST")
username = os.getenv("SHAREPOINT_USER")
password = os.getenv("SHAREPOINT_PASSWORD")

# Validate environment variables
for var_name, var_val in [
    ("SHAREPOINT_SITE", site_url),
    ("SHAREPOINT_LIST", list_name),
    ("SHAREPOINT_USER", username),
    ("SHAREPOINT_PASSWORD", password),
]:
    if not var_val:
        logger.error(f"Missing environment variable: {var_name}")
        raise RuntimeError(f"Missing environment variable: {var_name}")

ALL_FIELDS = [
    "ID", "Title", "Brand", "Varietal", "Vintage", "WineType",
    # Add other SharePoint fields as needed
]
ENABLED_FIELDS = [f for f in ALL_FIELDS if not f.startswith("#")]

FIELD_TYPE_MAP = {
    "ID": int,
    "Title": str,
    "Brand": str,
    "Varietal": str,
    "Vintage": str,
    "WineType": str,
    # Extend as needed
}

def convert_types(data: dict) -> dict:
    for k, v in data.items():
        if k in FIELD_TYPE_MAP and v is not None:
            try:
                data[k] = FIELD_TYPE_MAP[k](v)
            except Exception:
                data[k] = v
    return data

def get_sp_list():
    try:
        # FIX: with_credentials expects a credential object, not two separate args
        creds = UserCredential(username, password)
        ctx = ClientContext(site_url).with_credentials(creds)
        sp_list = ctx.web.lists.get_by_title(list_name)
        return ctx, sp_list
    except Exception as e:
        logger.error(f"Failed to get SharePoint context: {e}")
        raise HTTPException(status_code=500, detail=f"SharePoint auth error: {str(e)}")

@router.get("/blends/", response_model=List[BlendOut])
def get_blends():
    try:
        ctx, sp_list = get_sp_list()
        items = sp_list.items.top(100).select(ENABLED_FIELDS).get().execute_query()
        results = []
        for item in items:
            props = dict(item.properties)
            blend = {k: props.get(k) for k in ENABLED_FIELDS}
            blend = convert_types(blend)
            results.append(BlendOut(**blend))
        return results
    except Exception as e:
        logger.error(f"Error in get_blends: {e}")
        raise HTTPException(status_code=500, detail=f"SharePoint error: {str(e)}")

@router.get("/blends/{blend_id}", response_model=BlendOut)
def get_blend_by_id(blend_id: int):
    try:
        ctx, sp_list = get_sp_list()
        item = sp_list.items.get_by_id(blend_id).get().execute_query()
        props = dict(item.properties)
        blend = {k: props.get(k) for k in ENABLED_FIELDS}
        blend = convert_types(blend)
        return BlendOut(**blend)
    except Exception as e:
        logger.error(f"Error in get_blend_by_id: {e}")
        raise HTTPException(status_code=404, detail=f"Blend not found: {str(e)}")

@router.post("/blends/", response_model=BlendOut, status_code=201)
def create_blend(data: BlendCreate = Body(...)):
    try:
        ctx, sp_list = get_sp_list()
        data_dict = data.model_dump(exclude_unset=True)
        data_dict = convert_types(data_dict)
        create_data = {k: v for k, v in data_dict.items() if k in ENABLED_FIELDS and k != "ID"}
        item = sp_list.add_item(create_data)
        ctx.execute_query()
        # Some library versions expose "Id" instead of "ID"
        new_id = item.properties.get("ID") or item.properties.get("Id")
        if not new_id:
            # Fallback: refetch last created item props
            item = item.get().execute_query()
            new_id = item.properties.get("ID") or item.properties.get("Id")
        item = sp_list.items.get_by_id(int(new_id)).get().execute_query()
        props = dict(item.properties)
        blend = {k: props.get(k) for k in ENABLED_FIELDS}
        blend = convert_types(blend)
        return BlendOut(**blend)
    except Exception as e:
        logger.error(f"Error in create_blend: {e}")
        raise HTTPException(status_code=500, detail=f"SharePoint error: {str(e)}")

@router.patch("/blends/{blend_id}", response_model=BlendOut)
def update_blend(blend_id: int, data: BlendUpdate = Body(...)):
    try:
        ctx, sp_list = get_sp_list()
        item = sp_list.items.get_by_id(blend_id)
        data_dict = data.model_dump(exclude_unset=True)
        data_dict = convert_types(data_dict)
        updated_fields = {k: v for k, v in data_dict.items() if k in ENABLED_FIELDS and k != "ID"}
        for key, value in updated_fields.items():
            item.set_property(key, value)
        item.update()
        ctx.execute_query()
        item = sp_list.items.get_by_id(blend_id).get().execute_query()
        props = dict(item.properties)
        blend = {k: props.get(k) for k in ENABLED_FIELDS}
        blend = convert_types(blend)
        return BlendOut(**blend)
    except Exception as e:
        logger.error(f"Error in update_blend: {e}")
        raise HTTPException(status_code=500, detail=f"SharePoint error: {str(e)}")

@router.delete("/blends/{blend_id}", response_model=dict)
def delete_blend(blend_id: int):
    try:
        ctx, sp_list = get_sp_list()
        item = sp_list.items.get_by_id(blend_id)
        item.delete_object()
        ctx.execute_query()
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error in delete_blend: {e}")
        raise HTTPException(status_code=404, detail=f"Blend not found or already deleted: {str(e)}")