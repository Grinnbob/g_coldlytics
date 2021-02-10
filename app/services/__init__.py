from umongo import MotorAsyncIOInstance
from .base_model import CLBaseModel

instance = MotorAsyncIOInstance()

__all__ = [
    "instance",
    "CLBaseModel"
]
