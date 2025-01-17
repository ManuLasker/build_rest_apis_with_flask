from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from src.models import ItemModel

class Item(Resource):
    """Item Resources, inherit from Resource, this class contains all
    the endpoints for Students
    """
    TABLE_NAME = 'items'
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type = float,
                        required = True,
                        help="This field cannot be left blank!")
    parser.add_argument('store_id',
                        type = int,
                        required = True,
                        help="Every Item needs to have a store id!")
        
    @jwt_required()
    def get(self, name:str):
        item = ItemModel.find_by_name(name)
        status_code = 200 if item else 404 # not found
        if item:
            return {'item':item.json()}, status_code
        else:
            return  {'message': f'Item with name {name!r} not found!'}, status_code
    
    @jwt_required(fresh=True)
    def post(self, name:str):
        if ItemModel.find_by_name(name):
            # already exist
            return {'message': f'Item with name {name!r} already exist!'}, 400 # bad request
        
        # create Item
        data = Item.parser.parse_args()
        item = ItemModel(name=name, price=data['price'],
                         store_id=data['store_id'])
        try:
            item.save_to_db()
        except:
            return {'message': 'An error ocurred inserting the item.'}, 500 # internal server error
        return item.json(), 201 # for creating
    
    @jwt_required()
    def delete(self, name:str):
        claims:dict = get_jwt()
        item = ItemModel.find_by_name(name)
        if not claims.get('is_admin', False):
            return {
                'message': 'Admin privileges are required.'
            }
            
        if not item:
            return {'message': f'Item with name {name!r} does not exist!'}, 400 # bad request
        try:
            item.delete_from_db()
            return {'message': f'Item with name {name!r} deleted!'}
        except:
            return {'message': f'Internal error deleting item'}, 500
    
    @jwt_required()
    def put(self, name: str):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)
        if not item:
            item = ItemModel(name=name, price=data['price'],
                             store_id=data['store_id'])
            item.save_to_db()
            return {'item': item.json()}, 201
        else:
            item._update(data)
            item.save_to_db()
            return {'updated_item': item.json()}


class ItemList(Resource):
    """ItemList Resorce, for items"""
    @jwt_required(optional=True) # jwt is optional
    def get(self):
        user_id = get_jwt_identity() # None or user_id
        items = [item.json() for item in ItemModel.get_all_items()]
        if not user_id: # not jwt identity
            return {'items': [item['name'] for item in items],
                    'message': 'more data available if you log in'}, 200
        return {'items': items}, 200