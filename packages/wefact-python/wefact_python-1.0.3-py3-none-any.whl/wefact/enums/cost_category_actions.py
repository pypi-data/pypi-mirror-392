from enum import Enum


class CostCategoryAction(str, Enum):
    LIST = "costcategory_list"
    SHOW = "costcategory_show"
    ADD = "costcategory_add"
    EDIT = "costcategory_edit"
    DELETE = "costcategory_delete"
