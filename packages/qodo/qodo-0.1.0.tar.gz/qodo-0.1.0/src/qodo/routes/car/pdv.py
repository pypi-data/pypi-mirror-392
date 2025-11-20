from fastapi import APIRouter, Depends

from qodo.auth.deps import get_current_user
from qodo.controllers.sales.separate_payment_methods import (
    separating_sales_by_payments,
)
from qodo.model.user import Usuario

router = APIRouter()


@router.get('/completedsales')
async def result_sales(current_user: Usuario = Depends(get_current_user)):

    return await separating_sales_by_payments(current_user.empresa_id)
