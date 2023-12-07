from fastapi import APIRouter, Depends
from app.service.auth import valid_session
from app.model.auth import Session

router = APIRouter()


@router.get('/config')
async def get_user_config(ses: Session = Depends(valid_session)):
    return {"message": "{0} Config".format(ses.user.username)}


@router.post('/config')
async def set_user_config(ses: Session = Depends(valid_session)):
    return {"message": "Set User Config"}
